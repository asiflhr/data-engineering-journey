# Makefile for automating common tasks

.PHONY: setup clean lint

setup:
	@echo "Setting up virtual environment and installing dependencies..."
	python3 -m venv venv
	@. venv/bin/activate; pip install -r requirements.txt
	@echo "Setup complete. Activate with 'source venv/bin/activate'"

clean:
	@echo "Cleaning up Python cache files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	@echo "Running linter and formatter..."
	flake8 .
	black .