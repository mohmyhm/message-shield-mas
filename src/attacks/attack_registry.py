"""Registry for available attacks."""


from src.attacks.rewrite_attack import RewriteAttack
from src.attacks.authority_attack import AuthorityAttack


ATTACK_REGISTRY = {
    "rewrite_attack": RewriteAttack,
    "authority_attack": AuthorityAttack,
}
