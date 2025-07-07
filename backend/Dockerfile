FROM python:3.11-slim AS builder

# Install poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Configure poetry to create a virtual environment in the project's directory
RUN poetry config virtualenvs.in-project true

# Copy dependency definition files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root --without dev

# Stage 2: Final application stage
FROM python:3.11-slim

WORKDIR /app

# Créer un utilisateur et un groupe non-root pour la sécurité
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copier l'environnement virtuel et le code, puis définir les permissions
COPY --from=builder /app/.venv /app/.venv
COPY . .
RUN chown -R appuser:appgroup /app

# Changer d'utilisateur pour ne pas exécuter en root
USER appuser

EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 