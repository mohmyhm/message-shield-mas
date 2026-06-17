"""Simple provenance helpers for message tracking."""

from src.schema import Message


class ProvenanceTracker:
    def annotate(
        self,
        message: Message,
        source_stage: str,
        was_tampered: bool = False,
    ) -> Message:
        annotated = message.model_copy(deep=True)
        annotated.metadata["source_stage"] = source_stage
        annotated.metadata["was_tampered"] = was_tampered
        return annotated
