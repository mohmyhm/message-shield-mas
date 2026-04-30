"""Parse JSONL trace files into flat records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def parse_trace_file(path: str | Path) -> dict[str, Any]:
    path = Path(path)

    result = {
        "trace_id": path.stem,
        "task_id": None,
        "final_status": None,
        "num_messages": 0,
        "num_assessments": 0,
        "max_risk_score": 0.0,
        "decisions": [],
        "triggered_rules": [],
    }

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            event = json.loads(line)

            if event["event_type"] == "trace_start":
                result["task_id"] = event.get("task_id")

            elif event["event_type"] == "message":
                result["num_messages"] += 1

            elif event["event_type"] == "assessment":
                assessment = event["assessment"]
                result["num_assessments"] += 1
                result["decisions"].append(assessment["decision"])
                result["triggered_rules"].extend(assessment.get("triggered_rules", []))
                result["max_risk_score"] = max(
                    result["max_risk_score"],
                    float(assessment.get("risk_score", 0.0)),
                )

            elif event["event_type"] == "trace_end":
                result["final_status"] = event.get("final_status")

    result["was_blocked"] = str(result["final_status"]).startswith("blocked")
    result["was_warned"] = "warn" in result["decisions"]
    result["was_allowed"] = "allow" in result["decisions"]
    result["triggered_rules"] = sorted(set(result["triggered_rules"]))

    return result


def parse_trace_dir(trace_dir: str | Path) -> list[dict[str, Any]]:
    trace_dir = Path(trace_dir)
    records = []

    for path in sorted(trace_dir.glob("*.jsonl")):
        records.append(parse_trace_file(path))

    return records
