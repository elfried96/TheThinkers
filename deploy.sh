#!/bin/bash
# Script de déploiement pour Render

set -e

echo "🚀 Déploiement HackIA2025 sur Render"
echo "====================================="

# Vérifications préalables
if [ ! -f ".env" ]; then
    echo "❌ Fichier .env manquant"
    echo "💡 Copiez .env.example vers .env et remplissez les valeurs"
    exit 1
fi

# Source des variables d'environnement
source .env

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ GOOGLE_API_KEY manquante dans .env"
    exit 1
fi

echo "✅ Configuration vérifiée"

# Build local pour tester
echo ""
echo "🔧 Build local des images Docker..."

echo "📦 Build ANDFChat Backend..."
docker build -t hackia/andfchat:latest ./ANDFChat

echo "📦 Build API Coordonnées..."
docker build -t hackia/ia-api:latest ./IA

echo "✅ Images buildées avec succès"

# Test local optionnel
read -p "🧪 Voulez-vous tester localement avant le déploiement? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🏃 Lancement des tests locaux..."
    docker-compose up --build -d
    
    echo "⏳ Attente du démarrage des services..."
    sleep 15
    
    # Test ANDFChat
    echo "🔍 Test ANDFChat (port 8001)..."
    curl -f http://localhost:8001/health || echo "❌ ANDFChat non accessible"
    
    # Test API IA
    echo "🔍 Test API IA (port 8002)..."
    curl -f http://localhost:8002/health || echo "❌ API IA non accessible"
    
    echo "🛑 Arrêt des tests..."
    docker-compose down
fi

# Instructions pour Render
echo ""
echo "📋 ÉTAPES POUR RENDER:"
echo "======================"
echo ""
echo "1️⃣ Connectez votre repo GitHub à Render"
echo "2️⃣ Créez deux nouveaux Web Services:"
echo ""
echo "   🔹 ANDFChat Backend:"
echo "      - Name: andfchat-backend"
echo "      - Environment: Docker"
echo "      - Dockerfile Path: ./ANDFChat/Dockerfile"
echo "      - Build Context: ./ANDFChat"
echo ""
echo "   🔹 API Coordonnées:"
echo "      - Name: ia-coordinates-api" 
echo "      - Environment: Docker"
echo "      - Dockerfile Path: ./IA/Dockerfile"
echo "      - Build Context: ./IA"
echo ""
echo "3️⃣ Configurez les variables d'environnement:"
echo "   - GOOGLE_API_KEY=${GOOGLE_API_KEY}"
echo "   - PORT=10000 (Render utilise PORT au lieu de 8000)"
echo "   - ENVIRONMENT=production"
echo ""
echo "4️⃣ URLs de production (une fois déployé):"
echo "   - ANDFChat: https://andfchat-backend.onrender.com"
echo "   - API IA: https://ia-coordinates-api.onrender.com"
echo ""
echo "🎉 Déploiement prêt!"