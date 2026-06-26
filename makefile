# Auto-detect Python 3.12+
PYTHON := $(shell \
	python3.12 -c "import sys; print('python3.12')" 2>/dev/null || \
	python3 -c "import sys; assert sys.version_info >= (3,12,0); print('python3')" 2>/dev/null || \
	python -c "import sys; assert sys.version_info >= (3,12,0); print('python')" 2>/dev/null || \
	echo "none" \
)

VENV := .venv
VENV_BIN := $(VENV)/bin

.PHONY: check
check:
	@if [ "$(PYTHON)" = "none" ]; then \
		echo "ERROR: Python 3.12+ required"; \
		echo "Current: $$(python3 --version 2>/dev/null || echo 'not found')"; \
		exit 1; \
	fi
	@echo "OK: $$($(PYTHON) --version)"

.PHONY: venv
venv: check
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@echo "OK: Virtual environment created at $(VENV)"

.PHONY: install
install: venv
	$(VENV_BIN)/pip install -r requirements.txt
	@echo "OK: Dependencies installed"

.PHONY: run
run: install
	@echo "Starting application..."
	@$(VENV_BIN)/python app/main.py


.PHONY: start
start: install
	@echo "Starting application..."
	@$(VENV_BIN)/python app/main.py

.PHONY: clean
clean:
	@rm -rf $(VENV)
	@rm -rf __pycache__ */__pycache__ .pytest_cache
	@echo "OK: Cleaned"

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make check      - Check Python 3.12+ version"
	@echo "  make venv       - Create virtual environment"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run application (app/main.py)"
	@echo "  make start      - Install dependencies and run application"
	@echo "  make clean      - Remove virtual environment and caches"
	@echo "  make help       - Show this help"


.DEFAULT_GOAL := help