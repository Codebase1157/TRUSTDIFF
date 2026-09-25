.PHONY: install test run figures all clean

install:
	pip install -e ".[dev]"

test:
	pytest -q

run:
	python -m trustdiff run --scene both

figures:
	python -m trustdiff capture
	python -m trustdiff figures --which schematics
	python -m trustdiff figures --which all

all: run figures

clean:
	rm -rf results figures .pytest_cache
	find . -name __pycache__ -type d -exec rm -rf {} +
