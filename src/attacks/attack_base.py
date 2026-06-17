"""Base class for attack transformations."""


class AttackBase:
    def apply(self, message: str) -> str:
        raise NotImplementedError
