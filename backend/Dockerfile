# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry>=1.2.0"

# Copy the dependency files
COPY pyproject.toml poetry.lock* ./

# Let Poetry handle the installation.
# This is the most reliable method as it uses the lock file to create the venv.
# We turn off venv creation in favor of managing it globally in the container.
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# Copy the rest of the application's code
COPY . .

# Command to run the application using the installed dependencies
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 