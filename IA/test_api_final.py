#!/usr/bin/env python3
"""
Script de test pour l'API finale d'extraction de coordonnées
Usage: python test_api_final.py [image_path]
"""

import requests
import json
import sys
from pathlib import Path

def test_api_extraction(image_path: str, api_url: str = "http://localhost:8000"):
    """Test l'API d'extraction avec une image"""
    
    if not Path(image_path).exists():
        print(f"❌ Fichier non trouvé: {image_path}")
        return
    
    try:
        # Test santé de l'API
        print("🔍 Vérification API...")
        health_response = requests.get(f"{api_url}/health")
        if health_response.status_code == 200:
            print("✅ API accessible")
            print(f"Services: {health_response.json()['services']}")
        else:
            print(f"❌ API non accessible: {health_response.status_code}")
            return
        
        # Test extraction
        print(f"\n📤 Upload et extraction: {Path(image_path).name}")
        
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f, 'image/jpeg')}
            response = requests.post(f"{api_url}/extract", files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Extraction réussie!")
            
            # Affichage résultats
            print(f"\n📊 Résultats pour {result['filename']}:")
            print(f"   • Coordonnées trouvées: {result['coordinate_count']}")
            
            # Coordonnées UTM
            if result['coordinates_utm']:
                print(f"   • Coordonnées UTM (EPSG:32631):")
                for i, coord in enumerate(result['coordinates_utm'][:3]):  # Max 3 premiers
                    print(f"     [{i+1}] X: {coord['x']}, Y: {coord['y']}")
            
            # Coordonnées WGS84
            if result['coordinates_wgs84']:
                print(f"   • Coordonnées WGS84 (EPSG:4326):")
                for i, coord in enumerate(result['coordinates_wgs84'][:3]):  # Max 3 premiers
                    print(f"     [{i+1}] Lat: {coord['latitude']:.6f}, Lon: {coord['longitude']:.6f}")
            
            # Superpositions spatiales
            overlays = result['spatial_overlays']
            overlays_oui = {k: v for k, v in overlays.items() if v == "OUI"}
            if overlays_oui:
                print(f"   • Superpositions détectées: {list(overlays_oui.keys())}")
            else:
                print("   • Aucune superposition spatiale détectée")
            
            # JSON complet (optionnel)
            print(f"\n💾 JSON complet sauvé dans: result_{Path(image_path).stem}.json")
            with open(f"result_{Path(image_path).stem}.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
        else:
            print(f"❌ Erreur extraction: {response.status_code}")
            print(f"Détails: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API")
        print("💡 Assurez-vous que l'API est lancée avec: uv run python main_final.py")
    except Exception as e:
        print(f"❌ Erreur test: {e}")

def test_batch_extraction(image_paths: list, api_url: str = "http://localhost:8000"):
    """Test l'extraction par lot"""
    
    print(f"\n📤 Test extraction par lot ({len(image_paths)} fichiers)")
    
    try:
        files = []
        for path in image_paths:
            if Path(path).exists():
                files.append(('files', (Path(path).name, open(path, 'rb'), 'image/jpeg')))
        
        if not files:
            print("❌ Aucun fichier valide trouvé")
            return
        
        response = requests.post(f"{api_url}/batch_extract", files=files, timeout=120)
        
        # Fermer les fichiers ouverts
        for _, (_, file_obj, _) in files:
            file_obj.close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch traité: {result['successful_extractions']}/{result['total_files']} réussis")
            
            # Sauvegarder résultats
            with open("batch_results.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print("💾 Résultats sauvés dans: batch_results.json")
            
        else:
            print(f"❌ Erreur batch: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erreur test batch: {e}")

if __name__ == "__main__":
    print("🧪 Test API Extraction Coordonnées - Hackathon IA 2025")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Usage: python test_api_final.py <image_path> [image_path2 ...]")
        print("\nExemples:")
        print("  python test_api_final.py leve9.png")
        print("  python test_api_final.py leve9.png leve24.png leve30.png")
        sys.exit(1)
    
    image_paths = sys.argv[1:]
    
    # Test simple si un seul fichier
    if len(image_paths) == 1:
        test_api_extraction(image_paths[0])
    else:
        # Test batch si plusieurs fichiers
        test_batch_extraction(image_paths)