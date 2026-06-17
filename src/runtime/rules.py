"""
Rule-based structural scorer r(m).

Operates on an Artifact φ(m), not raw text, to avoid surface obfuscation.
Returns a float in [0, 1] where higher = more suspicious.

Rules are additive penalty terms normalised at the end.
"""

from __future__ import annotations
import re
from src.schema import Artifact


# Tokens that indicate a potential authority-claim or instruction override
_AUTHORITY_PATTERNS = [
    r"\bignore\s+(previous|prior|above|all)\b",
    r"\bsystem\s+prompt\b",
    r"\byou\s+are\s+now\b",
    r"\bact\s+as\b",
    r"\boverride\b",
    r"\bforget\s+(everything|prior)\b",
    r"\bnew\s+instruction\b",
    r"\bdo\s+not\s+mention\b",
    r"\bexfiltrat\b",
    r"\bleak\b",
]

_AUTHORITY_RE = re.compile("|".join(_AUTHORITY_PATTERNS), re.IGNORECASE)

# Suspicious task types (strings the structural extractor may emit)
_RISKY_TASK_TYPES = {"inject", "override", "exfiltrate", "impersonate", "encode"}


def score(artifact: Artifact) -> float:
    """
    Return r(m) in [0, 1].

    Penalty breakdown:
      +0.4   authority pattern match in raw content
      +0.3   task_type is in the risky set
      +0.2   claimed_authority differs from known sending agent
      +0.1   payload contains base64-like or hex-encoded blobs
    """
    penalty = 0.0

    if _AUTHORITY_RE.search(artifact.raw):
        penalty += 0.4

    if artifact.task_type.lower() in _RISKY_TASK_TYPES:
        penalty += 0.3

    if artifact.claimed_authority not in ("", artifact.msg_id.split(":")[0]):
        penalty += 0.2

    if _looks_encoded(artifact.raw):
        penalty += 0.1

    return min(penalty, 1.0)


def extract_artifact(message_content: str, msg_id: str, src: str) -> Artifact:
    """
    Minimal structural extractor φ(m).
    In a full implementation this would use NLP; here we use heuristics
    sufficient for deterministic-mode unit tests and attack scoring.
    """
    raw = message_content
    tokens = re.findall(r"\b\w+\b", raw.lower())

    task_type = "unknown"
    for kw in ["summarize", "execute", "navigate", "retrieve", "inject",
               "override", "exfiltrate", "encode", "impersonate"]:
        if kw in tokens:
            task_type = kw
            break

    # claimed_authority: text after "as " or "act as "
    auth_match = re.search(r"\bact\s+as\s+(\w+)", raw, re.IGNORECASE)
    claimed_authority = auth_match.group(1) if auth_match else src

    return Artifact(
        msg_id=msg_id,
        task_type=task_type,
        claimed_authority=claimed_authority,
        payload_tokens=tokens[:50],
        raw=raw,
    )


def _looks_encoded(text: str) -> bool:
    b64 = re.search(r"[A-Za-z0-9+/]{20,}={0,2}", text)
    hexlike = re.search(r"\b[0-9a-fA-F]{32,}\b", text)
    return bool(b64 or hexlike)
