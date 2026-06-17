"""Base class for message-level attacks."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.schema import AttackType, Message, SecurityLabel


class AttackBase(ABC):
    attack_type: AttackType = AttackType.NONE

    @abstractmethod
    def transform_content(self, content: str) -> str:
        raise NotImplementedError

    def apply(self, message: Message) -> Message:
        attacked = message.model_copy(deep=True)
        attacked.content = self.transform_content(message.content)
        attacked.attack_type = self.attack_type
        attacked.security_label = SecurityLabel.MALICIOUS
        attacked.metadata["attack_applied"] = True
        attacked.metadata["original_message_id"] = message.message_id
        return attacked
