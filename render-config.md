# Configuration Render pour ANDFChat et IA API

## 🚀 Services à Créer sur Render

### 1. Service ANDFChat Backend

**Type:** Web Service  
**Repository:** Votre repo GitHub  
**Branch:** main  
**Root Directory:** `IA/ANDFChat`  
**Build Command:** (laisser vide - Docker gère tout)  
**Start Command:** (laisser vide - Docker gère tout)  

**Variables d'environnement ANDFChat:**
```
GOOGLE_API_KEY=your_gemini_api_key_here
ENVIRONMENT=production
PORT=8000
```

### 2. Service IA Coordinate API

**Type:** Web Service  
**Repository:** Votre repo GitHub  
**Branch:** main  
**Root Directory:** `IA`  
**Build Command:** (laisser vide - Docker gère tout)  
**Start Command:** (laisser vide - Docker gère tout)  

**Variables d'environnement IA API:**
```
GOOGLE_API_KEY=your_gemini_api_key_here
ENVIRONMENT=production
PORT=8001
```

## 📋 Étapes de Déploiement

### Étape 1: Préparer le Repository
1. Commitez tous les fichiers
2. Pushez sur GitHub
3. Vérifiez que les Dockerfiles sont présents

### Étape 2: Créer les Services Render
1. Connectez-vous à Render
2. Cliquez "New +"
3. Sélectionnez "Web Service"
4. Connectez votre repo GitHub
5. Configurez selon les specs ci-dessus

### Étape 3: URLs de Production
Une fois déployé, vous aurez :
- ANDFChat: `https://votre-andf-service.onrender.com`
- IA API: `https://votre-ia-service.onrender.com`

## 🔧 Monitoring et Debug

### Health Checks
- ANDFChat: `GET /health`
- IA API: `GET /health`

### Logs
- Consultez les logs Render pour debug
- Les deux services ont des logs détaillés

### Tests
```bash
# Test ANDFChat
curl https://votre-andf-service.onrender.com/health

# Test IA API  
curl https://votre-ia-service.onrender.com/health
```