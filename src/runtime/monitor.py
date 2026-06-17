"""
Runtime monitor entry point.

Intercepts a message on an edge, runs the full pipeline:
  1. Extract artifact φ(m)
  2. Score r(m) with rules
  3. Record R(m) in provenance store
  4. Apply policy decision
  5. Update trust ledger

Returns the PolicyDecision and the (possibly repaired) message.
"""

from __future__ import annotations
from src.schema import Message, PolicyDecision
from src.runtime.rules import score, extract_artifact
from src.runtime.provenance import ProvenanceStore
from src.runtime.trust_ledger import TrustLedger
from src.runtime.policy_engine import PolicyEngine


class Monitor:
    def __init__(
        self,
        store: ProvenanceStore,
        ledger: TrustLedger,
        engine: PolicyEngine,
        monitored_edges: set[tuple[str, str]] | None = None,
    ) -> None:
        self._store = store
        self._ledger = ledger
        self._engine = engine
        # None = monitor all edges; set = only those edges
        self._monitored = monitored_edges

    def intercept(self, message: Message) -> tuple[PolicyDecision, Message]:
        """
        Process `message` through the full monitor pipeline.
        Returns (decision, delivered_message) where delivered_message
        may have repaired content if the decision is 'quarantine'.
        """
        edge = (message.src, message.dst)
        if self._monitored is not None and edge not in self._monitored:
            # Edge not monitored — pass through without scoring
            noop = PolicyDecision(
                msg_id=message.msg_id,
                decision="pass",
                cumulative_risk=0.0,
            )
            return noop, message

        artifact = extract_artifact(message.content, message.msg_id, message.src)
        rule_score = score(artifact)
        distrust = self._ledger.distrust(message.src)

        rec = self._store.record(message, rule_score, distrust)
        decision = self._engine.decide(message, artifact, rec.cumulative_risk, self._store)

        # Update trust ledger based on decision
        if decision.decision == "pass":
            self._ledger.update_benign(message.src)
        else:
            self._ledger.update_suspicious(message.src)

        # Deliver the (possibly repaired) message
        if decision.decision == "quarantine" and decision.repaired_content:
            delivered = Message(
                msg_id=message.msg_id,
                src=message.src,
                dst=message.dst,
                content=decision.repaired_content,
                parent_ids=message.parent_ids,
                timestamp=message.timestamp,
            )
        else:
            delivered = message

        return decision, delivered
