"""
Module d'amélioration des réponses avec Gemini - Version Avancée
==============================================================
Intégration moderne avec streaming, personnalisation et interaction utilisateur
"""

import os
import google.generativeai as genai
from typing import Dict, Any, Optional, AsyncGenerator, List
from dotenv import load_dotenv
import logging
import asyncio
import json
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Templates de prompts avancés
PROMPT_TEMPLATES = {
    "conversational": '''Tu es l'assistant virtuel officiel de l'ANDF (Agence Nationale du Domaine et du Foncier) du Bénin. 
Tu t'appelles "ANDF Assistant" et tu représentes l'institution avec professionnalisme et bienveillance.

Contexte de la conversation:
- Type de demande: {intent}
- Question de l'utilisateur: {question}
- Historique pertinent: {history}
- Profil utilisateur: {user_profile}

Réponse de base à améliorer:
{response}

Consignes pour améliorer la réponse:

🎯 **Personnalisation:**
- Adapte le ton selon le profil de l'utilisateur (citoyen, professionnel, fonctionnaire)
- Utilise un langage accessible mais professionnel
- Montre de l'empathie envers les préoccupations foncières

📋 **Structure de réponse:**
1. Salutation personnalisée et reconnaissance de la demande
2. Réponse claire et structurée avec points-clés
3. Informations pratiques (contacts, délais, coûts)
4. Questions de suivi suggérées
5. Formule de politesse et invitation à continuer

💡 **Enrichissement:**
- Ajoute des conseils pratiques pertinents
- Inclus les émojis appropriés pour la clarté
- Propose des actions concrètes
- Mentionne les alternatives disponibles

🔗 **Engagement utilisateur:**
- Pose une question ouverte pour encourager l'interaction
- Propose des sujets connexes qui pourraient intéresser l'utilisateur
- Inviter à préciser si des détails supplémentaires sont nécessaires

Réponds de manière naturelle, comme si tu étais en conversation directe avec l'utilisateur.''',

    "streaming_context": '''Continue cette conversation avec l'utilisateur de manière fluide et naturelle.

Contexte actuel: {context}
Dernière réponse: {last_response}
Nouvelle question: {new_question}

Instructions:
- Fais référence à la conversation précédente quand c'est pertinent
- Maintiens la cohérence du ton et du niveau de détail
- Approfondis ou précise selon la demande
- Garde l'aspect conversationnel et engageant''',

    "error_friendly": '''L'utilisateur a rencontré cette difficulté: {error_message}

Transforme cela en message d'assistance bienveillant qui:
1. Reconnaît la frustration de l'utilisateur
2. Explique simplement ce qui s'est passé
3. Propose des solutions concrètes
4. Rassure sur la disponibilité du support
5. Maintient un ton positif et encourageant

Ajoute une touche personnelle qui montre que l'ANDF se soucie de ses usagers.''',

    "follow_up": '''Basé sur cette conversation: {conversation_summary}

Génère 3-4 questions de suivi pertinentes que l'utilisateur pourrait avoir, formatées ainsi:
- Question pratique immédiate
- Question sur les étapes suivantes  
- Question sur les alternatives
- Question sur l'assistance disponible

Les questions doivent être naturelles et utiles pour progresser dans la démarche.'''
}

