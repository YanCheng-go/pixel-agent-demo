.PHONY: install run test build docker-run clean

VIDEO   ?= recording.mp4
INTERVAL ?= 5
MODEL   ?= gemma3

install:
	uv pip install -r requirements.txt

run:
	python src/main.py --video $(VIDEO) --interval $(INTERVAL) --model $(MODEL)

test:
	python -m pytest tests/ -v

build:
	docker build -t video-transcriber .

docker-run:
	docker run --rm --network host video-transcriber --video $(VIDEO) --interval $(INTERVAL) --model $(MODEL)

clean:
	rm -rf __pycache__ src/__pycache__ .pytest_cache tests/__pycache__
	rm -rf output/
	find . -type d -name 'vidtranscript_*' -exec rm -rf {} + 2>/dev/null || true
