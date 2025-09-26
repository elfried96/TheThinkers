#!/usr/bin/env python3
"""
Script de vérification avant déploiement
Vérifie que tous les fichiers nécessaires sont présents
"""
import os
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Vérifie qu'un fichier existe"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MANQUANT")
        return False

def check_deployment_ready():
    """Vérifie que tout est prêt pour le déploiement"""
    
    print("🔍 VÉRIFICATION DES FICHIERS DE DÉPLOIEMENT")
    print("=" * 60)
    
    base_path = "/home/elfried-kinzoun/HackAsini"
    all_good = True
    
    # Fichiers ANDFChat
    print("\n📦 ANDFChat Backend:")
    files_andf = [
        (f"{base_path}/IA/ANDFChat/Dockerfile", "Dockerfile ANDFChat"),
        (f"{base_path}/IA/ANDFChat/pyproject.toml", "Dependencies ANDFChat"),
        (f"{base_path}/IA/ANDFChat/enhanced_backend.py", "Backend principal"),
        (f"{base_path}/IA/ANDFChat/start_server.py", "Script démarrage"),
        (f"{base_path}/IA/ANDFChat/.dockerignore", "Docker ignore")
    ]
    
    for file_path, desc in files_andf:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # Fichiers IA API
    print("\n🧠 IA Coordinate API:")
    files_ia = [
        (f"{base_path}/IA/Dockerfile", "Dockerfile IA API"),
        (f"{base_path}/IA/pyproject.toml", "Dependencies IA API"),
        (f"{base_path}/IA/main_final.py", "API principale"),
        (f"{base_path}/IA/start_api_server.py", "Script démarrage API"),
        (f"{base_path}/IA/.dockerignore", "Docker ignore")
    ]
    
    for file_path, desc in files_ia:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # Fichiers de configuration
    print("\n⚙️ Configuration:")
    config_files = [
        (f"{base_path}/render-config.md", "Guide Render"),
        (f"{base_path}/docker-compose.yml", "Docker Compose")
    ]
    
    for file_path, desc in config_files:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # Résultat final
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 TOUT EST PRÊT POUR LE DÉPLOIEMENT RENDER!")
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. Commitez et pushez sur GitHub")
        print("2. Créez les services sur Render.com")
        print("3. Configurez les variables d'environnement")
        print("4. Déployez les services")
        print("\n📖 Consultez render-config.md pour les détails")
        return True
    else:
        print("❌ DES FICHIERS SONT MANQUANTS!")
        print("Corrigez les problèmes avant de déployer.")
        return False

if __name__ == "__main__":
    success = check_deployment_ready()
    exit(0 if success else 1)