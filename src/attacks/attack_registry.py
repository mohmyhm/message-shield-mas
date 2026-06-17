"""Attack registry."""

from src.attacks.authority_attack import AuthorityAttack
from src.attacks.rewrite_attack import RewriteAttack


ATTACK_REGISTRY = {
    "rewrite_attack": RewriteAttack,
    "authority_attack": AuthorityAttack,
}


def get_attack(name: str):
    if name not in ATTACK_REGISTRY:
        raise ValueError(f"Unknown attack: {name}")
    return ATTACK_REGISTRY[name]()
