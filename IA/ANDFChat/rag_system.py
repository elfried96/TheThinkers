"""
Système RAG (Retrieval-Augmented Generation) pour ANDF
======================================================
Implémentation complète du système RAG pour le chatbot ANDF
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
import uuid

# Import des librairies RAG
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
import re

# Configuration du logging
logger = logging.getLogger(__name__)

class ANDFRAGSystem:
    """
    Système RAG complet pour l'ANDF du Bénin
    """
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.embedding_model = None
        self.chroma_client = None
        self.collections = {}
        self.knowledge_base = {}
        self.session_history = {}
        self.stats = {
            "queries_processed": 0,
            "total_documents": 0,
            "average_confidence": 0.0,
            "startup_time": datetime.now().isoformat()
        }
        
    async def initialize(self):
        """Initialisation asynchrone du système RAG"""
        try:
            logger.info("🔧 Initialisation du modèle d'embeddings...")
            await self._initialize_embedding_model()
            
            logger.info("🗂️ Initialisation de ChromaDB...")
            await self._initialize_vector_db()
            
            logger.info("📚 Chargement de la base de connaissances...")
            await self._load_knowledge_base()
            
            logger.info("🔍 Indexation vectorielle...")
            await self._create_vector_indexes()
            
            logger.info("✅ Système RAG ANDF initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            raise e
    
    async def _initialize_embedding_model(self):
        """Initialise le modèle d'embeddings multilingue"""
        try:
            # Modèle optimisé pour le français et les langues locales
            self.embedding_model = SentenceTransformer(
                'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
            )
            logger.info("✅ Modèle d'embeddings chargé")
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle embeddings: {e}")
            raise e
    
    async def _initialize_vector_db(self):
        """Initialise ChromaDB"""
        try:
            # Configuration ChromaDB
            self.chroma_client = chromadb.Client(Settings(
                is_persistent=True,
                persist_directory="./chroma_db"
            ))
            
            # Collections spécialisées
            collection_names = [
                "procedures", "tarifs", "documents", "locations", 
                "legal_info", "faq", "digital_services"
            ]
            
            for name in collection_names:
                try:
                    # Essaie de récupérer la collection existante
                    collection = self.chroma_client.get_collection(name)
                    logger.info(f"📂 Collection '{name}' récupérée")
                except:
                    # Crée une nouvelle collection si elle n'existe pas
                    collection = self.chroma_client.create_collection(
                        name=name,
                        metadata={"description": f"Collection {name} pour ANDF"}
                    )
                    logger.info(f"📂 Collection '{name}' créée")
                
                self.collections[name] = collection
            
            logger.info("✅ ChromaDB initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation ChromaDB: {e}")
            raise e
    
    async def _load_knowledge_base(self):
        """Charge la base de connaissances depuis les fichiers JSON"""
        try:
            # Chargement des données principales
            with open(f"{self.data_dir}/andf_knowledge_base.json", "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
            
            # Chargement du dataset Q&A
            with open(f"{self.data_dir}/training_qa_dataset.json", "r", encoding="utf-8") as f:
                self.qa_dataset = json.load(f)
            
            # Chargement des métadonnées des sources
            with open(f"{self.data_dir}/sources_metadata.txt", "r", encoding="utf-8") as f:
                self.sources_metadata = f.read()
            
            self.stats["total_documents"] = len(self.knowledge_base)
            logger.info(f"✅ Base de connaissances chargée ({self.stats['total_documents']} documents)")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement base de connaissances: {e}")
            raise e
    
    async def _create_vector_indexes(self):
        """Crée les index vectoriels pour la recherche sémantique"""
        try:
            # Indexation des procédures
            await self._index_procedures()
            
            # Indexation des tarifs
            await self._index_tarifs()
            
            # Indexation de la FAQ
            await self._index_faq()
            
            # Indexation des informations légales
            await self._index_legal_info()
            
            logger.info("✅ Indexation vectorielle terminée")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'indexation: {e}")
            raise e
    
    async def _index_procedures(self):
        """Indexe les procédures ANDF"""
        procedures = self.knowledge_base.get("procedures_principales", {})
        
        documents = []
        metadatas = []
        ids = []
        
        for proc_key, proc_data in procedures.items():
            # Document principal de la procédure
            doc_content = self._format_procedure_document(proc_key, proc_data)
            
            documents.append(doc_content)
            metadatas.append({
                "type": "procedure",
                "procedure_id": proc_key,
                "nom": proc_data.get("nom_complet", ""),
                "cout": proc_data.get("cout_base", 0),
                "duree": proc_data.get("duree_estimee", ""),
                "category": "procedures"
            })
            ids.append(f"proc_{proc_key}_{hashlib.md5(doc_content.encode()).hexdigest()[:8]}")
            
        if documents:
            self.collections["procedures"].upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
        logger.info(f"📋 {len(documents)} procédures indexées")
    
    async def _index_tarifs(self):
        """Indexe les tarifs ANDF"""
        tarifs = self.knowledge_base.get("tarifs_detailles", {})
        
        documents = []
        metadatas = []
        ids = []
        
        for category, tarif_data in tarifs.items():
            if isinstance(tarif_data, dict):
                for service, prix in tarif_data.items():
                    if service not in ["devise", "note"]:
                        doc_content = f"Service: {service}\nCatégorie: {category}\nTarif: {prix}\nDevise: FCFA"
                        
                        documents.append(doc_content)
                        metadatas.append({
                            "type": "tarif",
                            "service": service,
                            "category": category,
                            "prix": str(prix)
                        })
                        ids.append(f"tarif_{service}_{hashlib.md5(doc_content.encode()).hexdigest()[:8]}")
        
        if documents:
            self.collections["tarifs"].upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
        logger.info(f"💰 {len(documents)} tarifs indexés")
    
    async def _index_faq(self):
        """Indexe les questions-réponses de la FAQ"""
        qa_pairs = self.qa_dataset.get("training_dataset", {}).get("qa_pairs", [])
        
        documents = []
        metadatas = []
        ids = []
        
        for qa in qa_pairs:
            # Document combinant question et réponse
            doc_content = f"Question: {qa['question']}\nRéponse: {qa['answer']}"
            
            documents.append(doc_content)
            metadatas.append({
                "type": "faq",
                "category": qa.get("category", "general"),
                "intent": qa.get("intent", "general"),
                "question": qa["question"],
                "qa_id": qa.get("id", "")
            })
            ids.append(qa.get("id", f"qa_{len(ids)}"))
        
        if documents:
            self.collections["faq"].upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
        logger.info(f"❓ {len(documents)} Q&A indexées")
    
    async def _index_legal_info(self):
        """Indexe les informations légales"""
        legal_info = self.knowledge_base.get("base_juridique", {})
        definitions = self.knowledge_base.get("definitions_cles", {})
        
        documents = []
        metadatas = []
        ids = []
        
        # Index des informations juridiques
        for key, info in legal_info.items():
            if isinstance(info, dict):
                doc_content = f"Référence légale: {key}\n{json.dumps(info, indent=2, ensure_ascii=False)}"
            else:
                doc_content = f"Référence légale: {key}\nInformation: {info}"
            
            documents.append(doc_content)
            metadatas.append({
                "type": "legal",
                "reference": key,
                "category": "base_juridique"
            })
            ids.append(f"legal_{key}_{hashlib.md5(doc_content.encode()).hexdigest()[:8]}")
        
        # Index des définitions
        for term, definition in definitions.items():
            doc_content = f"Terme: {term}\nDéfinition: {definition}"
            
            documents.append(doc_content)
            metadatas.append({
                "type": "definition",
                "term": term,
                "category": "definitions"
            })
            ids.append(f"def_{term}_{hashlib.md5(doc_content.encode()).hexdigest()[:8]}")
        
        if documents:
            self.collections["legal_info"].upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
        logger.info(f"⚖️ {len(documents)} infos légales indexées")
    
    def _format_procedure_document(self, proc_key: str, proc_data: Dict) -> str:
        """Formate une procédure en document textuel"""
        doc = f"Procédure: {proc_data.get('nom_complet', '')}\n"
        doc += f"Description: {proc_data.get('description', '')}\n"
        doc += f"Durée: {proc_data.get('duree_estimee', '')}\n"
        doc += f"Coût: {proc_data.get('cout_base', 0)} {proc_data.get('devise', 'FCFA')}\n"
        
        # Documents requis
        if "documents_requis" in proc_data:
            doc += "\nDocuments requis:\n"
            for doc_cat in proc_data["documents_requis"]:
                if isinstance(doc_cat, dict) and "documents" in doc_cat:
                    doc += f"- {doc_cat.get('categorie', '')}: {', '.join(doc_cat['documents'])}\n"
        
        # Étapes de la procédure
        if "etapes_procedure" in proc_data:
            doc += "\nÉtapes:\n"
            for etape in proc_data["etapes_procedure"]:
                if isinstance(etape, dict):
                    doc += f"{etape.get('ordre', '')}. {etape.get('nom', '')}: {etape.get('description', '')}\n"
        
        return doc
    
    async def process_query(self, query: str, session_id: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Traite une requête utilisateur et génère une réponse"""
        try:
            # Génération d'un ID de session si nécessaire
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Analyse de la requête
            intent = self._analyze_intent(query)
            entities = self._extract_entities(query)
            
            # Recherche contextuelle
            search_results = await self._search_all_collections(query)
            
            # Génération de la réponse
            response = self._generate_response(query, search_results, intent, entities)
            
            # Calcul de la confiance
            confidence = self._calculate_confidence(search_results, response)
            
            # Mise à jour des statistiques
            self._update_stats(confidence)
            
            # Sauvegarde de l'historique de session
            self._save_session_history(session_id, query, response)
            
            return {
                "response": response,
                "session_id": session_id,
                "confidence": confidence,
                "sources": self._format_sources(search_results),
                "metadata": {
                    "intent": intent,
                    "entities": entities,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement requête: {e}")
            return {
                "response": self._get_error_response(),
                "session_id": session_id or str(uuid.uuid4()),
                "confidence": 0.0,
                "sources": [],
                "metadata": {"error": str(e)}
            }
    
    def _analyze_intent(self, query: str) -> str:
        """Analyse l'intention de la requête"""
        query_lower = query.lower()
        
        # Mapping des intentions
        intent_patterns = {
            "cost_inquiry": ["combien", "coût", "prix", "tarif", "frais"],
            "procedure_info": ["comment", "procédure", "étapes", "démarche", "processus"],
            "location_info": ["où", "adresse", "localisation", "contact", "bcdf"],
            "document_required": ["documents", "pièces", "requis", "nécessaire", "fournir"],
            "problem_solving": ["problème", "conflit", "litige", "aide", "solution"],
            "legal_info": ["loi", "légal", "juridique", "droit", "code foncier"],
            "digital_services": ["e-notaire", "en ligne", "digital", "plateforme", "internet"]
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        return "general"
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extrait les entités de la requête"""
        entities = {
            "procedures": [],
            "communes": [],
            "services": [],
            "amounts": []
        }
        
        query_lower = query.lower()
        
        # Procédures
        procedures = ["titre foncier", "certificat d'appartenance", "mutation", "morcellement", "hypothèque", "bornage"]
        entities["procedures"] = [proc for proc in procedures if proc in query_lower]
        
        # Communes principales
        communes = ["cotonou", "porto-novo", "parakou", "abomey-calavi", "allada", "ouidah"]
        entities["communes"] = [commune for commune in communes if commune in query_lower]
        
        # Montants (recherche de nombres)
        amounts = re.findall(r'\d+[\d\s]*', query)
        entities["amounts"] = amounts
        
        return entities
    
    async def _search_all_collections(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Recherche dans toutes les collections"""
        all_results = []
        
        for collection_name, collection in self.collections.items():
            try:
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                
                # Formatage des résultats
                if results['documents'] and results['documents'][0]:
                    for i in range(len(results['documents'][0])):
                        result = {
                            "content": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i],
                            "distance": results['distances'][0][i] if 'distances' in results else 0.5,
                            "collection": collection_name,
                            "id": results['ids'][0][i]
                        }
                        all_results.append(result)
                        
            except Exception as e:
                logger.warning(f"⚠️ Erreur recherche collection {collection_name}: {e}")
                continue
        
        # Tri par pertinence (distance faible = plus pertinent)
        all_results.sort(key=lambda x: x["distance"])
        
        return all_results[:5]  # Retourne les 5 meilleurs résultats
    
    def _generate_response(self, query: str, search_results: List[Dict], intent: str, entities: Dict) -> str:
        """Génère la réponse finale"""
        if not search_results:
            return self._get_fallback_response(intent)
        
        # Sélection du meilleur résultat
        best_result = search_results[0]
        
        # Génération de réponse spécialisée selon l'intention
        if intent == "cost_inquiry":
            return self._generate_cost_response(query, search_results, entities)
        elif intent == "procedure_info":
            return self._generate_procedure_response(query, search_results, entities)
        elif intent == "location_info":
            return self._generate_location_response(query, search_results, entities)
        else:
            return self._generate_general_response(query, search_results)
    
    def _generate_cost_response(self, query: str, results: List[Dict], entities: Dict) -> str:
        """Génère une réponse spécialisée pour les coûts"""
        response = "💰 **Informations tarifaires ANDF**\n\n"
        
        for result in results[:2]:  # Utilise les 2 meilleurs résultats
            if result["metadata"].get("type") == "tarif":
                service = result["metadata"].get("service", "Service")
                prix = result["metadata"].get("prix", "Non spécifié")
                response += f"**{service}:** {prix}\n"
            elif "coût" in result["content"].lower() or "prix" in result["content"].lower():
                # Extrait les informations de coût du contenu
                lines = result["content"].split('\n')
                for line in lines:
                    if any(word in line.lower() for word in ["coût", "prix", "tarif"]):
                        response += f"- {line.strip()}\n"
        
        response += "\n📞 **Contact:** +229 21 30 10 20\n"
        response += "🌐 **Site:** https://andf.bj"
        
        return response
    
    def _generate_procedure_response(self, query: str, results: List[Dict], entities: Dict) -> str:
        """Génère une réponse spécialisée pour les procédures"""
        response = "📋 **Procédure ANDF**\n\n"
        
        best_result = results[0]
        content = best_result["content"]
        
        # Extraction des informations structurées
        if "Procédure:" in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('Procédure:'):
                    response += f"**{line}**\n\n"
                elif line.startswith('Durée:'):
                    response += f"⏱️ **{line}**\n"
                elif line.startswith('Coût:'):
                    response += f"💰 **{line}**\n"
                elif line.startswith('Documents requis:'):
                    response += f"\n📄 **{line}**\n"
                elif line.startswith('Étapes:'):
                    response += f"\n🔄 **{line}**\n"
                elif line.strip() and line.startswith('-'):
                    response += f"{line}\n"
        else:
            # Fallback: utilise le contenu brut
            response += content
        
        response += "\n**🏢 Service compétent:** BCDF de votre commune"
        
        return response
    
    def _generate_location_response(self, query: str, results: List[Dict], entities: Dict) -> str:
        """Génère une réponse pour les informations de localisation"""
        response = "📍 **Informations BCDF**\n\n"
        
        # Informations statiques des BCDF principaux
        bcdf_info = {
            "cotonou": {
                "adresse": "Quartier Gbégamey",
                "telephone": "+229 21 30 10 20",
                "departement": "Littoral"
            },
            "porto-novo": {
                "adresse": "Centre-ville",
                "telephone": "+229 20 21 22 23", 
                "departement": "Ouémé"
            },
            "parakou": {
                "adresse": "Centre administratif",
                "telephone": "+229 23 61 03 04",
                "departement": "Borgou"
            }
        }
        
        # Recherche de la commune mentionnée
        commune_found = None
        for commune in entities.get("communes", []):
            if commune.lower() in bcdf_info:
                commune_found = commune.lower()
                break
        
        if commune_found:
            info = bcdf_info[commune_found]
            response += f"**BCDF de {commune_found.title()}**\n"
            response += f"📍 **Adresse:** {info['adresse']}\n"
            response += f"📞 **Téléphone:** {info['telephone']}\n"
            response += f"🗺️ **Département:** {info['departement']}\n"
        else:
            response += "**BCDF principaux:**\n\n"
            for commune, info in bcdf_info.items():
                response += f"**{commune.title()}:** {info['adresse']} - {info['telephone']}\n"
        
        response += "\n⏰ **Horaires:** Lundi-Vendredi, 7h30-17h30"
        
        return response
    
    def _generate_general_response(self, query: str, results: List[Dict]) -> str:
        """Génère une réponse générale"""
        if not results:
            return self._get_fallback_response("general")
        
        best_result = results[0]
        content = best_result["content"]
        
        # Si c'est une Q&A, retourne directement la réponse
        if "Réponse:" in content:
            parts = content.split("Réponse:")
            if len(parts) > 1:
                return parts[1].strip()
        
        # Sinon, formate le contenu
        response = "Voici les informations que j'ai trouvées :\n\n"
        response += content
        response += "\n\n**Pour plus de détails :**\n"
        response += "📞 +229 21 30 10 20\n"
        response += "🌐 https://andf.bj"
        
        return response
    
    def _get_fallback_response(self, intent: str) -> str:
        """Réponse de fallback selon l'intention"""
        fallback_responses = {
            "cost_inquiry": """
Je n'ai pas trouvé d'informations spécifiques sur ce tarif.

**Tarifs principaux ANDF :**
- Titre foncier : 100,000 F CFA
- Certificat d'appartenance : 50,000 F CFA
- Mutations : 0,3% de la valeur marchande

📞 **Contact :** +229 21 30 10 20
            """,
            "procedure_info": """
Je n'ai pas trouvé de procédure spécifique pour votre demande.

**Services principaux ANDF :**
- Confirmation de droits fonciers
- Certificats d'appartenance
- Mutations de titre foncier

🏢 **Contactez votre BCDF local** pour plus de détails.
            """,
            "general": """
Je n'ai pas trouvé d'informations spécifiques sur votre question.

**Pour vous aider :**
📞 Contactez votre BCDF local
📱 Appelez le +229 21 30 10 20  
🌐 Consultez https://andf.bj

**Questions fréquentes :**
- Comment obtenir un titre foncier ?
- Quel est le coût d'un certificat d'appartenance ?
- Où se trouve mon BCDF ?
            """
        }
        
        return fallback_responses.get(intent, fallback_responses["general"])
    
    def _get_error_response(self) -> str:
        """Réponse en cas d'erreur"""
        return """
⚠️ Une erreur s'est produite lors du traitement de votre demande.

**Contactez directement :**
📞 +229 21 30 10 20
🌐 https://andf.bj
📧 contact@andf.bj

Nos équipes sont disponibles du lundi au vendredi, de 7h30 à 17h30.
        """
    
    def _calculate_confidence(self, search_results: List[Dict], response: str) -> float:
        """Calcule le score de confiance de la réponse"""
        if not search_results:
            return 0.1
        
        # Score basé sur la distance sémantique du meilleur résultat
        best_distance = search_results[0]["distance"]
        
        # Convertit la distance en score de confiance (0-1)
        confidence = max(0.1, 1.0 - best_distance)
        
        # Bonus pour les réponses complètes
        if len(response) > 100:
            confidence += 0.1
        
        # Bonus pour les réponses structurées
        if "**" in response or "📞" in response:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _format_sources(self, search_results: List[Dict]) -> List[Dict[str, Any]]:
        """Formate les sources pour la réponse"""
        sources = []
        for result in search_results[:3]:  # Top 3 sources
            source = {
                "collection": result["collection"],
                "type": result["metadata"].get("type", "unknown"),
                "relevance": 1.0 - result["distance"],
                "id": result["id"]
            }
            
            # Ajout d'infos spécifiques selon le type
            if "procedure_id" in result["metadata"]:
                source["procedure"] = result["metadata"]["procedure_id"]
            if "service" in result["metadata"]:
                source["service"] = result["metadata"]["service"]
            
            sources.append(source)
        
        return sources
    
    def _save_session_history(self, session_id: str, query: str, response: str):
        """Sauvegarde l'historique de la session"""
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        
        self.session_history[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response[:200] + "..." if len(response) > 200 else response
        })
        
        # Garde seulement les 10 derniers échanges par session
        if len(self.session_history[session_id]) > 10:
            self.session_history[session_id] = self.session_history[session_id][-10:]
    
    def _update_stats(self, confidence: float):
        """Met à jour les statistiques du système"""
        self.stats["queries_processed"] += 1
        
        # Calcul de la confiance moyenne
        current_avg = self.stats["average_confidence"]
        total_queries = self.stats["queries_processed"]
        
        self.stats["average_confidence"] = (
            (current_avg * (total_queries - 1) + confidence) / total_queries
        )
    
    # Méthodes publiques pour l'API
    
    async def get_procedures(self) -> List[Dict[str, Any]]:
        """Retourne la liste des procédures disponibles"""
        procedures = []
        for proc_key, proc_data in self.knowledge_base.get("procedures_principales", {}).items():
            procedures.append({
                "id": proc_key,
                "nom": proc_data.get("nom_complet", ""),
                "cout": proc_data.get("cout_base", 0),
                "duree": proc_data.get("duree_estimee", ""),
                "description": proc_data.get("description", "")
            })
        return procedures
    
    async def get_tarifs(self) -> Dict[str, Any]:
        """Retourne les tarifs ANDF"""
        return self.knowledge_base.get("tarifs_detailles", {})
    
    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recherche dans la base de connaissances"""
        results = await self._search_all_collections(query, n_results=limit)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result["content"],
                "type": result["metadata"].get("type", "unknown"),
                "collection": result["collection"],
                "relevance": 1.0 - result["distance"]
            })
        
        return formatted_results
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du système"""
        return {
            **self.stats,
            "collections_count": len(self.collections),
            "active_sessions": len(self.session_history),
            "uptime": (datetime.now() - datetime.fromisoformat(self.stats["startup_time"])).total_seconds()
        }
    
    async def cleanup(self):
        """Nettoyage des ressources"""
        logger.info("🧹 Nettoyage des ressources RAG...")
        self.session_history.clear()
        if self.chroma_client:
            # ChromaDB se gère automatiquement
            pass
        logger.info("✅ Nettoyage terminé")