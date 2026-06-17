"""Base agent interface."""


class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    def run(self, message: str) -> str:
        raise NotImplementedError
