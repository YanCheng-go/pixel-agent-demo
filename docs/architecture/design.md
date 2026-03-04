# Architecture Design: Video Transcription CLI Tool

## Tech Stack

| Technology | Version / Variant | Role |
|------------|------------------|------|
| Python | 3.12+ | Application runtime |
| ffmpeg | system package | Frame extraction from video files via subprocess |
| Ollama | latest | Local LLM inference server (HTTP API on port 11434) |
| llama3.2-vision | 11b (Q4 quantization) | Vision model for describing video frames |
| argparse | stdlib | CLI argument parsing |
| base64 | stdlib | Encoding frame images for the Ollama API |
| pathlib / tempfile | stdlib | File and temp directory management |

No third-party Python packages are required. The tool uses only the standard library plus system-level ffmpeg and Ollama.

## Pipeline Design

The tool follows a linear three-stage pipeline:

```
Video File
  --> [1. Extractor] ffmpeg extracts frames every N seconds
        --> temp/frame_000000.jpg, frame_000005.jpg, ...
  --> [2. Analyzer] each frame sent to Ollama vision API
        --> list of (timestamp, description) tuples
  --> [3. Transcript] assembled into markdown with timestamps
        --> output.md
```

Each stage completes fully before the next begins. This sequential design is intentional — see Key Design Decisions below.

## Component Overview

### `src/main.py` — CLI Entry Point

Responsibilities:
- Parse CLI arguments using argparse (per PRD CLI Interface: `--video`, `--interval`, `--model`, `--output`)
- Validate inputs: video file exists, interval is a positive integer, output path is writable
- Orchestrate the three pipeline stages in order
- Print progress to stderr (per PRD MVP scope: "Progress output to stderr showing current frame being processed")
- Exit with code 0 on success, non-zero on failure (per PRD US-1 acceptance criteria)
- Handle top-level errors and print clear messages to stderr (per PRD US-1: "Errors produce clear error messages to stderr")

Argument defaults (per PRD US-2 and US-3):
- `--interval`: 5 seconds
- `--model`: `llama3.2-vision:11b`
- `--output`: `<video-name>-transcript.md` in the current working directory

### `src/extractor.py` — Frame Extraction

Responsibilities:
- Accept a video file path and interval (seconds) as inputs
- Create a temporary directory for extracted frames
- Run ffmpeg via `subprocess.run()` to extract one frame every N seconds
- Return a list of `(timestamp_seconds, frame_file_path)` tuples sorted by timestamp
- Raise clear errors if ffmpeg is not found, the video file is invalid, or extraction fails

ffmpeg command:
```bash
ffmpeg -i <video> -vf "fps=1/<interval>" -q:v 2 <tmpdir>/frame_%06d.jpg
```

Frame naming convention: `frame_000001.jpg`, `frame_000002.jpg`, etc. (ffmpeg 1-indexed). The timestamp for frame N is `(N - 1) * interval` seconds.

Temp directory cleanup: the caller (`main.py`) is responsible for cleanup using a context manager or try/finally.

### `src/analyzer.py` — Vision Analysis

Responsibilities:
- Accept a frame file path and model name as inputs
- Read the image file and base64-encode it
- Send a `POST` request to the Ollama API to generate a description
- Return the text description string
- Raise clear errors if Ollama is unreachable or returns an error

Ollama API call:
```
POST http://localhost:11434/api/generate
Content-Type: application/json

{
  "model": "llama3.2-vision:11b",
  "prompt": "Describe what you see in this screenshot. Focus on the main content, UI elements, text, and any actions being performed.",
  "images": ["<base64-encoded-image>"],
  "stream": false
}
```

The `stream: false` flag ensures we get a single JSON response with the full text in the `response` field, rather than a stream of tokens.

Uses `urllib.request` from the standard library (no `requests` dependency needed).

### `src/transcript.py` — Markdown Assembly

Responsibilities:
- Accept a list of `(timestamp_seconds, description)` tuples, plus metadata (video name, model, interval)
- Format each timestamp as `HH:MM:SS` (per PRD US-1: "Each entry includes the timestamp HH:MM:SS")
- Assemble the full markdown document following the PRD output format (per PRD US-3)
- Write the markdown to the output file path
- Return the output file path on success

