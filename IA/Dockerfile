# Dockerfile pour API Extraction Coordonnées
FROM python:3.12-slim

# Informations du conteneur  
LABEL maintainer="HackIA2025 Team"
LABEL description="API FastAPI pour extraction de coordonnées géographiques avec Gemini AI"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_CACHE_DIR=/tmp/uv-cache

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Installer UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copier les fichiers de configuration UV
COPY --chown=app:app pyproject.toml uv.lock ./

# Installer les dépendances avec UV
RUN uv sync --frozen --no-install-project --no-dev

# Copier le code source
COPY --chown=app:app . .

# Installer le projet
RUN uv sync --frozen --no-dev

# Créer les dossiers nécessaires
RUN mkdir -p logs temp

# Exposer le port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Script de démarrage
COPY --chown=app:app <<'EOF' /home/app/start.sh
#!/bin/bash
set -e

echo "🚀 Démarrage API Extraction Coordonnées..."

# Vérifier les variables d'environnement
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ GOOGLE_API_KEY manquante"
    exit 1
fi

# Vérifier que les services sont disponibles
echo "🔍 Vérification des dépendances..."
uv run python -c "import fastapi, cv2, geopandas, pyproj; print('✅ Toutes les dépendances OK')"

# Démarrer l'API
echo "🌐 Lancement du serveur FastAPI sur 0.0.0.0:8000"
exec uv run python -m uvicorn main_final:app --host 0.0.0.0 --port 8000 --workers 1
EOF

RUN chmod +x /home/app/start.sh

# Commande par défaut
CMD ["uv", "run", "python", "start_api_server.py"]