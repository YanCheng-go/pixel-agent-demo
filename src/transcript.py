"""Markdown transcript assembly from analyzed frames."""

from datetime import datetime
from pathlib import Path


def format_timestamp(seconds: int) -> str:
    """Format seconds as HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def write_transcript(
    results: list[tuple[int, str]],
    output_path: str,
    video_name: str,
    model: str,
    interval: int,
) -> str:
    """Write a markdown transcript from (timestamp, description) tuples.

    Returns the output file path on success.
    """
    lines = [
        f"# Video Transcript: {video_name}",
        "",
        f"- **Source:** {video_name}",
        f"- **Model:** {model}",
        f"- **Frame interval:** {interval}s",
        f"- **Generated:** {datetime.now().isoformat()}",
        "",
        "---",
    ]

    for timestamp, description in results:
        lines.append("")
        lines.append(f"## {format_timestamp(timestamp)}")
        lines.append("")
        lines.append(description)

    out = Path(output_path)
    try:
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as e:
        raise RuntimeError(f"Error: cannot write to output path: {output_path}") from e

    return str(out)
