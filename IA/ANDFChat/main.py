"""
ANDF Chatbot Backend - FastAPI
===============================
API backend pour le chatbot ANDF du Bénin avec système RAG
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime
import uvicorn

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import du système RAG
from rag_system import ANDFRAGSystem

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
    rag_system_ready: bool

# Initialisation de l'application FastAPI
app = FastAPI(
    title="ANDF Chatbot API",
    description="API backend pour le chatbot de l'Agence Nationale du Domaine et du Foncier du Bénin",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer selon vos besoins en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance du système RAG
rag_system = None

@app.on_event("startup")
async def startup_event():
    """Initialisation du système RAG au démarrage"""
    global rag_system
    try:
        logger.info("🚀 Initialisation du système RAG ANDF...")
        rag_system = ANDFRAGSystem()
        await rag_system.initialize()
        logger.info("✅ Système RAG ANDF initialisé avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation du RAG: {e}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage lors de l'arrêt"""
    global rag_system
    if rag_system:
        await rag_system.cleanup()
    logger.info("👋 Arrêt du serveur ANDF Chatbot")

# Dépendance pour vérifier que le RAG est prêt
async def get_rag_system():
    if rag_system is None:
        raise HTTPException(
            status_code=503, 
            detail="Système RAG non initialisé. Veuillez réessayer dans quelques instants."
        )
    return rag_system

# Routes API

@app.get("/", response_model=Dict[str, str])
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "API Chatbot ANDF - Agence Nationale du Domaine et du Foncier du Bénin",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état du service"""
    return HealthResponse(
        status="healthy" if rag_system else "initializing",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        rag_system_ready=rag_system is not None
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    rag_system: ANDFRAGSystem = Depends(get_rag_system)
):
    """
    Endpoint principal pour les conversations avec le chatbot ANDF
    """
    try:
        logger.info(f"🤖 Nouvelle requête: {request.message[:100]}...")
        
        # Traitement de la requête par le système RAG
        result = await rag_system.process_query(
            query=request.message,
            session_id=request.session_id,
            context=request.context
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
        logger.error(f"❌ Erreur lors du traitement: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de votre demande: {str(e)}"
        )

@app.get("/procedures", response_model=List[Dict[str, Any]])
async def get_procedures(rag_system: ANDFRAGSystem = Depends(get_rag_system)):
    """
    Récupère la liste des procédures disponibles
    """
    try:
        procedures = await rag_system.get_procedures()
        return procedures
    except Exception as e:
        logger.error(f"❌ Erreur récupération procédures: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tarifs", response_model=Dict[str, Any])
async def get_tarifs(rag_system: ANDFRAGSystem = Depends(get_rag_system)):
    """
    Récupère les tarifs des services ANDF
    """
    try:
        tarifs = await rag_system.get_tarifs()
        return tarifs
    except Exception as e:
        logger.error(f"❌ Erreur récupération tarifs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bcdf", response_model=List[Dict[str, Any]])
async def get_bcdf_locations():
    """
    Récupère les informations sur les BCDF
    """
    try:
        # Pour l'instant, retourne les données statiques
        # Dans une vraie implémentation, ceci viendrait d'une base de données
        bcdf_data = [
            {
                "commune": "Cotonou",
                "adresse": "Quartier Gbégamey",
                "telephone": "+229 21 30 10 20",
                "departement": "Littoral",
                "services": ["Titre foncier", "Certificat d'appartenance", "Mutations"]
            },
            {
                "commune": "Porto-Novo", 
                "adresse": "Centre-ville",
                "telephone": "+229 20 21 22 23",
                "departement": "Ouémé",
                "services": ["Titre foncier", "Certificat d'appartenance", "Mutations"]
            },
            {
                "commune": "Parakou",
                "adresse": "Centre administratif",
                "telephone": "+229 23 61 03 04",
                "departement": "Borgou",
                "services": ["Titre foncier", "Certificat d'appartenance", "Mutations"]
            }
        ]
        return bcdf_data
    except Exception as e:
        logger.error(f"❌ Erreur récupération BCDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_model=Dict[str, Any])
async def search_knowledge(
    q: str,
    limit: int = 5,
    rag_system: ANDFRAGSystem = Depends(get_rag_system)
):
    """
    Recherche dans la base de connaissances ANDF
    """
    try:
        if not q or len(q.strip()) < 2:
            raise HTTPException(
                status_code=400, 
                detail="La requête doit contenir au moins 2 caractères"
            )
        
        results = await rag_system.search_knowledge(q, limit)
        
        return {
            "query": q,
            "results": results,
            "total": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur recherche: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=Dict[str, Any])
async def get_stats(rag_system: ANDFRAGSystem = Depends(get_rag_system)):
    """
    Statistiques du système
    """
    try:
        stats = await rag_system.get_stats()
        return stats
    except Exception as e:
        logger.error(f"❌ Erreur stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Gestion des erreurs globales
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
        "message": "Une erreur s'est produite. Veuillez réessayer ou contacter l'ANDF.",
        "contact": "+229 21 30 10 20"
    }

if __name__ == "__main__":
    # Configuration pour le développement
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )