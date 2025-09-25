"""
Backend ANDF avec intégration Gemini
===================================
Point d'entrée principal avec FastAPI et Gemini
"""

import asyncio
import uvicorn
from enhanced_backend import app
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

if __name__ == "__main__":
    # Configuration du serveur
    uvicorn.run(
        "run_enhanced_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Activation du rechargement automatique
        log_level="info"
    )
