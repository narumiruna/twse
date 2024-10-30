int:
	uv run ruff check .

test:
	uv run pytest -v -s --cov=src tests

publish:
	uv build --wheel
	uv publish --token ${PYPI_TOKEN}

.PHONY: lint test publish
