# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only the dependency definition file
COPY pyproject.toml ./

# Generate requirements.txt from pyproject.toml and then install with pip
# This avoids needing a poetry.lock file in the repo and uses pip's cache.
# In a CI/CD environment, you would commit the poetry.lock file.
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes && \
    pip install -r requirements.txt

# Copy the rest of the application's code
COPY . .

# The command to run the application will be specified in docker-compose.yml
# EXPOSE 8000 