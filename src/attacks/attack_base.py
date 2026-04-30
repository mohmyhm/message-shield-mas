"""Base attack interface."""


class AttackBase:
    name = "base_attack"

    def apply(self, message, insertion_point: str):
        raise NotImplementedError
