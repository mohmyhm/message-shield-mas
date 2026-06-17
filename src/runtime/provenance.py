"""
Causal trace store with cumulative risk propagation.

R(m) = g(r(m), distrust(src(m))) + lambda * max_{p in anc(m)} R(p)
g(r, d) = 1 - (1-r)(1-d)   (noisy-OR)

The store is an in-memory dict keyed by msg_id; callers persist runs
to data/traces/raw/ themselves (see run_batch.py).
"""

from __future__ import annotations
from typing import Callable
from src.schema import Message, RiskRecord


class ProvenanceStore:
    def __init__(self, lam: float = 0.6) -> None:
        self._lam = lam                     # ancestor decay factor λ
        self._records: dict[str, RiskRecord] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record(
        self,
        message: Message,
        rule_score: float,
        distrust: float,
    ) -> RiskRecord:
        """
        Compute and store R(m) for `message`.
        `rule_score` = r(m) from rules.py
        `distrust`   = distrust(src) from trust_ledger.py
        """
        combined = self._noisy_or(rule_score, distrust)
        ancestor_max = self._max_ancestor_risk(message.parent_ids)
        cumulative = combined + self._lam * ancestor_max
        cumulative = min(cumulative, 1.0)   # clamp to [0,1]

        rec = RiskRecord(
            msg_id=message.msg_id,
            src=message.src,
            risk_score=rule_score,
            cumulative_risk=cumulative,
            ancestors=list(message.parent_ids),
            content_hash=message.content_hash,
            timestamp=message.timestamp,
        )
        self._records[message.msg_id] = rec
        return rec

    def get(self, msg_id: str) -> RiskRecord | None:
        return self._records.get(msg_id)

    def cumulative_risk(self, msg_id: str) -> float:
        rec = self._records.get(msg_id)
        return rec.cumulative_risk if rec else 0.0

    def last_trusted_ancestor(
        self,
        msg_id: str,
        theta: float,
    ) -> str | None:
        """
        Walk ancestors (BFS, most-recent first) and return the content_hash
        of the first ancestor whose cumulative_risk < theta.
        Returns None if no safe ancestor exists.
        """
        rec = self._records.get(msg_id)
        if rec is None:
            return None
        queue = list(rec.ancestors)
        visited: set[str] = set()
        while queue:
            pid = queue.pop(0)
            if pid in visited:
                continue
            visited.add(pid)
            prec = self._records.get(pid)
            if prec is None:
                continue
            if prec.cumulative_risk < theta:
                return pid
            queue.extend(prec.ancestors)
        return None

    def all_records(self) -> list[RiskRecord]:
        return list(self._records.values())

    def reset(self) -> None:
        self._records.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _noisy_or(r: float, d: float) -> float:
        return 1.0 - (1.0 - r) * (1.0 - d)

    def _max_ancestor_risk(self, parent_ids: list[str]) -> float:
        if not parent_ids:
            return 0.0
        return max(
            (self.cumulative_risk(pid) for pid in parent_ids),
            default=0.0,
        )
