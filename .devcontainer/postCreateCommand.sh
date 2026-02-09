#! /usr/bin/env bash

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install --install-hooks
