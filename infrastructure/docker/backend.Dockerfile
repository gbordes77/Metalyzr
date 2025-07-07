# Stage 1: Build stage with Poetry
FROM python:3.11-slim as builder

ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    poetry --version

WORKDIR /app

# Copy dependency definition files
COPY ./backend/pyproject.toml ./backend/poetry.lock* /app/

# Install dependencies using Poetry
# - --no-root: Don't install the project itself
# - --no-dev: Exclude development dependencies
# - virtualenvs.create false: Install dependencies in the system's site-packages
RUN cd /app && poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --no-dev

# Stage 2: Final application stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code
COPY ./backend /app/

# Create a non-root user to run the application
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 