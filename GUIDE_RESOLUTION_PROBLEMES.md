# 🔧 Guide de Résolution des Problèmes - HackIA2025

Ce guide vous aide à diagnostiquer et résoudre les problèmes courants des deux APIs.

## 🗺️ Problème 1: Superposition des Couches Géographiques

### 🔍 Symptômes
- L'API retourne toujours "NON" pour toutes les couches d'appartenance
- Logs montrent "Aucune couche géographique chargée"
- Fonctionne sur Linux mais pas sur Windows

### 🎯 Cause Racine
Le chemin vers les fichiers GeoJSON est hardcodé et ne fonctionne pas sur tous les systèmes.

### ✅ Solution Appliquée

**Modifications dans `IA/main_final.py`:**

1. **Auto-détection des chemins** - La classe `SpatialOverlay` détecte automatiquement le bon chemin
2. **Compatibilité Windows/Linux** - Utilise `Path().resolve()` pour normaliser les chemins
3. **Logs détaillés** - Debug complet du chargement des couches
4. **Fallbacks multiples** - Teste plusieurs emplacements possibles

### 🧪 Test de la correction
```bash
cd IA/
uv run python test_single_image.py "./Data_Hackathon_IA_2025/Testing_Data/leve3.jpg"
```

### 📊 Logs de diagnostic
```
INFO:main_final:SpatialOverlay initialisé avec répertoire: /path/to/Data_Hackathon_IA_2025/couche
INFO:main_final:Répertoire trouvé: /path/to/Data_Hackathon_IA_2025/couche (existe: True)
INFO:main_final:Fichiers GeoJSON détectés: ['aif.geojson', 'parcelles.geojson', ...]
```

### 🔧 Vérifications pour déploiement
```bash
# 1. Vérifier que le dossier de données existe
ls Data_Hackathon_IA_2025/couche/*.geojson

# 2. Vérifier les permissions
ls -la Data_Hackathon_IA_2025/couche/

# 3. Test manuel
curl -X POST "http://localhost:8000/extract" -F "file=@test_image.jpg" | jq .
```

## 🤖 Problème 2: ANDFChat - ChromaDB Manquant

### 🔍 Symptômes
```
ERROR: No module named 'chromadb'
❌ Tests échoués: Import RAG
```

### ✅ Solution Appliquée

**Modifications dans `IA/ANDFChat/pyproject.toml`:**
```toml
dependencies = [
    # ... dépendances existantes
    "chromadb>=0.4.0",
    "sentence-transformers>=2.2.0",
    "numpy>=1.24.0", 
    "pandas>=2.0.0",
]
```

### 🔄 Installation
```bash
cd IA/ANDFChat/
uv sync
```

## 🌐 Problème 3: ANDFChat - Endpoints 404

### 🔍 Symptômes
```
HTTP/1.1 404 Not Found" for /chat, /procedures, /search
```

### 🎯 Cause
Le fichier `enhanced_backend.py` ne contenait pas tous les endpoints nécessaires.

### ✅ Solution Appliquée

**Ajout des endpoints manquants dans `enhanced_backend.py`:**

1. **`/procedures`** - Liste des procédures ANDF
2. **`/search`** - Recherche dans la base de connaissances

### 🧪 Test des corrections
```bash
cd IA/ANDFChat/
uv run python run_enhanced_backend.py

# Dans un autre terminal
curl http://localhost:8000/procedures
curl "http://localhost:8000/search?q=titre%20foncier&limit=3"
```

## 🐳 Corrections Docker

### Mise à jour du Dockerfile ANDFChat
```dockerfile
# Le Dockerfile pointe maintenant vers le bon dossier
COPY --chown=app:app . .
WORKDIR /home/app/IA/ANDFChat  # Chemin corrigé

# Variables d'environnement mises à jour
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
```

### Mise à jour du docker-compose.yml
```yaml
# Chemins corrigés pour les volumes
andfchat-backend:
  build: 
    context: ./IA/ANDFChat  # Chemin corrigé
    dockerfile: Dockerfile
  volumes:
    - ./IA/ANDFChat/data:/home/app/data
```

## 🔄 Scripts de Diagnostic

### Script de diagnostic complet
```bash
#!/bin/bash
echo "🔍 Diagnostic HackIA2025"

# Test API IA
echo "📍 Test API Extraction Coordonnées:"
cd IA/
if uv run python -c "import main_final; print('✅ Import OK')"; then
    echo "✅ API IA - Imports OK"
else
    echo "❌ API IA - Problème d'imports"
fi

# Test ANDFChat
echo "🤖 Test ANDFChat:"
cd ../IA/ANDFChat/
if uv run python -c "import chromadb, enhanced_backend; print('✅ Import OK')"; then
    echo "✅ ANDFChat - Imports OK"
else
    echo "❌ ANDFChat - Problème d'imports"
fi

# Test données géospatiales
echo "🗺️ Test Données Géospatiales:"
if find . -name "*.geojson" | head -1; then
    echo "✅ Fichiers GeoJSON trouvés"
else
    echo "❌ Aucun fichier GeoJSON trouvé"
fi
```

## 🚀 Déploiement sur Render

### Variables d'environnement critiques
```bash
# Pour les deux services
GOOGLE_API_KEY=your_key_here
PORT=10000
ENVIRONMENT=production
```

### Vérifications pré-déploiement
1. **Dépendances** - Toutes installées via UV
2. **Chemins** - Compatible Linux (Render utilise Linux)
3. **Variables d'env** - Configurées dans Render Dashboard
4. **Données géospatiales** - Incluses dans le build Docker

### Commandes de vérification Render
```bash
# Après déploiement, tester les endpoints
curl https://ia-coordinates-api.onrender.com/health
curl https://andfchat-backend.onrender.com/health
curl https://andfchat-backend.onrender.com/procedures
```

## 📋 Checklist de Déploiement

### Avant déploiement
- [ ] Tests locaux passent (Docker + API)
- [ ] Dépendances à jour (uv sync)
- [ ] Variables d'environnement configurées
- [ ] Données géospatiales présentes
- [ ] Dockerfiles testés

### Après déploiement  
- [ ] Health checks passent
- [ ] Tous les endpoints répondent
- [ ] Extraction de coordonnées fonctionne
- [ ] Superposition géographique active
- [ ] RAG system opérationnel

## 🔍 Logs de Debug

### API Extraction Coordonnées
```bash
# Logs détaillés pour diagnostic
uv run python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from main_final import SpatialOverlay
overlay = SpatialOverlay()
"
```

### ANDFChat
```bash
# Test complet du système
cd IA/ANDFChat/
uv run python test_enhanced_system.py
```

## 🛠️ Maintenance Continue

### Mise à jour des dépendances
```bash
# Mise à jour sécurisée
uv lock --upgrade
uv sync

# Test après mise à jour
python -m pytest tests/ -v
```

### Monitoring en production
- **Métriques** - Response time, error rate, memory usage
- **Alertes** - 404 errors, API timeouts, missing dependencies
- **Logs** - Structured logging pour debugging

---

**🎯 Avec ces corrections, les deux APIs sont maintenant robustes et prêtes pour la production !**