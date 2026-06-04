.PHONY: install-dev lint typecheck test test-cov smoke ci clean

PYTHON ?= python3
export PYTHONPATH := src

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m ruff format --check src tests

typecheck:
	$(PYTHON) -m mypy src/aklog

test:
	$(PYTHON) -m pytest tests

test-cov:
	$(PYTHON) -m pytest tests --cov=aklog --cov-report=term-missing --cov-report=html --cov-fail-under=75

smoke:
	$(PYTHON) -m aklog --version
	$(PYTHON) -m aklog -h
	test -x aklog
	bash -n aklog
	$(PYTHON) -c "from aklog.build_meta import __version__; assert __version__"

ci: lint typecheck test-cov smoke

clean:
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
