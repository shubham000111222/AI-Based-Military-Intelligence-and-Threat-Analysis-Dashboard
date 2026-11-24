# ==============================================================================
# AI-Based Military Intelligence & Threat Analysis Dashboard
# Professional Engineering Makefile
# ==============================================================================

.PHONY: help setup data train evaluate test lint run docker clean

help:
	@echo "Available commands:"
	@echo "  make setup     - Install Python dependencies from requirements.txt"
	@echo "  make data      - Prepare and clean the GTD dataset into parquet"
	@echo "  make train     - Train attack prediction models & compute SHAP explanations"
	@echo "  make evaluate  - Run out-of-time forecast and early-warning backtest evaluations"
	@echo "  make test      - Run complete unit test suite with coverage report"
	@echo "  make lint      - Check and format code with Ruff"
	@echo "  make run       - Launch the multipage Streamlit dashboard"
	@echo "  make docker    - Build the production Docker container image"
	@echo "  make clean     - Clean temporary caches and build artifacts"

setup:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

data:
	python scripts/prepare_data.py
	python scripts/build_embeddings.py

train:
	python scripts/train_attack_model.py

evaluate:
	python scripts/evaluate_forecasts.py
	python scripts/evaluate_anomaly.py

test:
	python -m pytest -v --cov=src --cov-report=term-missing tests/

lint:
	python -m ruff check .
	python -m ruff format --check .

run:
	streamlit run app.py

docker:
	docker build -t threat-intelligence-dashboard:latest .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
