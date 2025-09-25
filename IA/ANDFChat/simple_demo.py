"""
Démonstration simplifiée du chatbot ANDF
========================================
Version allégée pour tester l'interface sans dépendances ML lourdes
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleANDFChatbot:
    """Version simplifiée du chatbot ANDF pour démonstration"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.qa_dataset = {}
        self.session_history = {}
        self.stats = {
            "queries_processed": 0,
            "startup_time": datetime.now().isoformat()
        }
        self.load_data()
    
    def load_data(self):
        """Charge les données depuis les fichiers JSON"""
        try:
            # Chargement de la knowledge base
            with open("./data/andf_knowledge_base.json", "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
            
            # Chargement du dataset Q&A
            with open("./data/training_qa_dataset.json", "r", encoding="utf-8") as f:
                self.qa_dataset = json.load(f)
            
            logger.info("✅ Données chargées avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement données: {e}")
            raise e
    
    def analyze_intent(self, query: str) -> str:
        """Analyse simple de l'intention basée sur des mots-clés"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["combien", "coût", "prix", "tarif", "frais"]):
            return "cost_inquiry"
        elif any(word in query_lower for word in ["comment", "procédure", "étapes", "démarche"]):
            return "procedure_info"
        elif any(word in query_lower for word in ["où", "adresse", "localisation", "bcdf"]):
            return "location_info"
        elif any(word in query_lower for word in ["documents", "pièces", "requis", "fournir"]):
            return "document_required"
        elif any(word in query_lower for word in ["problème", "conflit", "aide", "solution"]):
            return "problem_solving"
        else:
            return "general"
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extraction simple d'entités"""
        entities = {
            "procedures": [],
            "communes": [],
            "services": []
        }
        
        query_lower = query.lower()
        
        # Procédures
        procedures = ["titre foncier", "certificat d'appartenance", "mutation", "morcellement"]
        entities["procedures"] = [proc for proc in procedures if proc in query_lower]
        
        # Communes
        communes = ["cotonou", "porto-novo", "parakou", "abomey-calavi"]
        entities["communes"] = [commune for commune in communes if commune in query_lower]
        
        return entities
    
    def search_qa_dataset(self, query: str) -> Optional[Dict]:
        """Recherche simple dans le dataset Q&A"""
        query_lower = query.lower()
        
        # Recherche par mots-clés dans les questions
        qa_pairs = self.qa_dataset.get("training_dataset", {}).get("qa_pairs", [])
        
        best_match = None
        best_score = 0
        
        for qa in qa_pairs:
            question = qa.get("question", "").lower()
            
            # Score simple basé sur les mots communs
            common_words = set(query_lower.split()) & set(question.split())
            score = len(common_words)
            
            if score > best_score:
                best_score = score
                best_match = qa
        
        return best_match if best_score > 1 else None
    
    def generate_cost_response(self, query: str, entities: Dict) -> str:
        """Génère une réponse pour les questions de coût"""
        tarifs = self.knowledge_base.get("tarifs_detailles", {})
        
        response = "💰 **Informations tarifaires ANDF**\n\n"
        
        if "titre foncier" in query.lower():
            frais = tarifs.get("frais_etablissement", {})
            titre_cost = frais.get("titre_foncier_standard", 100000)
            response += f"**Titre foncier :** {titre_cost:,} F CFA\n"
            response += "- Durée : 120 jours\n"
            response += "- Plus frais de bornage contradictoire\n\n"
        
        if "certificat" in query.lower():
            frais = tarifs.get("frais_etablissement", {})
            cert_cost = frais.get("certificat_appartenance", 50000)
            response += f"**Certificat d'appartenance :** {cert_cost:,} F CFA\n"
            response += "- Validité : 1 an non renouvelable\n\n"
        
        if "mutation" in query.lower():
            frais = tarifs.get("frais_transactions", {})
            mutation_rate = frais.get("mutations", "0.3% valeur marchande")
            response += f"**Mutations :** {mutation_rate}\n\n"
        
        response += "📞 **Contact :** +229 21 30 10 20\n"
        response += "🌐 **Site :** https://andf.bj"
        
        return response
    
    def generate_procedure_response(self, query: str, entities: Dict) -> str:
        """Génère une réponse pour les procédures"""
        procedures = self.knowledge_base.get("procedures_principales", {})
        
        response = "📋 **Procédure ANDF**\n\n"
        
        if "titre foncier" in query.lower():
            proc = procedures.get("titre_foncier", {})
            
            response += f"**{proc.get('nom_complet', 'Titre foncier')}**\n\n"
            response += f"💰 **Coût :** {proc.get('cout_base', 100000):,} F CFA\n"
            response += f"⏱️ **Durée :** {proc.get('duree_estimee', '120 jours')}\n\n"
            
            if "etapes_procedure" in proc:
                response += "**🔄 Étapes principales :**\n"
                for etape in proc["etapes_procedure"][:3]:  # Affiche les 3 premières étapes
                    nom = etape.get("nom", "")
                    description = etape.get("description", "")
                    response += f"{etape.get('ordre', '')}. **{nom}** : {description}\n"
        
        response += "\n**🏢 Service compétent :** BCDF de votre commune"
        return response
    
    def generate_location_response(self, query: str, entities: Dict) -> str:
        """Génère une réponse pour les questions de localisation"""
        response = "📍 **Informations BCDF**\n\n"
        
        # Informations des principaux BCDF
        bcdf_info = {
            "cotonou": {
                "adresse": "Quartier Gbégamey, Cotonou",
                "telephone": "+229 21 30 10 20",
                "departement": "Littoral"
            },
            "porto-novo": {
                "adresse": "Centre-ville, Porto-Novo",
                "telephone": "+229 20 21 22 23",
                "departement": "Ouémé"
            },
            "parakou": {
                "adresse": "Centre administratif, Parakou",
                "telephone": "+229 23 61 03 04",
                "departement": "Borgou"
            }
        }
        
        commune_found = False
        for commune in entities.get("communes", []):
            if commune in bcdf_info:
                info = bcdf_info[commune]
                response += f"**BCDF de {commune.title()}**\n"
                response += f"📍 **Adresse :** {info['adresse']}\n"
                response += f"📞 **Téléphone :** {info['telephone']}\n"
                response += f"🗺️ **Département :** {info['departement']}\n\n"
                commune_found = True
                break
        
        if not commune_found:
            response += "**Principaux BCDF :**\n\n"
            for commune, info in bcdf_info.items():
                response += f"**{commune.title()} :** {info['telephone']}\n"
        
        response += "\n⏰ **Horaires :** Lundi-Vendredi, 7h30-17h30"
        return response
    
    def generate_fallback_response(self, intent: str) -> str:
        """Réponse par défaut selon l'intention"""
        fallbacks = {
            "cost_inquiry": """
💰 **Tarifs principaux ANDF :**
- Titre foncier : 100,000 F CFA
- Certificat d'appartenance : 50,000 F CFA  
- Mutations : 0,3% de la valeur marchande

📞 **Contact :** +229 21 30 10 20
            """,
            "procedure_info": """
📋 **Services ANDF principaux :**
- Confirmation de droits fonciers (Titre foncier)
- Certificats d'appartenance
- Mutations de titre foncier
- Morcelements

🏢 **Contactez votre BCDF local** pour les détails.
            """,
            "general": """
Bonjour ! Je suis l'assistant virtuel de l'ANDF.

**Je peux vous aider avec :**
- Les procédures foncières
- Les tarifs et coûts
- La localisation des BCDF
- Les documents requis

**Questions populaires :**
- Comment obtenir un titre foncier ?
- Combien coûte un certificat d'appartenance ?
- Où se trouve mon BCDF ?

📞 **Contact direct :** +229 21 30 10 20
            """
        }
        
        return fallbacks.get(intent, fallbacks["general"])
    
    def chat(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Interface principale du chatbot"""
        try:
            # Génération d'un ID de session
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Analyse de la requête
            intent = self.analyze_intent(query)
            entities = self.extract_entities(query)
            
            # Recherche dans le dataset Q&A
            qa_match = self.search_qa_dataset(query)
            
            # Génération de la réponse
            if qa_match:
                # Utilise la réponse du dataset Q&A
                response = qa_match["answer"]
                confidence = 0.8
            else:
                # Génère une réponse basée sur l'intention
                if intent == "cost_inquiry":
                    response = self.generate_cost_response(query, entities)
                    confidence = 0.7
                elif intent == "procedure_info":
                    response = self.generate_procedure_response(query, entities)
                    confidence = 0.7
                elif intent == "location_info":
                    response = self.generate_location_response(query, entities)
                    confidence = 0.7
                else:
                    response = self.generate_fallback_response(intent)
                    confidence = 0.5
            
            # Mise à jour des statistiques
            self.stats["queries_processed"] += 1
            
            # Sauvegarde de l'historique
            if session_id not in self.session_history:
                self.session_history[session_id] = []
            
            self.session_history[session_id].append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response[:100] + "..." if len(response) > 100 else response
            })
            
            return {
                "response": response,
                "session_id": session_id,
                "confidence": confidence,
                "sources": [{"type": "qa_dataset" if qa_match else "rule_based"}],
                "metadata": {
                    "intent": intent,
                    "entities": entities,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement: {e}")
            
            return {
                "response": "⚠️ Une erreur s'est produite. Contactez l'ANDF au +229 21 30 10 20",
                "session_id": session_id or str(uuid.uuid4()),
                "confidence": 0.0,
                "sources": [],
                "metadata": {"error": str(e)}
            }

def demo_conversation():
    """Démonstration d'une conversation avec le chatbot"""
    print("🇧🇯 DÉMONSTRATION CHATBOT ANDF BÉNIN")
    print("=" * 50)
    
    # Initialisation du chatbot
    bot = SimpleANDFChatbot()
    
    # Questions de démonstration
    demo_questions = [
        "Bonjour, comment ça va ?",
        "Comment obtenir un titre foncier ?",
        "Combien coûte un certificat d'appartenance ?",
        "Où se trouve le BCDF de Cotonou ?",
        "Quels documents faut-il pour une mutation ?",
        "J'ai un problème avec mon terrain"
    ]
    
    session_id = "demo_session"
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{i}. 👤 **UTILISATEUR:** {question}")
        print("🤖 **ANDF CHATBOT:**")
        print("-" * 40)
        
        result = bot.chat(question, session_id)
        print(result["response"])
        print(f"\n🎯 Confiance: {result['confidence']:.1f} | Intention: {result['metadata']['intent']}")
        print("-" * 40)
    
    # Mode interactif
    print(f"\n📊 **STATISTIQUES:** {bot.stats['queries_processed']} requêtes traitées")
    print("\n💬 **MODE INTERACTIF**")
    print("Tapez vos questions (ou 'quit' pour sortir):")
    
    while True:
        try:
            user_input = input("\n👤 Votre question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'sortir', 'q']:
                print("👋 Au revoir ! Contactez l'ANDF pour plus d'informations.")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 **ANDF CHATBOT:**")
            print("-" * 40)
            
            result = bot.chat(user_input)
            print(result["response"])
            print(f"\n🎯 Confiance: {result['confidence']:.1f}")
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

def test_basic_functionality():
    """Test rapide des fonctionnalités de base"""
    print("⚡ TEST RAPIDE DU CHATBOT ANDF")
    print("=" * 40)
    
    try:
        bot = SimpleANDFChatbot()
        
        # Test de base
        result = bot.chat("Comment obtenir un titre foncier ?")
        print(f"✅ Question traitée")
        print(f"✅ Réponse: {len(result['response'])} caractères")
        print(f"✅ Confiance: {result['confidence']:.2f}")
        
        # Test des données
        print(f"✅ Knowledge base chargée: {len(bot.knowledge_base)} sections")
        print(f"✅ Dataset Q&A: {len(bot.qa_dataset.get('training_dataset', {}).get('qa_pairs', []))} paires")
        
        print("\n🎉 Test rapide réussi !")
        
    except Exception as e:
        print(f"❌ Test échoué: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_basic_functionality()
        elif sys.argv[1] == "demo":
            demo_conversation()
    else:
        # Mode par défaut: démonstration
        demo_conversation()