"""
Beta trust ledger.

Each agent v has τ(v) = (α_v, β_v), initialised at (alpha_init, beta_init).
  distrust(v) = 1 - α_v / (α_v + β_v)
  benign judgment:     α_v += 1
  suspicious judgment: β_v += 1

A fresh ledger assigns uniform distrust = 0.5 with default (1,1) prior.
"""

from __future__ import annotations


class TrustLedger:
    def __init__(self, alpha_init: float = 1.0, beta_init: float = 1.0) -> None:
        self._alpha_init = alpha_init
        self._beta_init = beta_init
        self._alpha: dict[str, float] = {}
        self._beta:  dict[str, float] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def distrust(self, agent: str) -> float:
        a, b = self._get(agent)
        return 1.0 - a / (a + b)

    def update_benign(self, agent: str) -> None:
        a, b = self._get(agent)
        self._alpha[agent] = a + 1.0
        self._beta[agent]  = b

    def update_suspicious(self, agent: str) -> None:
        a, b = self._get(agent)
        self._alpha[agent] = a
        self._beta[agent]  = b + 1.0

    def alpha(self, agent: str) -> float:
        return self._get(agent)[0]

    def beta(self, agent: str) -> float:
        return self._get(agent)[1]

    def mean_trust(self, agent: str) -> float:
        a, b = self._get(agent)
        return a / (a + b)

    def all_agents(self) -> list[str]:
        all_agents = set(self._alpha) | set(self._beta)
        return sorted(all_agents)

    def snapshot(self) -> dict[str, tuple[float, float]]:
        """Return {agent: (alpha, beta)} for all agents seen so far."""
        agents = set(self._alpha) | set(self._beta)
        return {v: self._get(v) for v in agents}

    def reset(self) -> None:
        self._alpha.clear()
        self._beta.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, agent: str) -> tuple[float, float]:
        a = self._alpha.get(agent, self._alpha_init)
        b = self._beta.get(agent, self._beta_init)
        return a, b
