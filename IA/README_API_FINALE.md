# API d'Extraction de Coordonnées - Version Finale

## 🎯 Description

API FastAPI complète pour l'extraction de coordonnées géographiques à partir d'images (PDF, JPG, PNG) avec :
- ✅ Extraction automatique via Gemini AI
- ✅ Conversion vers EPSG:4326 (WGS84)
- ✅ Superposition avec couches géographiques  
- ✅ Format de sortie compatible avec `submissions_reordered.csv`

## 🚀 Démarrage Rapide

### 1. Installation des dépendances
```bash
uv sync
```

### 2. Configuration
Créer un fichier `.env` :
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Lancement de l'API
```bash
python start_api.py
```

L'API sera disponible sur : `http://localhost:8000`

## 📊 Endpoints

### 🔍 GET `/`
Informations générales sur l'API

### 🏥 GET `/health` 
Vérification de l'état de l'API et des services

### 📤 POST `/extract`
Extraction de coordonnées d'un fichier unique

**Paramètres:**
- `file`: Fichier image (JPG, PNG, TIFF, PDF*)

**Réponse JSON:**
```json
{
  "filename": "leve1.jpg",
  "timestamp": "2025-09-26T10:30:45.123456",
  "extraction_success": true,
  "coordinates": "[{\"x\": 427484.52, \"y\": 704121.76}]",
  "coordinates_wgs84": [
    {
      "latitude": 6.36123456,
      "longitude": 2.41234567,
      "utm_zone_detected": 31
    }
  ],
  "aif": "NON",
  "air_proteges": "NON",
  "parcelles": "OUI",
  // ... toutes les 13 couches
  "metadata": {
    "coordinate_count": 4,
    "coordinate_system_utm": "EPSG:32631",
    "coordinate_system_wgs84": "EPSG:4326"
  }
}
```

### 📤 POST `/batch_extract`
Extraction par lot (max 10 fichiers)

**Paramètres:**
- `files`: Liste de fichiers images

## 🗺️ Couches Géographiques Supportées

L'API vérifie l'appartenance aux couches suivantes :
- `aif` - Aires d'Importance Floristique
- `air_proteges` - Aires Protégées
- `dpl` - Domaine Public Lacustre
- `dpm` - Domaine Public Maritime
- `enregistrement_individuel` - Enregistrement Individuel
- `litige` - Zones de Litige
- `parcelles` - Parcelles
- `restriction` - Zones de Restriction
- `tf_demembres` - Titres Fonciers Démembrés
- `tf_en_cours` - Titres Fonciers en Cours
- `tf_etat` - Titres Fonciers de l'État
- `titre_reconstitue` - Titres Reconstitués
- `zone_inondable` - Zones Inondables

## 🔄 Conversion de Coordonnées

L'API convertit automatiquement :
- **Entrée**: Coordonnées UTM (détection automatique zone)
- **Sortie**: EPSG:4326 (WGS84) - Latitude/Longitude

### Zones UTM Supportées
- Zone 31N (Bénin/Afrique de l'Ouest) : EPSG:32631
- Auto-détection basée sur les coordonnées X

## 🧪 Tests

### Test complet de l'API
```bash
python test_api_complete.py
```

### Test manuel avec curl
```bash
# Health check
curl http://localhost:8000/health

# Upload d'une image
curl -X POST "http://localhost:8000/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@votre_image.jpg"
```

## 📁 Structure des Fichiers

```
IA/
├── main_final.py              # API FastAPI principale
├── start_api.py               # Script de lancement
├── test_api_complete.py       # Tests automatisés
├── example_response_complete.json  # Exemple de réponse
├── submissions_reordered.csv  # Données de référence
└── README_API_FINALE.md       # Cette documentation
```

## ⚡ Pipeline de Traitement

1. **Upload du fichier** (image/PDF)
2. **Préprocessing** (amélioration contraste, débruitage)
3. **Extraction Gemini** (coordonnées UTM)
4. **Conversion EPSG:4326** (latitude/longitude)
5. **Superposition spatiale** (couches géographiques)
6. **Formatage JSON** (compatible CSV)

## 🔧 Configuration Avancée

### Variables d'environnement
```bash
GOOGLE_API_KEY=your_key        # Obligatoire
```

### Dépendances principales
- FastAPI + Uvicorn (API web)
- Google Generative AI (extraction)
- OpenCV (preprocessing images)
- PyProj (conversion coordonnées)
- GeoPandas + Shapely (superposition spatiale)

## 🚨 Limitations

- **PDF** : Support en développement
- **Lot** : Maximum 10 fichiers par requête
- **Timeout** : 60s pour extraction simple, 120s pour batch
- **Formats** : PNG, JPG, JPEG, TIFF, PDF*

## 📈 Performance

- Extraction simple : ~10-30s selon taille image
- Batch (3 fichiers) : ~45-90s
- Préprocessing : ~2-5s par image
- Conversion coordonnées : <1s

## 🆘 Dépannage

### API ne démarre pas
```bash
# Vérifier les dépendances
python -c "import fastapi, google.generativeai, pyproj, geopandas"

# Vérifier la clé API
echo $GOOGLE_API_KEY
```

### Erreur extraction
- Vérifier que l'image contient des coordonnées numériques
- Vérifier que les coordonnées sont au format UTM
- Tester avec `test_api_complete.py`

### Superposition spatiale désactivée
```bash
# Installer GeoPandas
pip install geopandas shapely

# Ou avec uv
uv add geopandas shapely
```

## 🎊 Exemple d'Utilisation

```python
import requests

# Upload d'une image
with open('leve1.jpg', 'rb') as f:
    files = {'file': ('leve1.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/extract', files=files)
    
result = response.json()
print(f"Coordonnées détectées: {result['metadata']['coordinate_count']}")
print(f"Première coord WGS84: {result['coordinates_wgs84'][0]}")
```

---
**🔥 API prête pour la production - HackIA2025 🔥**