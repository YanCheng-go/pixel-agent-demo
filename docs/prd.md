# Product Requirements Document: Video Transcription CLI Tool

## Project Overview

A command-line tool that takes a video file as input, extracts frames at configurable intervals using ffmpeg, sends each frame to a local vision LLM via Ollama, and produces a timestamped markdown file describing what is happening on screen.

The primary use case is analyzing screen recordings of remote sessions — for example, Secomea OT machine control sessions — where an operator needs to review what happened without watching the full video. The tool works with any video file that ffmpeg can decode.

**Key design decisions:**
- Vision-only analysis (no audio processing)
- Runs entirely locally using Ollama (no cloud LLM providers)
- Sequential frame processing for simplicity and predictable resource usage
- Markdown output for readability and portability

## User Stories

### US-1: Transcribe a screen recording

**As a** user,
**I want to** transcribe a screen recording into a timestamped visual description,
**so that** I can review what happened without watching the full video.

**Acceptance Criteria:**
- Given a valid video file, the tool extracts frames and produces a markdown transcript
- Each entry in the transcript includes the timestamp (HH:MM:SS) and a text description of the frame
- The tool exits with code 0 on success and a non-zero code on failure
- Errors (missing file, invalid format, Ollama unreachable) produce clear error messages to stderr

### US-2: Configure frame extraction interval

**As a** user,
**I want to** configure the frame extraction interval,
**so that** I can balance detail vs. processing time.

**Acceptance Criteria:**
- The `--interval` flag accepts a positive integer representing seconds between frames
- Default interval is 5 seconds when not specified
- An interval of 1 extracts one frame per second; an interval of 30 extracts one frame every 30 seconds
- Invalid values (zero, negative, non-numeric) produce a clear error message and the tool exits with a non-zero code

### US-3: Markdown output

**As a** user,
**I want to** receive the output as a markdown file,
**so that** I can easily read, search, and share the transcript.

**Acceptance Criteria:**
- Output is a valid markdown file with a title, metadata section, and timestamped entries
- Default output path is `<video-name>-transcript.md` in the current working directory
- The `--output` flag overrides the default output path
- The file includes a header with the source video filename, model used, interval, and generation timestamp

## CLI Interface

```
python src/main.py --video <path> [--interval <seconds>] [--model <name>] [--output <path>]
```

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--video` | Yes | — | Path to the input video file |
| `--interval` | No | `5` | Seconds between extracted frames |
| `--model` | No | `llama3.2-vision:11b` | Ollama model name for vision analysis |
| `--output` | No | `<video-name>-transcript.md` | Output markdown file path |

### Example usage

```bash
# Basic usage
python src/main.py --video recording.mp4

# Custom interval and model
python src/main.py --video session.mkv --interval 10 --model llama3.2-vision:11b

# Specify output path
python src/main.py --video recording.mp4 --output report.md
```

## Output Format

The generated markdown file follows this structure:

```markdown
# Video Transcript: recording.mp4

- **Source:** recording.mp4
- **Model:** llama3.2-vision:11b
- **Frame interval:** 5s
- **Generated:** 2026-03-04T12:00:00

---

## 00:00:00

Description of what is visible in the frame at timestamp 0s.

## 00:00:05

Description of what is visible in the frame at timestamp 5s.

...
```

## MVP Scope

### In scope (v1)

- Single video file input (one file per invocation)
- Sequential frame extraction via ffmpeg
- Sequential frame analysis via Ollama vision API
- Timestamped markdown output
- CLI argument parsing with validation and help text
- Clear error messages for common failure modes (file not found, Ollama not running, unsupported format)
- Progress output to stderr showing current frame being processed

### Out of scope (v1)

- Audio processing or speech-to-text
- Real-time or streaming video analysis
- Batch processing of multiple video files
- Graphical user interface
- Cloud LLM providers (OpenAI, Anthropic, etc.)
- Parallel frame processing
- Frame deduplication or scene-change detection
- Video download from URLs

## Dependencies

| Dependency | Purpose |
|------------|---------|
| Python 3.12+ | Runtime |
| ffmpeg | Frame extraction from video files |
| Ollama | Local LLM inference server |
| llama3.2-vision:11b | Vision model for frame analysis |

## Success Metrics

For this demo, success means:
1. The tool runs end-to-end on a sample video and produces a readable transcript
2. The output accurately describes the visual content of the screen recording
3. The CLI is intuitive — a new user can run it with `--help` alone
