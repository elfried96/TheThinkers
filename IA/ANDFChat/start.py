#!/usr/bin/env python3
"""
Script de démarrage pour le chatbot ANDF
========================================
Lance le système approprié selon les dépendances disponibles
"""

import sys
import subprocess
import importlib
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependency(module_name: str) -> bool:
    """Vérifie si un module est disponible"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def install_basic_dependencies():
    """Installe les dépendances de base via uv"""
    basic_deps = [
        "fastapi",
        "uvicorn",
        "pydantic", 
        "httpx",
        "python-multipart"
    ]
    
    try:
        logger.info("📦 Installation des dépendances de base...")
        cmd = ["uv", "add"] + basic_deps
        subprocess.run(cmd, check=True)
        logger.info("✅ Dépendances de base installées")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur installation: {e}")
        return False
    except FileNotFoundError:
        logger.error("❌ 'uv' non trouvé. Installez uv ou utilisez pip")
        return False

def install_ml_dependencies():
    """Installe les dépendances ML via uv"""
    ml_deps = [
        "chromadb",
        "sentence-transformers",
        "torch",
        "numpy",
        "scikit-learn"
    ]
    
    try:
        logger.info("🤖 Installation des dépendances ML...")
        cmd = ["uv", "add"] + ml_deps
        subprocess.run(cmd, check=True)
        logger.info("✅ Dépendances ML installées")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur installation ML: {e}")
        return False

def start_simple_demo():
    """Lance la démonstration simple"""
    logger.info("🚀 Lancement de la démonstration simple...")
    try:
        from simple_demo import demo_conversation
        demo_conversation()
    except Exception as e:
        logger.error(f"❌ Erreur démonstration: {e}")

def start_full_api():
    """Lance l'API complète avec RAG"""
    logger.info("🚀 Lancement de l'API FastAPI complète...")
    try:
        subprocess.run([
            sys.executable, "main.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur API: {e}")
    except KeyboardInterrupt:
        logger.info("👋 Arrêt de l'API")

def start_simple_api():
    """Lance une API simplifiée sans ML"""
    logger.info("🚀 Lancement de l'API simplifiée...")
    
    # Créer un serveur FastAPI simple
    try:
        import uvicorn
        from simple_api import create_simple_app
        
        app = create_simple_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except ImportError:
        logger.error("❌ FastAPI/Uvicorn non disponibles")
    except Exception as e:
        logger.error(f"❌ Erreur API simple: {e}")

def main():
    """Point d'entrée principal"""
    print("🇧🇯 CHATBOT ANDF - DÉMARRAGE AUTOMATIQUE")
    print("=" * 50)
    
    # Vérification des fichiers de données
    data_files = [
        "data/andf_knowledge_base.json",
        "data/training_qa_dataset.json"
    ]
    
    missing_files = [f for f in data_files if not Path(f).exists()]
    if missing_files:
        logger.error(f"❌ Fichiers manquants: {missing_files}")
        return 1
    
    logger.info("✅ Fichiers de données présents")
    
    # Vérification des dépendances
    has_fastapi = check_dependency("fastapi")
    has_uvicorn = check_dependency("uvicorn") 
    has_chromadb = check_dependency("chromadb")
    has_transformers = check_dependency("transformers")
    
    logger.info(f"📊 État des dépendances:")
    logger.info(f"   FastAPI: {'✅' if has_fastapi else '❌'}")
    logger.info(f"   Uvicorn: {'✅' if has_uvicorn else '❌'}")
    logger.info(f"   ChromaDB: {'✅' if has_chromadb else '❌'}")
    logger.info(f"   Transformers: {'✅' if has_transformers else '❌'}")
    
    # Logique de démarrage
    if has_fastapi and has_uvicorn and has_chromadb and has_transformers:
        # Système complet disponible
        logger.info("🎯 Toutes les dépendances disponibles - API complète")
        start_full_api()
        
    elif has_fastapi and has_uvicorn:
        # API basique disponible
        logger.info("⚡ Dépendances de base - API simplifiée")
        start_simple_api()
        
    else:
        # Mode démonstration seulement
        logger.info("💡 Mode démonstration simple")
        
        # Proposer l'installation
        response = input("\n❓ Installer les dépendances ? (y/N): ").strip().lower()
        
        if response in ['y', 'yes', 'o', 'oui']:
            if install_basic_dependencies():
                logger.info("✅ Redémarrez le script pour utiliser l'API")
            else:
                logger.info("🔄 Lancement en mode démonstration...")
                start_simple_demo()
        else:
            start_simple_demo()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}")
        sys.exit(1)