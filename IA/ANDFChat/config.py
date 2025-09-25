"""
Configuration centralisée pour le chatbot ANDF
"""

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration Gemini
GEMINI_CONFIG = {
    "api_key": os.getenv("GOOGLE_API_KEY"),
    "temperature": 0.7,
    "top_p": 0.9,
    "max_output_tokens": 2048,
    "model": "gemini-pro"
}

# Configuration des prompts
PROMPT_TEMPLATES = {
    "general_enhancement": """
    En tant qu'assistant virtuel de l'ANDF (Agence Nationale du Domaine et du Foncier) au Bénin,
    reformule la réponse suivante de manière professionnelle, claire et empathique.
    
    Contexte: {context}
    Question originale: {question}
    Réponse à améliorer: {response}
    
    Instructions:
    1. Utiliser un ton professionnel mais accessible
    2. Structurer clairement la réponse
    3. Ajouter des formules de politesse appropriées
    4. Maintenir la précision technique
    5. Adapter le niveau de langage au contexte
    """,

    "error_response": """
    Reformule ce message d'erreur de manière constructive et compréhensible:
    {error_message}
    
    Instructions:
    1. Expliquer clairement le problème
    2. Suggérer des solutions si possible
    3. Maintenir un ton rassurant
    4. Donner des points de contact si nécessaire
    """
}

# Configuration du système
SYSTEM_CONFIG = {
    "max_retries": 3,
    "timeout": 30,
    "default_language": "fr",
    "supported_languages": ["fr", "fon", "yoruba"],
    "max_message_length": 1000,
    "session_timeout": 3600  # 1 heure
}

# Messages d'erreur personnalisés
ERROR_MESSAGES = {
    "internal_error": "Une erreur interne s'est produite. Notre équipe technique a été notifiée.",
    "validation_error": "Les informations fournies ne sont pas valides. Veuillez vérifier et réessayer.",
    "not_found": "La ressource demandée n'a pas été trouvée.",
    "timeout": "Le délai de réponse a été dépassé. Veuillez réessayer.",
    "maintenance": "Le système est actuellement en maintenance. Veuillez réessayer plus tard."
}
