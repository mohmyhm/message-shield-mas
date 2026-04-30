"""Trace logging utilities."""

from pathlib import Path


def save_trace_jsonl(trace, output_dir: str = "data/traces/raw") -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"{trace.run_id}.jsonl"

    with path.open("w", encoding="utf-8") as file:
        for row in trace.rows:
            file.write(row.model_dump_json() + "\n")

    return path
