#!/usr/bin/env python3
"""
Script de démarrage pour l'API IA Coordinate Extraction
Optimisé pour déploiement sur Render
"""
import os
import uvicorn
from main_final import app

def main():
    """Lance le serveur API IA avec la configuration Render"""
    
    # Port depuis variable d'environnement (Render utilise PORT)
    port = int(os.getenv("PORT", 8001))
    
    # Host pour Render
    host = "0.0.0.0"
    
    print(f"🚀 Démarrage IA Coordinate API sur {host}:{port}")
    print("=" * 50)
    
    # Configuration pour production
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        # Configuration pour production
        reload=False,
        workers=1,  # Render recommande 1 worker
        # Timeout élevé pour le traitement d'images
        timeout_keep_alive=300
    )

if __name__ == "__main__":
    main()