Output structure (per PRD Output Format):
```markdown
# Video Transcript: <video-name>

- **Source:** <video-name>
- **Model:** <model-name>
- **Frame interval:** <interval>s
- **Generated:** <ISO-8601 timestamp>

---

## 00:00:00

<description>

## 00:00:05

<description>
```

## Data Flow Detail

```
main.py
  |
  |-- parse args: --video recording.mp4 --interval 5 --model llama3.2-vision:11b
  |
  |-- extractor.extract_frames(video_path, interval)
  |     |
  |     |-- subprocess: ffmpeg -i recording.mp4 -vf "fps=1/5" -q:v 2 /tmp/xxx/frame_%06d.jpg
  |     |
  |     └-- returns: [(0, "/tmp/xxx/frame_000001.jpg"),
  |                    (5, "/tmp/xxx/frame_000002.jpg"),
  |                    (10, "/tmp/xxx/frame_000003.jpg"), ...]
  |
  |-- for each (timestamp, frame_path):
  |     |
  |     |-- analyzer.analyze_frame(frame_path, model)
  |     |     |
  |     |     |-- POST http://localhost:11434/api/generate
  |     |     |   body: { model, prompt, images: [base64(frame)], stream: false }
  |     |     |
  |     |     └-- returns: "The screen shows a terminal window with..."
  |     |
  |     └-- append (timestamp, description) to results
  |         (print progress to stderr)
  |
  |-- transcript.write_transcript(results, metadata, output_path)
  |     |
  |     └-- writes formatted markdown to output.md
  |
  └-- exit 0
```

## Key Design Decisions

### Why Ollama (local inference)

Per PRD: "Runs entirely locally using Ollama (no cloud LLM providers)." The primary use case involves analyzing OT machine control session recordings where data sensitivity matters — no frames or descriptions leave the machine. Ollama provides a simple HTTP API that runs locally with no account or API key required.

### Why llama3.2-vision:11b

The 11B parameter model at Q4 quantization requires approximately 8GB VRAM, fitting comfortably on a GPU with 24GB RAM. It provides good visual understanding for screen recordings while remaining practical to run on a single workstation. The model name is configurable via `--model` so users can swap in alternatives.

### Why ffmpeg (subprocess)

ffmpeg handles virtually every video format without additional Python dependencies. Using `subprocess.run()` keeps the Python dependency footprint at zero third-party packages. ffmpeg is widely available and already a project dependency.

### Why sequential processing

Per PRD: "Sequential frame processing for simplicity and predictable resource usage." Ollama processes one inference request at a time by default, so parallelizing the Python side would only add complexity without improving throughput. Sequential processing also makes progress reporting straightforward — we can print "Processing frame 3/20..." to stderr (per PRD MVP scope).

### Why no third-party Python packages

The standard library provides everything needed: `argparse` for CLI, `subprocess` for ffmpeg, `urllib.request` for HTTP calls to Ollama, `base64` for image encoding, `json` for API payloads, `tempfile` for temp directories, `pathlib` for file paths. This keeps the tool simple to install and run.

## Error Handling Strategy

Per PRD US-1 acceptance criteria, the tool must handle these failure modes with clear stderr messages:

| Error | Detection | Message |
|-------|-----------|---------|
| Video file not found | `pathlib.Path.exists()` check before extraction | `Error: video file not found: <path>` |
| ffmpeg not installed | `subprocess.run()` raises `FileNotFoundError` | `Error: ffmpeg is not installed or not in PATH` |
| ffmpeg extraction fails | Non-zero exit code from subprocess | `Error: ffmpeg failed: <stderr output>` |
| Ollama not running | `urllib.error.URLError` on API call | `Error: cannot connect to Ollama at localhost:11434. Is it running?` |
| Ollama model not found | 404 or error in API response | `Error: model '<name>' not found. Pull it with: ollama pull <name>` |
| Invalid interval | argparse type validation | `Error: --interval must be a positive integer` |
| Output path not writable | Exception on file write | `Error: cannot write to output path: <path>` |

All errors print to stderr and exit with a non-zero code.
