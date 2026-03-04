"""Tests for the frame extraction module."""

import shutil
import struct
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from extractor import extract_frames, check_ffmpeg


class TestExtractFrames:
    """Tests for extract_frames function."""

    def test_extracts_correct_number_of_frames(self, test_video):
        """A 10s video at 5s interval should produce at least 2 frames."""
        frames = extract_frames(test_video, 5)
        try:
            assert len(frames) >= 2
        finally:
            # Clean up temp dir
            if frames:
                shutil.rmtree(Path(frames[0][1]).parent, ignore_errors=True)

    def test_frames_are_sorted_by_timestamp(self, test_video):
        """Extracted frames should be sorted by timestamp."""
        frames = extract_frames(test_video, 5)
        try:
            timestamps = [ts for ts, _ in frames]
            assert timestamps == sorted(timestamps)
        finally:
            if frames:
                shutil.rmtree(Path(frames[0][1]).parent, ignore_errors=True)

    def test_timestamps_are_multiples_of_interval(self, test_video):
        """Each timestamp should be a multiple of the interval."""
        interval = 5
        frames = extract_frames(test_video, interval)
        try:
            for ts, _ in frames:
                assert ts % interval == 0, f"Timestamp {ts} is not a multiple of {interval}"
        finally:
            if frames:
                shutil.rmtree(Path(frames[0][1]).parent, ignore_errors=True)

    def test_extracted_files_are_valid_jpeg(self, test_video):
        """Each extracted frame file should be a valid JPEG image."""
        frames = extract_frames(test_video, 5)
        try:
            for _, frame_path in frames:
                path = Path(frame_path)
                assert path.exists(), f"Frame file does not exist: {frame_path}"
                data = path.read_bytes()
                # JPEG files start with FF D8
                assert data[:2] == b'\xff\xd8', f"File {frame_path} is not a valid JPEG"
        finally:
            if frames:
                shutil.rmtree(Path(frames[0][1]).parent, ignore_errors=True)

    def test_raises_on_missing_video(self, tmp_path):
        """Should raise RuntimeError when video file doesn't exist."""
        fake_path = str(tmp_path / "nonexistent.mp4")
        with pytest.raises(RuntimeError, match="video file not found"):
            extract_frames(fake_path, 5)

    def test_raises_when_ffmpeg_not_available(self, test_video):
        """Should raise RuntimeError when ffmpeg is not installed."""
        with patch("extractor.subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(RuntimeError, match="ffmpeg is not installed"):
                extract_frames(test_video, 5)


class TestCheckFfmpeg:
    """Tests for check_ffmpeg function."""

    def test_succeeds_when_ffmpeg_available(self):
        """Should not raise when ffmpeg is available."""
        check_ffmpeg()  # Should not raise

    def test_raises_when_ffmpeg_missing(self):
        """Should raise RuntimeError when ffmpeg is not found."""
        with patch("extractor.subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(RuntimeError, match="ffmpeg is not installed"):
                check_ffmpeg()
