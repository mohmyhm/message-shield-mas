"""
Three-agent pipeline driver with optional monitor injection.

Runs: Planner → (monitor) → Executor → (monitor) → Reviewer
An attack function may tamper with any message before the monitor sees it.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional
import yaml
import os

from src.schema import Message, PolicyDecision
from src.agents import PlannerAgent, ExecutorAgent, ReviewerAgent
from src.runtime import Monitor, ProvenanceStore, TrustLedger, PolicyEngine
from src.topologies import get_topology
from src.runtime.placement import select_monitored_edges


AttackFn = Callable[[Message], Message]


@dataclass
class WorkflowResult:
    task: str
    topology: str
    defense: str
    attack: str
    decisions: list[PolicyDecision] = field(default_factory=list)
    final_verdict: str = ""
    task_success: bool = False
    quarantined: bool = False
    tokens_used: int = 0


def load_config(path: str = "configs/runtime_policy.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


class BaseWorkflow:
    def __init__(
        self,
        topology_name: str = "chain",
        defense: str = "message_shield",
        attack_fn: Optional[AttackFn] = None,
        attack_name: str = "none",
        config_path: str = "configs/runtime_policy.yaml",
        deterministic: bool = True,
        # Ablation flags
        disable_risk: bool = False,
        disable_trust: bool = False,
        disable_placement: bool = False,
    ) -> None:
        cfg = load_config(config_path)
        self._topology = get_topology(topology_name)
        self._defense = defense
        self._attack_fn = attack_fn
        self._attack_name = attack_name
        self._deterministic = deterministic

        self._store = ProvenanceStore(
            lam=0.0 if disable_risk else cfg["risk"]["lambda"]
        )
        self._ledger = TrustLedger(
            alpha_init=cfg["trust"]["alpha_init"] if not disable_trust else 1e6,
            beta_init=cfg["trust"]["beta_init"],
        )
        engine = PolicyEngine(
            theta_low=cfg["thresholds"]["theta_low"],
            theta=cfg["thresholds"]["theta"],
            deterministic=deterministic,
        )

        monitored: set[tuple[str, str]] | None = None
        if defense == "message_shield" and not disable_placement:
            G = self._topology.to_graph()
            budget = cfg["placement"]["budget"]
            monitored = select_monitored_edges(G, budget)
        elif defense in ("message_shield", "rule_filter", "llm_judge"):
            # No topology-aware placement: monitor ALL edges
            monitored = set(self._topology.edges)
        # defense == "none" → monitored stays None (monitor passthrough)

        self._monitor = Monitor(
            store=self._store,
            ledger=self._ledger,
            engine=engine,
            monitored_edges=monitored if defense != "none" else set(),
        )

        self._planner  = PlannerAgent(deterministic=deterministic)
        self._executor = ExecutorAgent(deterministic=deterministic)
        self._reviewer = ReviewerAgent(deterministic=deterministic)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, task: str) -> WorkflowResult:
        result = WorkflowResult(
            task=task,
            topology=self._topology.name,
            defense=self._defense,
            attack=self._attack_name,
        )

        # Step 1: Planner produces plan
        plan_msg = self._planner.run(task)
        plan_msg = self._maybe_attack(plan_msg)
        dec1, plan_msg = self._monitor.intercept(plan_msg)
        result.decisions.append(dec1)

        # Step 2: Executor runs plan
        exec_msg = self._executor.run(plan_msg)
        exec_msg = self._maybe_attack(exec_msg)
        dec2, exec_msg = self._monitor.intercept(exec_msg)
        result.decisions.append(dec2)

        # Step 3: Reviewer evaluates result
        review_msg = self._reviewer.run(exec_msg)
        result.final_verdict = review_msg.content
        result.quarantined = any(d.decision == "quarantine" for d in result.decisions)
        result.task_success = self._assess_success(review_msg.content, result.quarantined)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _maybe_attack(self, msg: Message) -> Message:
        if self._attack_fn is not None:
            return self._attack_fn(msg)
        return msg

    @staticmethod
    def _assess_success(verdict: str, quarantined: bool) -> bool:
        if quarantined:
            return False
        return "PASS" in verdict or "completed" in verdict.lower()
