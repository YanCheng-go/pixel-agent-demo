# Video Transcription CLI Tool
#
# This container expects access to an Ollama instance. Either:
#   - Use --network host so the container can reach localhost:11434
#   - Or set OLLAMA_HOST=http://host.docker.internal:11434 on macOS/Windows

FROM python:3.12-slim AS base

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

USER appuser

ENTRYPOINT ["python", "src/main.py"]
