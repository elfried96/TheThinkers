"""
Module d'amélioration des réponses avec Gemini
============================================
Utilise l'API Gemini pour améliorer la qualité et le format des réponses
"""

import os
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv
import logging
import asyncio

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Templates de prompts
PROMPT_TEMPLATES = {
    "enhancement": '''En tant qu'assistant virtuel de l'ANDF (Agence Nationale du Domaine et du Foncier) au Bénin,
reformule la réponse suivante de manière professionnelle, claire et empathique.

Contexte: {context}
Question originale: {question}

Réponse à améliorer:
{response}

Instructions:
1. Utiliser un ton professionnel mais accessible
2. Structurer clairement la réponse
3. Ajouter des formules de politesse appropriées
4. Maintenir la précision technique
5. Adapter le niveau de langage au contexte
6. Garder les émojis et la mise en forme markdown existants''',

    "error": '''Reformule ce message d'erreur de manière constructive et compréhensible pour un utilisateur:
{error_message}

Instructions:
1. Expliquer clairement le problème
2. Utiliser un langage simple
3. Suggérer des solutions si possible
4. Maintenir un ton rassurant'''
}

class GeminiEnhancer:
    def __init__(self):
        """Initialise l'enhancer avec la configuration de Gemini"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Clé API Gemini non trouvée dans les variables d'environnement")

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                "gemini-pro",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_output_tokens": 2048,
                }
            )
            logger.info("✅ Modèle Gemini initialisé avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation Gemini: {e}")
            raise

    async def enhance_response(self, original_response: str, context: Dict[str, Any]) -> str:
        """
        Améliore la réponse en utilisant Gemini
        """
        try:
            # Utilisation du template avec format
            prompt = PROMPT_TEMPLATES["enhancement"].format(
                context=context.get("intent", "général"),
                question=context.get("question", "demande d'information"),
                response=original_response
            )

            response = await self.model.generate_content(prompt)
            enhanced_text = response.text.strip()
            
            # Nettoyage et validation de la réponse
            if len(enhanced_text) > 1000:  # Limite arbitraire
                enhanced_text = enhanced_text[:997] + "..."
            
            logger.info("✅ Réponse améliorée générée avec succès")
            return enhanced_text
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'amélioration: {e}")
            return original_response

    async def format_error_message(self, error_message: str) -> str:
        """
        Améliore le format des messages d'erreur
        """
        try:
            # Utilisation du template avec format
            prompt = PROMPT_TEMPLATES["error"].format(error_message=error_message)

            response = await self.model.generate_content(prompt)
            formatted_error = response.text.strip()
            
            logger.info("✅ Message d'erreur reformulé avec succès")
            return formatted_error
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du formatage du message d'erreur: {e}")
            return error_message
