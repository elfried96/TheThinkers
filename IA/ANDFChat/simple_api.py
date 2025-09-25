"""
API FastAPI simplifiée pour le chatbot ANDF
===========================================
Version sans dépendances ML lourdes pour démarrage rapide
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Import du chatbot simple
from simple_demo import SimpleANDFChatbot

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modèles Pydantic
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    confidence: float
    sources: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    mode: str

def create_simple_app() -> FastAPI:
    """Crée l'application FastAPI simplifiée"""
    
    app = FastAPI(
        title="ANDF Chatbot API (Simple)",
        description="API simplifiée pour le chatbot ANDF - sans dépendances ML",
        version="1.0.0-simple",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Instance du chatbot simple
    chatbot = None
    
    @app.on_event("startup")
    async def startup_event():
        nonlocal chatbot
        try:
            logger.info("🚀 Initialisation du chatbot ANDF simple...")
            chatbot = SimpleANDFChatbot()
            logger.info("✅ Chatbot ANDF simple prêt")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            raise e
    
    @app.get("/", response_model=Dict[str, str])
    async def root():
        """Page d'accueil de l'API"""
        return {
            "message": "API Chatbot ANDF (Version Simplifiée)",
            "version": "1.0.0-simple", 
            "mode": "demo",
            "docs": "/docs",
            "health": "/health"
        }
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Vérification de l'état du service"""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0-simple",
            mode="demo"
        )
    
    @app.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        """Endpoint principal pour les conversations"""
        if not chatbot:
            raise HTTPException(
                status_code=503, 
                detail="Chatbot non initialisé"
            )
        
        try:
            logger.info(f"🤖 Nouvelle requête: {request.message[:50]}...")
            
            result = chatbot.chat(
                query=request.message,
                session_id=request.session_id
            )
            
            response = ChatResponse(
                response=result["response"],
                session_id=result["session_id"],
                timestamp=datetime.now().isoformat(),
                confidence=result["confidence"],
                sources=result["sources"],
                metadata=result.get("metadata", {})
            )
            
            logger.info(f"✅ Réponse générée (confiance: {result['confidence']:.2f})")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors du traitement: {str(e)}"
            )
    
    @app.get("/procedures", response_model=List[Dict[str, Any]])
    async def get_procedures():
        """Liste des procédures ANDF"""
        if not chatbot:
            raise HTTPException(status_code=503, detail="Chatbot non initialisé")
        
        try:
            procedures = []
            proc_data = chatbot.knowledge_base.get("procedures_principales", {})
            
            for proc_key, proc_info in proc_data.items():
                procedures.append({
                    "id": proc_key,
                    "nom": proc_info.get("nom_complet", ""),
                    "cout": proc_info.get("cout_base", 0),
                    "duree": proc_info.get("duree_estimee", ""),
                    "description": proc_info.get("description", "")
                })
            
            return procedures
            
        except Exception as e:
            logger.error(f"❌ Erreur procédures: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/tarifs", response_model=Dict[str, Any])
    async def get_tarifs():
        """Tarifs des services ANDF"""
        if not chatbot:
            raise HTTPException(status_code=503, detail="Chatbot non initialisé")
        
        try:
            return chatbot.knowledge_base.get("tarifs_detailles", {})
        except Exception as e:
            logger.error(f"❌ Erreur tarifs: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/bcdf", response_model=List[Dict[str, Any]])
    async def get_bcdf():
        """Informations BCDF"""
        bcdf_data = [
            {
                "commune": "Cotonou",
                "adresse": "Quartier Gbégamey",
                "telephone": "+229 21 30 10 20",
                "departement": "Littoral"
            },
            {
                "commune": "Porto-Novo",
                "adresse": "Centre-ville", 
                "telephone": "+229 20 21 22 23",
                "departement": "Ouémé"
            },
            {
                "commune": "Parakou",
                "adresse": "Centre administratif",
                "telephone": "+229 23 61 03 04", 
                "departement": "Borgou"
            }
        ]
        return bcdf_data
    
    @app.get("/stats", response_model=Dict[str, Any])
    async def get_stats():
        """Statistiques du système"""
        if not chatbot:
            raise HTTPException(status_code=503, detail="Chatbot non initialisé")
        
        return {
            **chatbot.stats,
            "mode": "simple",
            "active_sessions": len(chatbot.session_history),
            "knowledge_sections": len(chatbot.knowledge_base),
            "qa_pairs": len(chatbot.qa_dataset.get("training_dataset", {}).get("qa_pairs", []))
        }
    
    # Gestion des erreurs
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return {
            "error": "Endpoint non trouvé",
            "message": "Vérifiez l'URL de votre requête",
            "docs": "/docs"
        }
    
    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        return {
            "error": "Erreur interne du serveur",
            "message": "Une erreur s'est produite. Contactez l'ANDF.",
            "contact": "+229 21 30 10 20"
        }
    
    return app

# Pour lancement direct
if __name__ == "__main__":
    import uvicorn
    
    app = create_simple_app()
    
    print("🚀 Lancement de l'API ANDF simplifiée...")
    print("📚 Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )