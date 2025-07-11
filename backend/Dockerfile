# Stage 1: Build dependencies
FROM python:3.11-slim as builder

# Install poetry
RUN pip install poetry

# Copy dependency files
WORKDIR /app
COPY backend/pyproject.toml backend/poetry.lock* ./

# Install dependencies, including dev for playwright install command
RUN poetry install --no-root

# Install Playwright browsers
RUN poetry run playwright install --with-deps
# We use --with-deps to let it handle system dependencies

# Now, create the final image from the python-base
FROM python:3.11-slim as final

# Set working directory
WORKDIR /app

# Copy installed dependencies and browsers from the builder stage
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy application code
COPY ./backend /app

# Expose port and command
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 