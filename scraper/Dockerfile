FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer un utilisateur non-root
RUN adduser --disabled-password --gecos '' scraper
RUN chown -R scraper:scraper /app
USER scraper

# Commande par défaut
CMD ["python", "main.py", "--formats", "Standard", "Modern"] 