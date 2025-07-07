FROM python:3.11-slim

WORKDIR /app

# Créer un utilisateur et un groupe non-root pour la sécurité
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Install poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy dependency definition files
COPY pyproject.toml poetry.lock* ./

# Install dependencies directly in the system Python (no virtual env)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --without dev

# Copy application code
COPY . .
RUN chown -R appuser:appgroup /app

# Changer d'utilisateur pour ne pas exécuter en root
USER appuser

EXPOSE 8000

# Set Python path
ENV PYTHONPATH="/app"

# Commande pour démarrer l'application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 