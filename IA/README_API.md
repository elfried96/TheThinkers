# 🚀 API Finale - Extraction Coordonnées

**Pipeline complète d'extraction de coordonnées géographiques avec FastAPI**

## ✨ Fonctionnalités

### 🔧 Pipeline intégrée
- **Extraction Gemini AI** : Analyse d'images avec IA
- **Préprocessing** : Amélioration automatique des images
- **Conversion coordonnées** : UTM → WGS84 (EPSG:4326)
- **Superposition spatiale** : Détection des couches géographiques
- **Format JSON** : Sortie structurée compatible hackathon

### 📋 Formats supportés
- **Images** : PNG, JPG, JPEG, TIFF
- **PDF** : En cours de développement

## 🚀 Démarrage rapide

### 1. Installation des dépendances
```bash
cd IA/
uv sync
```

### 2. Configuration
```bash
# Créer fichier .env avec votre clé Gemini
echo "GOOGLE_API_KEY=votre_clé_api_ici" > .env
```

### 3. Lancement de l'API
```bash
uv run python main_final.py
```

L'API sera accessible sur : http://localhost:8000

### 4. Test de l'API
```bash
# Test simple
uv run python test_api_final.py leve9.png

# Test par lot
uv run python test_api_final.py leve9.png leve24.png leve30.png
```

## 📡 Endpoints API

### `GET /`
Informations générales de l'API

### `GET /health`
Vérification du statut des services

### `POST /extract`
**Extraction individuelle d'un fichier**

**Paramètres :**
- `file` : Fichier image à traiter (multipart/form-data)

**Réponse JSON :**
```json
{
  "filename": "leve9.png",
  "timestamp": "2025-01-24T15:30:00",
  "extraction_success": true,
  "coordinate_count": 4,
  
  "coordinates_utm": [
    {"x": 448005.15, "y": 703480.27},
    {"x": 448034.38, "y": 703480.24}
  ],
  
  "coordinates_wgs84": [
    {"latitude": 6.353842, "longitude": 2.417156},
    {"latitude": 6.353839, "longitude": 2.417445}
  ],
  
  "spatial_overlays": {
    "aif": "NON",
    "parcelles": "OUI",
    "litige": "NON"
  },
  
  "metadata": {
    "coordinate_system_utm": "EPSG:32631",
    "coordinate_system_wgs84": "EPSG:4326",
    "extraction_method": "gemini-1.5-flash"
  }
}
```

### `POST /batch_extract`
**Extraction par lot (max 10 fichiers)**

**Paramètres :**
- `files` : Tableau de fichiers images

## 🧪 Exemples d'utilisation

### cURL
```bash
# Test santé
curl http://localhost:8000/health

# Upload fichier
curl -X POST \
  -F "file=@leve9.png" \
  http://localhost:8000/extract
```

### Python requests
```python
import requests

# Extraction simple
with open('leve9.png', 'rb') as f:
    files = {'file': ('leve9.png', f, 'image/png')}
    response = requests.post('http://localhost:8000/extract', files=files)
    
result = response.json()
print(f"Coordonnées trouvées: {result['coordinate_count']}")
```

### JavaScript (fetch)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/extract', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🔧 Configuration avancée

### Variables d'environnement
```bash
# Obligatoire
GOOGLE_API_KEY=votre_clé_gemini

# Optionnel
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### Personnalisation
- **Zone UTM** : Modifier `utm_zone=31` dans `CoordinateConverter`
- **Couches géographiques** : Ajuster `layer_names` dans `SpatialOverlay`
- **Timeout API** : Modifier `timeout=30` dans les requêtes Gemini

## 🐛 Dépannage

### Erreurs courantes

**❌ "GOOGLE_API_KEY non trouvée"**
```bash
# Vérifier fichier .env
cat .env
# Doit contenir: GOOGLE_API_KEY=votre_clé
```

**❌ "PyProj non disponible"**
```bash
# Installer dépendances géospatiales
uv add pyproj geopandas shapely
```

**❌ "Connexion refusée"**
```bash
# Vérifier que l'API tourne
ps aux | grep python
# Ou relancer
uv run python main_final.py
```

### Logs
```bash
# Voir logs détaillés
tail -f api.log

# Niveau debug
LOG_LEVEL=DEBUG uv run python main_final.py
```

## 📊 Performance

### Benchmarks typiques
- **Extraction simple** : ~3-5 secondes/image
- **Avec preprocessing** : ~5-8 secondes/image  
- **Batch 5 images** : ~15-25 secondes
- **Mémoire** : ~200-500MB selon taille images

### Optimisations
- Cache des couches géospatiales
- Preprocessing conditionnel
- Timeout adaptatifs
- Limitation batch (10 fichiers max)

## 🔗 Intégration

### Docker (optionnel)
```dockerfile
FROM python:3.12-slim
COPY . /app
WORKDIR /app
RUN pip install uv && uv sync
EXPOSE 8000
CMD ["uv", "run", "python", "main_final.py"]
```

### Déploiement
```bash
# Production avec Gunicorn
uv add gunicorn
gunicorn main_final:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

**🎯 API développée pour le Hackathon IA 2025**  
**📍 Extraction automatique de coordonnées cadastrales**