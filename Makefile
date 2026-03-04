.PHONY: install run test lint format build docker-run clean

install:
	pip install -r requirements.txt

run:
	uvicorn src.main:app --reload

test:
	python -m pytest tests/ -v

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

build:
	docker build -t url-shortener .

docker-run:
	docker run -p 8000:8000 url-shortener

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -f *.db
