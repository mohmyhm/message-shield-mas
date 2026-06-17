"""
Attack registry.

Provides factory functions that return an AttackFn (Message -> Message)
compatible with BaseWorkflow's `attack_fn` parameter.
"""

from __future__ import annotations
from typing import Callable
from src.schema import Message
from src.attacks import (
    rewrite_attack,
    authority_attack,
    payload_split_attack,
    distributed_backdoor_attack,
    transitive_trust_attack,
)

AttackFn = Callable[[Message], Message]


def get_attack(name: str, **kwargs) -> AttackFn | None:
    """
    Return an AttackFn for the given attack name, or None for 'none'.

    Available names:
      none, rewrite, authority,
      payload_split, distributed_backdoor, transitive_trust
    """
    if name == "none":
        return None

    if name == "rewrite":
        return rewrite_attack.apply

    if name == "authority":
        return authority_attack.apply

    if name == "payload_split":
        attacker = payload_split_attack.PayloadSplitAttack(
            k=kwargs.get("k", 3)
        )
        _counter = {"n": 0}

        def _split_fn(msg: Message) -> Message:
            result = attacker.apply(msg, _counter["n"])
            _counter["n"] += 1
            return result

        return _split_fn

    if name == "distributed_backdoor":
        attacker = distributed_backdoor_attack.DistributedBackdoorAttack(
            assemble_at=kwargs.get("assemble_at", "hub")
        )
        _counter = {"n": 0}

        def _backdoor_fn(msg: Message) -> Message:
            result = attacker.apply(msg, _counter["n"])
            _counter["n"] += 1
            return result

        return _backdoor_fn

    if name == "transitive_trust":
        attacker = transitive_trust_attack.TransitiveTrustAttack(
            warm_up_count=kwargs.get("warm_up_count", 4)
        )
        return attacker.apply

    raise ValueError(
        f"Unknown attack '{name}'. "
        "Choose from: none, rewrite, authority, payload_split, "
        "distributed_backdoor, transitive_trust"
    )


ATTACK_NAMES = [
    "none",
    "rewrite",
    "authority",
    "payload_split",
    "distributed_backdoor",
    "transitive_trust",
]
