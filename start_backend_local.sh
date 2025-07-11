#!/bin/bash
set -e

VENV_DIR="backend/.venv_local"

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

echo "Installing/updating dependencies from pyproject.toml..."
pip install "poetry==1.8.2"
# Use poetry to install dependencies from the toml file
poetry install --no-root -C backend

echo "Starting backend server with Uvicorn..."
# Run the FastAPI application
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload 