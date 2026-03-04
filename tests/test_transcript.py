"""Tests for the markdown transcript assembly module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from transcript import format_timestamp, write_transcript


class TestFormatTimestamp:
    """Tests for format_timestamp function."""

    def test_zero_seconds(self):
        assert format_timestamp(0) == "00:00:00"

    def test_seconds_only(self):
        assert format_timestamp(45) == "00:00:45"

    def test_minutes_and_seconds(self):
        assert format_timestamp(125) == "00:02:05"

    def test_one_hour(self):
        assert format_timestamp(3600) == "01:00:00"

    def test_over_one_hour(self):
        """Timestamps for videos over 1 hour should include HH."""
        assert format_timestamp(7261) == "02:01:01"

    def test_large_timestamp(self):
        assert format_timestamp(36000) == "10:00:00"


class TestWriteTranscript:
    """Tests for write_transcript function."""

    def test_creates_output_file(self, tmp_output_dir, sample_transcript_data):
        """Output file should be created at the specified path."""
        output_path = str(tmp_output_dir / "transcript.md")
        write_transcript(sample_transcript_data, output_path, "test.mp4", "llama3.2-vision:11b", 5)
        assert Path(output_path).exists()

    def test_markdown_header(self, tmp_output_dir, sample_transcript_data):
        """Output should contain a top-level heading with the video name."""
        output_path = str(tmp_output_dir / "transcript.md")
        write_transcript(sample_transcript_data, output_path, "test.mp4", "llama3.2-vision:11b", 5)
        content = Path(output_path).read_text()
        assert "# Video Transcript: test.mp4" in content

    def test_metadata_fields(self, tmp_output_dir, sample_transcript_data):
        """Output should include source, model, and interval metadata."""
        output_path = str(tmp_output_dir / "transcript.md")
        write_transcript(sample_transcript_data, output_path, "test.mp4", "llama3.2-vision:11b", 5)
        content = Path(output_path).read_text()
        assert "**Source:** test.mp4" in content
        assert "**Model:** llama3.2-vision:11b" in content
        assert "**Frame interval:** 5s" in content

    def test_timestamps_in_output(self, tmp_output_dir, sample_transcript_data):
        """Each entry should have a timestamp heading in HH:MM:SS format."""
        output_path = str(tmp_output_dir / "transcript.md")
        write_transcript(sample_transcript_data, output_path, "test.mp4", "llama3.2-vision:11b", 5)
        content = Path(output_path).read_text()
        assert "## 00:00:00" in content
        assert "## 00:00:05" in content
        assert "## 00:00:10" in content

    def test_descriptions_in_output(self, tmp_output_dir, sample_transcript_data):
        """Each entry's description should appear in the output."""
        output_path = str(tmp_output_dir / "transcript.md")
        write_transcript(sample_transcript_data, output_path, "test.mp4", "llama3.2-vision:11b", 5)
        content = Path(output_path).read_text()
        for _, desc in sample_transcript_data:
            assert desc in content

    def test_long_video_timestamps(self, tmp_output_dir, long_video_transcript_data):
        """Videos over 1 hour should show HH:MM:SS timestamps."""
        output_path = str(tmp_output_dir / "transcript.md")
        write_transcript(long_video_transcript_data, output_path, "long.mp4", "model", 5)
        content = Path(output_path).read_text()
        assert "## 00:00:00" in content
        assert "## 01:00:00" in content
        assert "## 02:01:01" in content

    def test_empty_input_produces_valid_markdown(self, tmp_output_dir):
        """Empty input should produce a markdown file with just the header."""
        output_path = str(tmp_output_dir / "empty.md")
        write_transcript([], output_path, "empty.mp4", "model", 5)
        content = Path(output_path).read_text()
        assert "# Video Transcript: empty.mp4" in content
        assert "---" in content
        # Should not have any ## timestamp headings
        assert "## " not in content

    def test_returns_output_path(self, tmp_output_dir, sample_transcript_data):
        """write_transcript should return the output file path."""
        output_path = str(tmp_output_dir / "transcript.md")
        result = write_transcript(sample_transcript_data, output_path, "test.mp4", "model", 5)
        assert result == output_path