class EnhancedGeminiAssistant:
    def __init__(self):
        """Initialise l'assistant Gemini avancé"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY manquante dans le fichier .env")

            genai.configure(api_key=api_key)
            
            # Configuration optimisée pour la conversation
            self.model = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config={
                    "temperature": 0.8,  # Plus créatif pour un ton naturel
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 1500,  # Réponses plus substantielles
                    "stop_sequences": []
                }
            )
            
            # Configuration pour le streaming
            self.streaming_model = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_output_tokens": 1000,
                }
            )
            
            # Historique de conversation par session
            self.conversation_history = {}
            
            logger.info("✅ Assistant Gemini avancé initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation Gemini: {e}")
            self.model = None
            self.streaming_model = None

    def _extract_user_profile(self, context: Dict[str, Any]) -> str:
        """Extrait le profil utilisateur du contexte"""
        user_context = context.get('user_context', {})
        
        if user_context.get('is_professional'):
            return "professionnel du secteur foncier"
        elif user_context.get('is_first_time'):
            return "premier contact avec l'ANDF"
        elif user_context.get('has_experience'):
            return "utilisateur expérimenté des services ANDF"
        else:
            return "citoyen ordinaire"

    def _get_conversation_history(self, session_id: str) -> str:
        """Récupère l'historique de conversation"""
        if not session_id or session_id not in self.conversation_history:
            return "Première interaction"
        
        history = self.conversation_history[session_id]
        if len(history) > 3:  # Garde seulement les 3 derniers échanges
            history = history[-3:]
        
        return " | ".join([f"Q: {h['question'][:50]}... R: {h['response'][:50]}..." for h in history])

    def _update_conversation_history(self, session_id: str, question: str, response: str):
        """Met à jour l'historique de conversation"""
        if not session_id:
            return
            
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            'question': question,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limite à 10 échanges par session
        if len(self.conversation_history[session_id]) > 10:
            self.conversation_history[session_id] = self.conversation_history[session_id][-10:]

    async def enhance_response_conversational(
        self, 
        original_response: str, 
        context: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> str:
        """Améliore la réponse avec un style conversationnel"""
        
        if not self.model:
            return original_response
            
        try:
            user_profile = self._extract_user_profile(context)
            history = self._get_conversation_history(session_id)
            
            prompt = PROMPT_TEMPLATES["conversational"].format(
                intent=context.get("intent", "information générale"),
                question=context.get("question", "demande non spécifiée"),
                history=history,
                user_profile=user_profile,
                response=original_response
            )

            response = self.model.generate_content(prompt)
            enhanced_text = response.text.strip()
            
            # Mise à jour de l'historique
            if session_id:
                self._update_conversation_history(
                    session_id, 
                    context.get("question", ""), 
                    enhanced_text[:200]
                )
            
            logger.info("✅ Réponse conversationnelle générée")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"❌ Erreur amélioration conversationnelle: {e}")
            return original_response

    async def generate_streaming_response(
        self, 
        query: str, 
        context: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Génère une réponse en streaming"""
        
        if not self.streaming_model:
            yield "Service de streaming non disponible temporairement."
            return
            
        try:
            user_profile = self._extract_user_profile(context)
            history = self._get_conversation_history(session_id)
            
            prompt = f"""En tant qu'assistant ANDF, réponds à cette question de manière conversationnelle:

Question: {query}
Profil utilisateur: {user_profile}
Historique: {history}
Contexte: {context.get('intent', 'général')}

Réponds naturellement, comme dans une conversation en face à face."""

            # Simulation du streaming (Gemini Pro ne supporte pas le streaming natif)
            response = self.streaming_model.generate_content(prompt)
            full_response = response.text
            
            # Simulation du streaming par chunks
            words = full_response.split()
            current_chunk = ""
            
            for i, word in enumerate(words):
                current_chunk += word + " "
                
                # Envoie un chunk tous les 3-5 mots
                if (i + 1) % 4 == 0 or i == len(words) - 1:
                    yield current_chunk.strip()
                    current_chunk = ""
                    await asyncio.sleep(0.1)  # Délai pour simuler le streaming
                    
        except Exception as e:
            logger.error(f"❌ Erreur streaming: {e}")
            yield f"Désolé, je rencontre des difficultés techniques. Contactez le support ANDF au +229 21 30 10 20."

    async def generate_follow_up_questions(
        self, 
        conversation_context: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> List[str]:
        """Génère des questions de suivi pertinentes"""
        
        if not self.model:
            return [
                "Avez-vous d'autres questions sur cette procédure ?",
                "Souhaitez-vous connaître les coûts associés ?",
                "Avez-vous besoin d'aide pour localiser votre BCDF ?"
            ]
            
        try:
            history = self._get_conversation_history(session_id)
            conversation_summary = f"Intent: {conversation_context.get('intent')}, Historique: {history}"
            
            prompt = PROMPT_TEMPLATES["follow_up"].format(
                conversation_summary=conversation_summary
            )
            
            response = self.model.generate_content(prompt)
            
            # Parse la réponse pour extraire les questions
            questions_text = response.text.strip()
            questions = []
            
            for line in questions_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    question = line[1:].strip()
                    if question:
                        questions.append(question)
                        
            return questions[:4] if questions else [
                "Avez-vous besoin de précisions supplémentaires ?",
                "Y a-t-il d'autres aspects qui vous préoccupent ?",
                "Souhaitez-vous que je vous aide avec autre chose ?"
            ]
            
        except Exception as e:
            logger.error(f"❌ Erreur génération questions: {e}")
            return ["Avez-vous d'autres questions ?"]

    async def create_friendly_error_message(self, error_message: str, context: Dict[str, Any]) -> str:
        """Crée un message d'erreur amical et utile"""
        
        if not self.model:
            return f"Nous rencontrons quelques difficultés techniques. Veuillez réessayer ou contacter notre support au +229 21 30 10 20. Erreur: {error_message}"
            
        try:
            prompt = PROMPT_TEMPLATES["error_friendly"].format(
                error_message=error_message
            )
            
            response = self.model.generate_content(prompt)
            friendly_message = response.text.strip()
            
            logger.info("✅ Message d'erreur amélioré")
            return friendly_message
            
        except Exception as e:
            logger.error(f"❌ Erreur formatage erreur: {e}")
            return f"Nous nous excusons pour ce désagrément technique. Notre équipe travaille à résoudre le problème. En attendant, vous pouvez nous contacter au +229 21 30 10 20 pour une assistance immédiate."

    def get_conversation_stats(self, session_id: str) -> Dict[str, Any]:
        """Retourne les statistiques de conversation pour une session"""
        if session_id not in self.conversation_history:
            return {"total_exchanges": 0, "session_start": None}
            
        history = self.conversation_history[session_id]
        return {
            "total_exchanges": len(history),
            "session_start": history[0]["timestamp"] if history else None,
            "last_interaction": history[-1]["timestamp"] if history else None,
            "topics_discussed": len(set(h.get("intent", "général") for h in history))
        }

    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Nettoie les anciennes sessions de conversation"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        sessions_to_remove = []
        for session_id, history in self.conversation_history.items():
            if history and len(history) > 0:
                last_interaction = datetime.fromisoformat(history[-1]["timestamp"]).timestamp()
                if last_interaction < cutoff_time:
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.conversation_history[session_id]
            
        logger.info(f"🧹 Nettoyage: {len(sessions_to_remove)} sessions supprimées")