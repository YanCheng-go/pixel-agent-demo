"""Shared pytest fixtures for video transcription tests."""

import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def test_video(tmp_path):
    """Create a tiny 10-second test video with color bars using ffmpeg lavfi."""
    video_path = tmp_path / "test_video.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "color=c=blue:s=320x240:d=10",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            str(video_path),
        ],
        capture_output=True,
        check=True,
    )
    return str(video_path)


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Provide a temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_transcript_data():
    """Provide sample transcript data as a list of (timestamp, description) tuples."""
    return [
        (0, "A blue screen is displayed with no other elements."),
        (5, "The blue screen continues with the same solid color."),
        (10, "Still showing a plain blue background."),
    ]


@pytest.fixture
def long_video_transcript_data():
    """Provide transcript data with timestamps exceeding 1 hour."""
    return [
        (0, "Introduction slide."),
        (3600, "One hour mark — new section begins."),
        (7261, "Two hours, one minute, and one second in."),
    ]
