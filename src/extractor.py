"""Frame extraction from video files using ffmpeg."""

import subprocess
import tempfile
from pathlib import Path


def check_ffmpeg():
    """Verify that ffmpeg is installed and accessible."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError("Error: ffmpeg is not installed or not in PATH")


def extract_frames(video_path: str, interval: int) -> list[tuple[int, str]]:
    """Extract one frame every `interval` seconds from a video file.

    Returns a list of (timestamp_seconds, frame_file_path) tuples sorted by timestamp.
    The caller is responsible for cleaning up the temporary directory.
    """
    video = Path(video_path)
    if not video.exists():
        raise RuntimeError(f"Error: video file not found: {video_path}")

    check_ffmpeg()

    tmpdir = tempfile.mkdtemp(prefix="vidtranscript_")
    output_pattern = str(Path(tmpdir) / "frame_%06d.jpg")

    result = subprocess.run(
        [
            "ffmpeg",
            "-i", str(video),
            "-vf", f"fps=1/{interval}",
            "-q:v", "2",
            output_pattern,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Error: ffmpeg failed: {result.stderr}")

    # Collect extracted frames (ffmpeg uses 1-based indexing)
    frames = []
    for frame_file in sorted(Path(tmpdir).glob("frame_*.jpg")):
        # Extract the frame number from the filename
        frame_num = int(frame_file.stem.split("_")[1])
        timestamp = (frame_num - 1) * interval
        frames.append((timestamp, str(frame_file)))

    return frames
