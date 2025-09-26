#!/usr/bin/env python3
"""
Script de lancement rapide pour l'API d'extraction de coordonnées
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    required_packages = [
        'fastapi', 'uvicorn', 'google.generativeai', 'numpy', 
        'cv2', 'pandas', 'PIL', 'dotenv', 'requests', 
        'pyproj', 'geopandas', 'shapely'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                import PIL
            elif package == 'google.generativeai':
                import google.generativeai
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Packages manquants: {', '.join(missing_packages)}")
        print("   Installez avec: uv sync")
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def check_env_vars():
    """Vérifie les variables d'environnement"""
    from dotenv import load_dotenv
    load_dotenv()
    
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ GOOGLE_API_KEY manquante dans .env")
        print("   Créez un fichier .env avec: GOOGLE_API_KEY=your_key_here")
        return False
    
    print("✅ Variables d'environnement OK")
    return True

def main():
    print("🚀 Démarrage API d'extraction de coordonnées")
    print("=" * 50)
    
    # Vérifications préalables
    if not check_dependencies():
        return 1
    
    if not check_env_vars():
        return 1
    
    # Vérifier que le fichier main_final.py existe
    main_file = Path("main_final.py")
    if not main_file.exists():
        print(f"❌ Fichier main_final.py introuvable dans {Path.cwd()}")
        return 1
    
    print("\n🌐 Lancement du serveur FastAPI...")
    print("   URL: http://localhost:8000")
    print("   Documentation: http://localhost:8000/docs")
    print("   Santé: http://localhost:8000/health")
    print("\n💡 Ctrl+C pour arrêter le serveur")
    
    # Lancer le serveur
    import uvicorn
    try:
        uvicorn.run(
            "main_final:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur")
        return 0

if __name__ == "__main__":
    sys.exit(main())