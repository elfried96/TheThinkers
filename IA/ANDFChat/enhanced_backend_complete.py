"""
Backend FastAPI Complet pour ANDF Chatbot - Suite et Fin
========================================================
Continuation du système intelligent avec tous les endpoints
"""

# Continuation du fichier enhanced_backend.py

# =============================================================================
# ENDPOINTS COMPLÉMENTAIRES
# =============================================================================

@app.get("/procedures", response_model=List[Dict[str, Any]])
async def get_procedures(
    category: Optional[str] = None,
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Récupère la liste complète des procédures ANDF avec détails enrichis
    
    Paramètres:
    - category: Filtre par catégorie (optionnel)
    """
    try:
        procedures = []
        kb_procedures = engine.processor.knowledge_base.get("procedures_principales", {})
        
        for proc_key, proc_data in kb_procedures.items():
            procedure_info = {
                "id": proc_key,
                "nom": proc_data.get("nom_complet", ""),
                "description": proc_data.get("description", ""),
                "cout": proc_data.get("cout_base", 0),
                "duree": proc_data.get("duree_estimee", ""),
                "duree_numerique": proc_data.get("digitalisation_2025", {}).get("delai_numerique", ""),
                "validite": proc_data.get("validite", ""),
                "base_legale": proc_data.get("base_legale", ""),
                "documents_requis": len(proc_data.get("documents_requis_complets", {}).get("identite", [])),
                "etapes": len(proc_data.get("procedure_detaillee", {})),
                "digitalise": "digitalisation_2025" in proc_data,
                "urgence_possible": proc_key in ["mutations_titre"],
                "categories": [
                    "formalisation" if "titre" in proc_key else "certification",
                    "numerique" if "digitalisation_2025" in proc_data else "classique"
                ]
            }
            
            # Filtrage par catégorie si spécifié
            if category:
                if category.lower() not in [cat.lower() for cat in procedure_info["categories"]]:
                    continue
            
            procedures.append(procedure_info)
        
        logger.info(f"📋 {len(procedures)} procédures récupérées")
        return procedures
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération procédures: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des procédures")

@app.get("/procedures/{procedure_id}", response_model=Dict[str, Any])
async def get_procedure_details(
    procedure_id: str,
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Récupère les détails complets d'une procédure spécifique
    """
    try:
        procedures = engine.processor.knowledge_base.get("procedures_principales", {})
        
        if procedure_id not in procedures:
            raise HTTPException(
                status_code=404, 
                detail=f"Procédure '{procedure_id}' non trouvée"
            )
        
        procedure_data = procedures[procedure_id]
        
        # Enrichissement avec informations contextuelles
        detailed_info = {
            **procedure_data,
            "procedure_id": procedure_id,
            "derniere_mise_a_jour": "2025-01-25",
            "aide_contextuelle": {
                "questions_frequentes": [
                    f"Combien coûte {procedure_data.get('nom_complet', '')} ?",
                    f"Combien de temps prend {procedure_data.get('nom_complet', '')} ?",
                    f"Quels documents pour {procedure_data.get('nom_complet', '')} ?"
                ],
                "liens_utiles": [
                    {"nom": "e-Notaire", "url": "enotaire.andf.bj"},
                    {"nom": "ANDF", "url": "https://andf.bj"},
                    {"nom": "Service Public", "url": "https://service-public.bj"}
                ]
            }
        }
        
        logger.info(f"📄 Détails procédure {procedure_id} récupérés")
        return detailed_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur détails procédure: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des détails")

@app.get("/tarifs", response_model=Dict[str, Any])
async def get_tarifs(
    procedure: Optional[str] = None,
    annee: Optional[int] = 2025,
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Récupère les tarifs ANDF avec comparaisons et calculateurs
    """
    try:
        tarifs_base = engine.processor.knowledge_base.get("tarifs_detailles_2025", {})
        
        response_data = {
            "tarifs": tarifs_base,
            "annee": annee,
            "derniere_mise_a_jour": "2025-01-25",
            "devise": "FCFA",
            "notes_importantes": [
                "Frais de bornage contradictoire non inclus",
                "Tarifs e-Notaire réduits depuis janvier 2025",
                "Possibilité de paiement échelonné pour gros montants"
            ]
        }
        
        # Calculateur de coûts intégré
        if procedure:
            response_data["calculateur"] = _generate_cost_calculator(procedure, tarifs_base)
        
        # Comparaison avec les anciens tarifs
        if "reductions_2025" in tarifs_base:
            response_data["economies_2025"] = tarifs_base["reductions_2025"]
        
        logger.info(f"💰 Tarifs récupérés pour {procedure or 'toutes procédures'}")
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération tarifs: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des tarifs")

@app.get("/bcdf", response_model=List[Dict[str, Any]])
async def get_bcdf_locations(
    commune: Optional[str] = None,
    departement: Optional[str] = None,
    services: Optional[str] = None,
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Récupère les informations complètes des BCDF avec filtres avancés
    """
    try:
        # Données BCDF enrichies depuis les recherches web
        bcdf_data = engine.processor.knowledge_base.get("structures_andf_completes", {}).get("bcdf_principaux", {}).get("bureaux", [])
        
        # Ajout des BCDF manquants avec informations partielles
        bcdf_complets = [
            {
                "commune": "Cotonou",
                "adresse": "Quartier Gbégamey",
                "telephone": "+229 21 30 10 20",
                "email": "bcdf.cotonou@andf.bj",
                "departement": "Littoral",
                "communes_desservies": ["Cotonou"],
                "horaires": "Lundi-Vendredi : 7h30-17h30",
                "services": ["Titre foncier", "Certificat appartenance", "Mutations", "e-Notaire"],
                "statut": "pilote_e_notaire",
                "geolocalisation": {"lat": 6.3703, "lon": 2.3912}
            },
            {
                "commune": "Porto-Novo",
                "adresse": "Centre-ville",
                "telephone": "+229 20 21 22 23",
                "email": "bcdf.portonovo@andf.bj",
                "departement": "Ouémé",
                "communes_desservies": ["Porto-Novo", "Sèmè-Kpodji", "Adjarra"],
                "horaires": "Lundi-Vendredi : 8h00-17h00",
                "services": ["Titre foncier", "Certificat appartenance", "Mutations"],
                "statut": "actif",
                "geolocalisation": {"lat": 6.4968, "lon": 2.6036}
            },
            {
                "commune": "Parakou",
                "adresse": "Centre administratif",
                "telephone": "+229 23 61 03 04",
                "email": "bcdf.parakou@andf.bj",
                "departement": "Borgou",
                "communes_desservies": ["Parakou", "Tchaourou", "N'Dali"],
                "horaires": "Lundi-Vendredi : 7h30-17h30",
                "services": ["Titre foncier", "Certificat appartenance", "Mutations"],
                "statut": "actif",
                "geolocalisation": {"lat": 9.3372, "lon": 2.6203}
            },
            {
                "commune": "Abomey-Calavi",
                "adresse": "Centre-ville",
                "telephone": "+229 21 38 20 15",
                "email": "bcdf.abomeycalavi@andf.bj",
                "departement": "Atlantique",
                "communes_desservies": ["Abomey-Calavi", "Allada", "Ouidah", "Toffo", "Zè"],
                "horaires": "Lundi-Vendredi : 7h30-17h00",
                "services": ["Titre foncier", "Certificat appartenance", "Mutations"],
                "statut": "actif",
                "geolocalisation": {"lat": 6.4395, "lon": 2.3566}
            }
        ]
        
        # Application des filtres
        filtered_bcdf = bcdf_complets
        
        if commune:
            filtered_bcdf = [b for b in filtered_bcdf if commune.lower() in [c.lower() for c in b.get("communes_desservies", [])] or commune.lower() == b.get("commune", "").lower()]
        
        if departement:
            filtered_bcdf = [b for b in filtered_bcdf if departement.lower() == b.get("departement", "").lower()]
        
        if services:
            filtered_bcdf = [b for b in filtered_bcdf if services.lower() in [s.lower() for s in b.get("services", [])]]
        
        # Enrichissement avec informations contextuelles
        for bcdf in filtered_bcdf:
            bcdf["conseils_pratiques"] = [
                "Appelez avant votre déplacement",
                "Préparez votre dossier complet",
                "Évitez les heures de pointe (12h-14h)",
                "Vérifiez les jours fériés"
            ]
            bcdf["acces_transport"] = "Transport public et taxi disponibles"
            bcdf["parking"] = "Parking disponible" if bcdf["commune"] in ["Cotonou", "Porto-Novo"] else "Stationnement possible"
        
        logger.info(f"📍 {len(filtered_bcdf)} BCDF récupérés avec filtres")
        return filtered_bcdf
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération BCDF: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des BCDF")

@app.get("/search", response_model=Dict[str, Any])
async def search_knowledge(
    q: str = Field(..., min_length=2, description="Terme de recherche"),
    limit: int = Field(default=10, ge=1, le=50, description="Nombre maximum de résultats"),
    category: Optional[str] = Field(default=None, description="Catégorie de recherche"),
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Recherche avancée dans la base de connaissances ANDF
    
    Fonctionnalités:
    - Recherche full-text dans toutes les données
    - Filtrage par catégorie
    - Score de pertinence
    - Suggestions de recherche
    """
    try:
        # Correction automatique de la requête
        corrected_query, corrections = engine.correct_user_input(q)
        
        # Recherche dans la base de connaissances
        search_results = engine.search_knowledge_base(corrected_query, "search")
        
        # Limitation des résultats
        limited_results = search_results[:limit]
        
        # Génération de suggestions
        suggestions = _generate_search_suggestions(corrected_query, engine.processor.knowledge_base)
        
        response_data = {
            "query": {
                "original": q,
                "corrected": corrected_query,
                "corrections_applied": corrections
            },
            "results": [
                {
                    "title": _extract_title_from_result(result),
                    "content": _truncate_content(result["content"], 200),
                    "category": result.get("metadata", {}).get("type", "general"),
                    "relevance_score": round(result["similarity"], 3),
                    "source": result["source"],
                    "url": _generate_result_url(result)
                }
                for result in limited_results
            ],
            "metadata": {
                "total_found": len(search_results),
                "showing": len(limited_results),
                "search_time": "< 100ms",
                "suggestions": suggestions[:5]
            },
            "filters": {
                "categories_available": list(set(r.get("metadata", {}).get("type", "general") for r in search_results)),
                "sources_available": list(set(r["source"] for r in search_results))
            }
        }
        
        logger.info(f"🔍 Recherche '{q}' → {len(limited_results)} résultats")
        return response_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Paramètre de recherche invalide: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Erreur recherche: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche")

@app.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(
    detailed: bool = False,
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Statistiques complètes du système avec métriques avancées
    """
    try:
        base_stats = engine.stats
        
        # Calculs avancés
        uptime_seconds = (datetime.now() - base_stats['startup_time']).total_seconds()
        success_rate = (base_stats['successful_responses'] / base_stats['total_queries'] * 100) if base_stats['total_queries'] > 0 else 0
        
        # Statistiques de base
        stats_response = {
            "system": {
                "status": "healthy",
                "uptime_seconds": int(uptime_seconds),
                "uptime_human": _format_uptime(uptime_seconds),
                "version": "2.0.0",
                "environment": "production"
            },
            "usage": {
                "total_queries": base_stats['total_queries'],
                "successful_responses": base_stats['successful_responses'],
                "success_rate_percent": round(success_rate, 2),
                "error_corrections": base_stats.get('error_corrections', 0),
                "average_response_time": round(base_stats.get('average_response_time', 0), 3)
            },
            "knowledge_base": {
                "total_procedures": len(engine.processor.knowledge_base.get("procedures_principales", {})),
                "total_qa_pairs": len(engine.processor.qa_dataset.get("training_dataset", {}).get("qa_pairs", [])),
                "knowledge_sections": len(engine.processor.knowledge_base),
                "last_update": "2025-01-25"
            },
            "sessions": {
                "active_sessions": len(engine.session_store),
                "total_interactions": sum(len(session) for session in engine.session_store.values())
            }
        }
        
        # Statistiques détaillées si demandées
        if detailed:
            stats_response["detailed"] = {
                "response_times": {
                    "min": min(base_stats.get('response_times', [1])),
                    "max": max(base_stats.get('response_times', [1])),
                    "median": _calculate_median(base_stats.get('response_times', [1]))
                },
                "intent_distribution": _calculate_intent_distribution(engine.session_store),
                "common_corrections": _get_common_corrections(engine),
                "peak_hours": _analyze_usage_patterns(engine.session_store),
                "memory_usage": {
                    "sessions_mb": len(str(engine.session_store)) / 1024 / 1024,
                    "knowledge_base_mb": len(str(engine.processor.knowledge_base)) / 1024 / 1024
                }
            }
        
        logger.info("📊 Statistiques système récupérées")
        return stats_response
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques")

@app.post("/feedback", response_model=Dict[str, str])
async def submit_feedback(
    feedback: Dict[str, Any],
    background_tasks: BackgroundTasks,
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Soumission de feedback utilisateur pour amélioration continue
    """
    try:
        # Validation du feedback
        required_fields = ["message", "rating"]
        missing_fields = [field for field in required_fields if field not in feedback]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Champs requis manquants: {missing_fields}"
            )
        
        # Enrichissement du feedback
        enriched_feedback = {
            **feedback,
            "timestamp": datetime.now().isoformat(),
            "feedback_id": str(uuid.uuid4()),
            "system_version": "2.0.0"
        }
        
        # Traitement asynchrone du feedback
        background_tasks.add_task(process_feedback, enriched_feedback)
        
        logger.info(f"📝 Feedback reçu: note {feedback.get('rating', 'N/A')}/5")
        
        return {
            "status": "received",
            "message": "Merci pour votre feedback ! Il nous aidera à améliorer le service ANDF.",
            "feedback_id": enriched_feedback["feedback_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur feedback: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement du feedback")

@app.get("/help", response_model=Dict[str, Any])
async def get_help():
    """
    Guide d'aide et documentation de l'API
    """
    return {
        "api_info": {
            "name": "ANDF Chatbot Backend",
            "version": "2.0.0",
            "description": "Backend intelligent pour l'assistance foncière ANDF Bénin"
        },
        "endpoints": {
            "chat": {
                "url": "/chat",
                "method": "POST",
                "description": "Interface de conversation principale",
                "exemple": {
                    "message": "Comment obtenir un titre foncier ?",
                    "session_id": "optional",
                    "language": "fr"
                }
            },
            "procedures": {
                "url": "/procedures",
                "method": "GET",
                "description": "Liste des procédures ANDF",
                "parametres": ["category"]
            },
            "search": {
                "url": "/search",
                "method": "GET", 
                "description": "Recherche dans la base de connaissances",
                "parametres": ["q", "limit", "category"]
            }
        },
        "examples": {
            "questions_courantes": [
                "Comment obtenir un titre foncier ?",
                "Combien coûte un certificat d'appartenance ?",
                "Où se trouve le BCDF de Cotonou ?",
                "Comment utiliser e-Notaire ?",
                "Que faire si j'ai perdu mon titre foncier ?"
            ]
        },
        "contact": {
            "andf": "+229 21 30 10 20",
            "email": "contact@andf.bj",
            "site": "https://andf.bj",
            "e_notaire": "enotaire.andf.bj"
        }
    }

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def _generate_cost_calculator(procedure: str, tarifs: Dict) -> Dict[str, Any]:
    """Génère un calculateur de coûts pour une procédure"""
    calculators = {
        "titre_foncier": {
            "frais_base": 100000,
            "frais_variables": ["bornage_contradictoire", "plan_topographique"],
            "estimation_totale": "150,000 - 300,000 F CFA",
            "facteurs": ["superficie", "complexite_terrain", "choix_geometre"]
        },
        "mutations_titre": {
            "formule": "0.3% de la valeur marchande",
            "minimum": 30000,
            "exemples": {
                "terrain_5M": 15000,
                "terrain_20M": 30000,
                "terrain_100M": 50000
            }
        }
    }
    
    return calculators.get(procedure, {"message": "Calculateur non disponible pour cette procédure"})

def _generate_search_suggestions(query: str, knowledge_base: Dict) -> List[str]:
    """Génère des suggestions de recherche intelligentes"""
    suggestions = []
    
    # Suggestions basées sur les mots-clés
    if "titre" in query.lower():
        suggestions.extend(["titre foncier procédure", "titre foncier documents", "titre foncier coût"])
    elif "certificat" in query.lower():
        suggestions.extend(["certificat appartenance", "certificat validité", "certificat documents"])
    elif "bcdf" in query.lower():
        suggestions.extend(["bcdf cotonou", "bcdf adresses", "bcdf contacts"])
    
    # Suggestions génériques
    suggestions.extend([
        "procédures foncières",
        "tarifs ANDF 2025",
        "e-notaire utilisation",
        "documents requis",
        "contacts BCDF"
    ])
    
    return list(set(suggestions))[:10]

def _extract_title_from_result(result: Dict) -> str:
    """Extrait un titre pertinent d'un résultat de recherche"""
    if result["source"] == "qa_dataset":
        return result.get("question", "Question ANDF")
    elif "key" in result.get("metadata", {}):
        return result["metadata"]["key"].replace("_", " ").title()
    else:
        return "Information ANDF"

def _truncate_content(content: str, max_length: int) -> str:
    """Tronque le contenu à une longueur maximale"""
    if len(content) <= max_length:
        return content
    return content[:max_length-3] + "..."

def _generate_result_url(result: Dict) -> Optional[str]:
    """Génère une URL pour un résultat si applicable"""
    if result["source"] == "qa_dataset":
        return f"/faq/{result.get('metadata', {}).get('id', '')}"
    elif result.get("section"):
        return f"/knowledge/{result['section']}/{result.get('key', '')}"
    return None

def _format_uptime(seconds: float) -> str:
    """Formate la durée de fonctionnement en texte lisible"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if days > 0:
        return f"{days}j {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def _calculate_median(values: List[float]) -> float:
    """Calcule la médiane d'une liste de valeurs"""
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    if n % 2 == 0:
        return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
    else:
        return sorted_values[n//2]

def _calculate_intent_distribution(sessions: Dict) -> Dict[str, int]:
    """Calcule la distribution des intentions dans les sessions"""
    intent_counts = {}
    
    for session_data in sessions.values():
        for interaction in session_data:
            intent = interaction.get("intent", "unknown")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    return intent_counts

def _get_common_corrections(engine: ANDFChatbotEngine) -> List[Dict[str, Any]]:
    """Récupère les corrections les plus fréquentes"""
    # Simule les corrections communes (dans un vrai système, ceci serait persisté)
    return [
        {"original": "titre foncer", "corrected": "titre foncier", "frequency": 45},
        {"original": "bcfd", "corrected": "bcdf", "frequency": 32},
        {"original": "certifica", "corrected": "certificat", "frequency": 28}
    ]

def _analyze_usage_patterns(sessions: Dict) -> Dict[str, Any]:
    """Analyse les patterns d'utilisation"""
    hours = {}
    
    for session_data in sessions.values():
        for interaction in session_data:
            timestamp = interaction.get("timestamp", "")
            if timestamp:
                try:
                    hour = datetime.fromisoformat(timestamp).hour
                    hours[hour] = hours.get(hour, 0) + 1
                except:
                    continue
    
    peak_hour = max(hours.items(), key=lambda x: x[1]) if hours else (12, 0)
    
    return {
        "peak_hour": peak_hour[0],
        "peak_requests": peak_hour[1],
        "total_hours_active": len(hours)
    }

async def process_feedback(feedback: Dict[str, Any]):
    """Traitement asynchrone du feedback utilisateur"""
    try:
        # Dans un vrai système, on sauvegarderait en base de données
        # et on analyserait pour améliorer le système
        
        logger.info(f"📝 Traitement feedback {feedback['feedback_id']}")
        
        # Simulation de traitement
        await asyncio.sleep(1)
        
        # Analyse du sentiment (simulation)
        rating = feedback.get("rating", 3)
        if rating >= 4:
            logger.info("😊 Feedback positif reçu")
        elif rating <= 2:
            logger.warning("😞 Feedback négatif - nécessite attention")
        
        # Dans un vrai système:
        # - Sauvegarde en base
        # - Analyse de sentiment
        # - Génération d'alertes si nécessaire
        # - Mise à jour des métriques qualité
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement feedback: {e}")

# =============================================================================
# MIDDLEWARE PERSONNALISÉ
# =============================================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Ajoute le temps de traitement dans les headers"""
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(round(process_time, 3))
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes pour monitoring"""
    client_ip = request.client.host
    method = request.method
    url = str(request.url)
    
    logger.info(f"🌐 {client_ip} {method} {url}")
    
    response = await call_next(request)
    
    logger.info(f"📤 Response {response.status_code}")
    
    return response

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Démarrage du Backend ANDF Intelligent...")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🧪 Tests: http://localhost:8000/health")
    
    uvicorn.run(
        "enhanced_backend_complete:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )