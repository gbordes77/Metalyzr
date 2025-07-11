# Stage 1: Build environment with all dependencies
FROM python:3.11-slim as builder
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency definition files
COPY backend/pyproject.toml backend/poetry.lock ./

# Install all dependencies (including dev dependencies like playwright)
# This is necessary to run the playwright install command
RUN poetry install --no-root

# Download and install browsers needed by Playwright
RUN poetry run playwright install --with-deps


# Stage 2: Final production image
FROM python:3.11-slim as final
WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the playwright browser cache from the builder stage
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy the application code
COPY ./backend /app

# Expose port and define the command to run the application
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 