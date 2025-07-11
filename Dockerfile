# Stage 1: Builder - To install dependencies
FROM --platform=linux/amd64 python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install "poetry>=1.2.0"

# Copy dependency files from the backend directory
COPY backend/pyproject.toml backend/poetry.lock* ./

# Install dependencies using Poetry
# --no-dev: Exclude development dependencies
# --no-root: Don't install the project itself, only dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

# Stage 2: Final image - To run the application
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code from the backend directory
COPY ./backend /app/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 