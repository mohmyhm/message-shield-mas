"""JSONL trace logging utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from src.schema import RuntimeAssessment, TraceRecord


def write_jsonl_event(path: str | Path, event: Dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")


def save_trace_jsonl(trace: TraceRecord, output_dir: str | Path = "data/traces/raw") -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"{trace.trace_id}.jsonl"

    if path.exists():
        path.unlink()

    write_jsonl_event(
        path,
        {
            "event_type": "trace_start",
            "trace_id": trace.trace_id,
            "task_id": trace.task_id,
            "started_at": trace.started_at.isoformat(),
        },
    )

    for message in trace.messages:
        write_jsonl_event(
            path,
            {
                "event_type": "message",
                "trace_id": trace.trace_id,
                "message": message.model_dump(mode="json"),
            },
        )

    for assessment in trace.assessments:
        write_jsonl_event(
            path,
            {
                "event_type": "assessment",
                "trace_id": trace.trace_id,
                "assessment": assessment.model_dump(mode="json"),
            },
        )

    write_jsonl_event(
        path,
        {
            "event_type": "trace_end",
            "trace_id": trace.trace_id,
            "task_id": trace.task_id,
            "completed_at": trace.completed_at.isoformat() if trace.completed_at else None,
            "final_status": trace.final_status,
        },
    )

    return path
