# 🐳 Guide de Déploiement Docker - HackIA2025

## 📋 Vue d'ensemble

Ce guide vous permet de déployer les deux APIs du projet HackIA2025 :
- **ANDFChat Backend** : Système de RAG avec Gemini AI
- **API Extraction Coordonnées** : Extraction de coordonnées géographiques

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│  ANDFChat API   │    │ Coordinates API │
│   Port: 8001    │    │   Port: 8002    │
│                 │    │                 │
│ - RAG System    │    │ - OCR Gemini    │
│ - Gemini AI     │    │ - Coordinates   │
│ - Knowledge Base│    │ - EPSG:4326     │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
            ┌─────────────────┐
            │     Nginx       │
            │   Port: 80      │
            │ (Reverse Proxy) │
            └─────────────────┘
```

## 🚀 Déploiement Local

### 1. Prérequis
```bash
# Docker et Docker Compose installés
docker --version
docker-compose --version

# Clé API Google Gemini
export GOOGLE_API_KEY="your_api_key_here"
```

### 2. Configuration
```bash
# Copier le fichier d'environnement
cp .env.example .env

# Éditer les variables d'environnement
nano .env
```

### 3. Lancement
```bash
# Build et démarrage des services
docker-compose up --build -d

# Vérifier les logs
docker-compose logs -f

# Tester les endpoints
curl http://localhost:8001/health  # ANDFChat
curl http://localhost:8002/health  # API Coordonnées
```

### 4. Accès aux services
- **ANDFChat** : http://localhost:8001
- **API Coordonnées** : http://localhost:8002  
- **Documentation API** : 
  - http://localhost:8001/docs
  - http://localhost:8002/docs

## ☁️ Déploiement sur Render

### 1. Préparation
```bash
# Exécuter le script de déploiement
./deploy.sh
```

### 2. Configuration Render

#### Service 1: ANDFChat Backend
```
Name: andfchat-backend
Environment: Docker
Dockerfile Path: ./ANDFChat/Dockerfile
Build Context: ./ANDFChat
Port: 10000
```

#### Service 2: API Coordonnées
```
Name: ia-coordinates-api
Environment: Docker  
Dockerfile Path: ./IA/Dockerfile
Build Context: ./IA
Port: 10000
```

### 3. Variables d'environnement Render
```
GOOGLE_API_KEY=your_key_here
PORT=10000
ENVIRONMENT=production
PYTHONUNBUFFERED=1
```

### 4. URLs de production
- **ANDFChat** : https://andfchat-backend.onrender.com
- **API Coordonnées** : https://ia-coordinates-api.onrender.com

## 🔧 Commandes Docker Utiles

### Développement
```bash
# Rebuild complet
docker-compose build --no-cache

# Logs en temps réel
docker-compose logs -f [service_name]

# Redémarrer un service
docker-compose restart andfchat-backend

# Shell dans un conteneur
docker-compose exec andfchat-backend bash
```

### Production
```bash
# Lancer avec Nginx
docker-compose --profile production up -d

# Monitoring
docker stats
docker-compose ps

# Cleanup
docker system prune -a
```

## 🏥 Health Checks

Les deux services exposent des endpoints de santé :

```bash
# Vérification automatique
curl -f http://localhost:8001/health
curl -f http://localhost:8002/health

# Réponse attendue
{
  "status": "healthy",
  "timestamp": "2025-09-26T10:00:00.000Z",
  "services": {
    "gemini_api": true,
    "coordinate_conversion": true
  }
}
```

## 📊 Monitoring

### Métriques importantes
- **CPU Usage** : <80% recommandé
- **Memory Usage** : <80% recommandé  
- **Response Time** : <30s pour extraction
- **Error Rate** : <5%

### Logs à surveiller
```bash
# Erreurs critiques
docker-compose logs | grep ERROR

# Performance
docker-compose logs | grep "processing time"

# API Gemini
docker-compose logs | grep "Gemini"
```

## 🚨 Dépannage

### Problèmes courants

#### 1. API Gemini ne répond pas
```bash
# Vérifier la clé API
docker-compose exec andfchat-backend printenv | grep GOOGLE_API_KEY

# Tester manuellement
docker-compose exec andfchat-backend curl -f https://generativelanguage.googleapis.com/v1beta/models
```

#### 2. Extraction de coordonnées échoue
```bash
# Vérifier les dépendances géospatiales
docker-compose exec ia-coordinates-api python -c "import geopandas, pyproj"

# Logs détaillés
docker-compose logs ia-coordinates-api | tail -100
```

#### 3. Build Docker échoue
```bash
# Nettoyage cache
docker builder prune

# Build verbeux
docker-compose build --no-cache --progress=plain
```

### Redémarrage d'urgence
```bash
# Arrêt complet
docker-compose down

# Nettoyage volumes
docker-compose down -v

# Redémarrage propre
docker-compose up --build -d
```

## 📈 Optimisations Production

### 1. Ressources
```yaml
# Dans docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 1G
      cpus: '0.5'
```

### 2. Cache
- Utiliser Redis pour cache des réponses
- Cache des images préprocessées
- Cache des conversions de coordonnées

### 3. Scaling
```bash
# Multiple replicas
docker-compose up --scale andfchat-backend=2

# Load balancing avec Nginx
```

## 🔒 Sécurité

### Variables d'environnement
- ✅ Jamais commiter les clés API
- ✅ Utiliser des secrets Render
- ✅ Rotation régulière des clés

### Réseau
- ✅ Firewall configuré
- ✅ HTTPS en production
- ✅ Rate limiting

---

**🎯 Les deux APIs sont prêtes pour la production !**