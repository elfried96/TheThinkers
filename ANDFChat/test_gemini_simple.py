#!/usr/bin/env python3
"""
Test simple de l'API Gemini pour diagnostiquer le problème
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini():
    # Chargement des variables d'environnement
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY manquante")
        return False
        
    print(f"✅ API Key trouvée: {api_key[:10]}...")
    
    try:
        # Configuration de Gemini
        genai.configure(api_key=api_key)
        
        # Test avec le nouveau modèle
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Test simple
        response = model.generate_content("Dis bonjour en français")
        print(f"✅ Test réussi: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_gemini()