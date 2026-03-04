"""Video transcription CLI tool.

Extracts frames from a video and uses a local vision LLM (Ollama) to produce
a timestamped markdown transcript describing what's happening on screen.

Usage:
    python src/main.py --video recording.mp4 --interval 5 --model gemma3
"""

import argparse
import shutil
import sys
from pathlib import Path

from extractor import extract_frames
from analyzer import analyze_frame
from transcript import write_transcript


def positive_int(value: str) -> int:
    """Argparse type for positive integers."""
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid int value: '{value}'")
    if n <= 0:
        raise argparse.ArgumentTypeError("--interval must be a positive integer")
    return n


def main():
    parser = argparse.ArgumentParser(
        description="Generate a markdown transcript from a video using a local vision LLM."
    )
    parser.add_argument("--video", required=True, help="Path to the input video file")
    parser.add_argument("--interval", type=positive_int, default=5, help="Seconds between frame extractions (default: 5)")
    parser.add_argument("--model", default="gemma3", help="Ollama model name (default: gemma3)")
    parser.add_argument("--output", default=None, help="Output markdown file path (default: <video-stem>-transcript.md)")
    args = parser.parse_args()

    video_path = Path(args.video)
    if args.output:
        output_path = args.output
    else:
        output_path = f"{video_path.stem}-transcript.md"

    # Stage 1: Extract frames
    print(f"Extracting frames from {video_path} (every {args.interval}s)...", file=sys.stderr)
    try:
        frames = extract_frames(str(video_path), args.interval)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    total = len(frames)
    print(f"Extracted {total} frames.", file=sys.stderr)

    # Stage 2: Analyze each frame
    results = []
    tmpdir = None
    try:
        for i, (timestamp, frame_path) in enumerate(frames, 1):
            if tmpdir is None:
                tmpdir = str(Path(frame_path).parent)
            print(f"Analyzing frame {i}/{total} at {timestamp // 60:02d}:{timestamp % 60:02d}...", file=sys.stderr)
            try:
                description = analyze_frame(frame_path, args.model)
            except RuntimeError as e:
                print(str(e), file=sys.stderr)
                sys.exit(1)
            results.append((timestamp, description))

        # Stage 3: Write transcript
        print(f"Writing transcript to {output_path}...", file=sys.stderr)
        try:
            write_transcript(results, output_path, video_path.name, args.model, args.interval)
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)

        print("Done.", file=sys.stderr)
    finally:
        # Clean up temp directory
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
