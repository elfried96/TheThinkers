#!/usr/bin/env python3
"""
Test simple de l'API Gemini pour vérifier la connectivité
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_gemini_connectivity():
    """Test basique de l'API Gemini"""
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY manquante dans .env")
        return False
    
    # URLs à tester (basé sur les modèles disponibles)
    test_urls = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-002:generateContent?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    ]
    
    # Test payload simple
    test_payload = {
        "contents": [{
            "parts": [{"text": "Dis simplement 'API fonctionne'"}]
        }],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 10
        }
    }
    
    for i, url in enumerate(test_urls, 1):
        print(f"🔍 Test API {i}/{len(test_urls)}: {url.split('models/')[1].split(':')[0]}")
        
        try:
            response = requests.post(
                url,
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"✅ Modèle {i} fonctionne !")
                
                # Afficher la réponse
                try:
                    data = response.json()
                    text_response = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    print(f"   Réponse: {text_response.strip()}")
                except:
                    print("   Réponse reçue mais format inattendu")
                    
                return url  # Retourner l'URL qui fonctionne
                
            else:
                print(f"❌ Modèle {i} échoué: {response.status_code}")
                if response.status_code == 404:
                    print("   → Modèle non trouvé ou accès refusé")
                elif response.status_code == 403:
                    print("   → Clé API invalide ou quotas dépassés")
                else:
                    print(f"   → Erreur: {response.text[:100]}")
        
        except requests.exceptions.Timeout:
            print(f"⏰ Modèle {i} timeout")
        except requests.exceptions.RequestException as e:
            print(f"🌐 Modèle {i} erreur réseau: {e}")
        except Exception as e:
            print(f"💥 Modèle {i} erreur: {e}")
    
    print("❌ Aucun modèle Gemini accessible")
    return False

def test_list_models():
    """Liste les modèles Gemini disponibles"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return
    
    print("\n🔍 Liste des modèles disponibles:")
    
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(list_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"   Modèles trouvés: {len(models)}")
            for model in models:
                name = model.get('name', '').replace('models/', '')
                print(f"   - {name}")
        else:
            print(f"   Erreur listage: {response.status_code}")
    except Exception as e:
        print(f"   Erreur: {e}")

def main():
    print("🧪 Test de connectivité API Gemini")
    print("=" * 50)
    
    working_url = test_gemini_connectivity()
    
    if working_url:
        print(f"\n✅ API Gemini opérationnelle !")
        print(f"   URL recommandée: {working_url.split('?')[0]}")
    else:
        print(f"\n💥 Problème avec l'API Gemini")
        print("💡 Suggestions:")
        print("   1. Vérifiez votre GOOGLE_API_KEY dans .env")
        print("   2. Vérifiez que l'API Generative Language est activée")
        print("   3. Vérifiez vos quotas Google Cloud")
        
        # Tenter de lister les modèles disponibles
        test_list_models()

if __name__ == "__main__":
    main()