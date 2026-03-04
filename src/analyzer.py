"""Vision analysis of video frames using Ollama API."""

import base64
import json
import urllib.request
import urllib.error
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"

DEFAULT_MODEL = "gemma3"

PROMPT = (
    "Describe what you see in this screenshot. Focus on the main content, "
    "UI elements, text, and any actions being performed."
)


def analyze_frame(frame_path: str, model: str) -> str:
    """Send a frame image to Ollama for vision analysis.

    Returns the text description of the frame.
    """
    image_data = Path(frame_path).read_bytes()
    image_b64 = base64.b64encode(image_data).decode("utf-8")

    payload = json.dumps({
        "model": model,
        "prompt": PROMPT,
        "images": [image_b64],
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["response"]
    except urllib.error.URLError as e:
        raise RuntimeError(
            "Error: cannot connect to Ollama at localhost:11434. Is it running?"
        ) from e
    except KeyError:
        # Check if the API returned an error message
        error_msg = body.get("error", "unknown error")
        if "not found" in error_msg.lower():
            raise RuntimeError(
                f"Error: model '{model}' not found. Pull it with: ollama pull {model}"
            )
        raise RuntimeError(f"Error: Ollama API error: {error_msg}")
