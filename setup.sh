#!/usr/bin/env bash
# One-time setup for a fresh copy of this template.
# Usage:  bash setup.sh

set -e

echo "==> Creating virtual environment (.venv)"
python3 -m venv .venv

echo "==> Activating venv and installing requirements"
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Registering Jupyter kernel for this project"
PROJECT_NAME="$(basename "$PWD")"
python -m ipykernel install --user --name="$PROJECT_NAME" --display-name="Python ($PROJECT_NAME)"

echo ""
echo "Done. To get started:"
echo "  source .venv/bin/activate"
echo "  streamlit run dashboard.py     # dashboard"
echo "  jupyter notebook                # exploration"
