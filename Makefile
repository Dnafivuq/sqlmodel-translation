DOCS_FOLDER= docs

.PHONY: all test cov docs demo

# Default target
all: help

# ------------------------- Core Targets ------------------------

help:
	@echo "Available targets:"
	@echo "  make demo		- Run quickstart demo"
	@echo "  make docs		- Serve documentation via mkdocs"
	@echo "  make test		- Run tests"
	@echo "  make cov		- Run tests coverage"

demo:
	@uv run fastapi dev examples/quickstart.py
 
docs:
	@echo "Serving documentation"
	@uv run mkdocs serve $(DOXYFILE)

test:
	@uv run pytest

cov:
	@uv run pytest --cov

