#!/usr/bin/env python3
"""
Script de test rapide pour une image spécifique
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configuration logging pour voir les détails
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger l'environnement
load_dotenv()

# Importer les classes depuis main_final
from main_final import GeminiExtractor, ImagePreprocessor, CoordinateConverter

def test_single_extraction(image_path: str):
    """Test d'extraction sur une seule image avec debug détaillé"""
    
    print(f"🔍 Test extraction sur: {image_path}")
    print("=" * 60)
    
    if not Path(image_path).exists():
        print(f"❌ Image introuvable: {image_path}")
        return False
    
    # Vérifier la clé API
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY manquante dans .env")
        return False
    
    try:
        # Initialiser les composants
        extractor = GeminiExtractor()
        preprocessor = ImagePreprocessor()
        converter = CoordinateConverter()
        
        print("✅ Composants initialisés")
        
        # Préprocessing de l'image
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            processed_path = preprocessor.enhance_image(image_path, tmp_file.name)
        
        print(f"✅ Image préprocessée: {processed_path}")
        
        # Extraction avec Gemini
        print("🤖 Extraction Gemini en cours...")
        coordinates = extractor.extract_coordinates(processed_path)
        
        print(f"📊 Résultats extraction:")
        print(f"   Nombre de coordonnées détectées: {len(coordinates)}")
        
        if coordinates:
            print("   Coordonnées détectées:")
            for i, coord in enumerate(coordinates, 1):
                print(f"     {i}. X={coord.get('x', 'N/A')}, Y={coord.get('y', 'N/A')}")
                
                # Test conversion WGS84
                if 'x' in coord and 'y' in coord:
                    utm_zone = converter.auto_detect_utm_zone(coord['x'])
                    lat, lon = converter.convert_utm_to_wgs84(coord['x'], coord['y'], utm_zone)
                    if lat and lon:
                        print(f"        → WGS84: Lat={lat:.6f}, Lon={lon:.6f} (Zone UTM {utm_zone})")
            
            # Comparer avec les données attendues du CSV
            csv_path = "submissions_TheThinkers.csv"
            if Path(csv_path).exists():
                print(f"\n📋 Comparaison avec {csv_path}:")
                image_name = Path(image_path).name
                
                with open(csv_path, 'r') as f:
                    for line in f:
                        if image_name in line:
                            parts = line.split(',', 2)
                            if len(parts) >= 2:
                                expected_coords_str = parts[1].strip('"')
                                try:
                                    expected_coords = json.loads(expected_coords_str.replace('""', '"'))
                                    print(f"   Attendu: {len(expected_coords)} coordonnées")
                                    print(f"   Détecté: {len(coordinates)} coordonnées")
                                    
                                    if len(expected_coords) == len(coordinates):
                                        print("   ✅ Nombre correct !")
                                    else:
                                        print("   ⚠️ Nombre différent")
                                        print("   Coordonnées attendues:")
                                        for i, exp in enumerate(expected_coords, 1):
                                            print(f"     {i}. X={exp.get('x', 'N/A')}, Y={exp.get('y', 'N/A')}")
                                            
                                except json.JSONDecodeError as e:
                                    print(f"   ❌ Erreur parsing CSV: {e}")
                            break
            
        else:
            print("   ❌ Aucune coordonnée détectée")
            print("   💡 Suggestions:")
            print("     - Vérifiez que l'image contient des coordonnées numériques visibles")
            print("     - Les coordonnées doivent être au format UTM (6-7 chiffres)")
            print("     - Exemple: 427094.7, 712773.67")
        
        # Nettoyage
        try:
            os.unlink(processed_path)
        except:
            pass
        
        return len(coordinates) > 0
        
    except Exception as e:
        print(f"❌ Erreur durant l'extraction: {e}")
        import traceback
        print(f"   Détails: {traceback.format_exc()}")
        return False

def main():
    """Fonction principale"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test_single_image.py <chemin_image>")
        print("Exemple: python test_single_image.py leve3.jpg")
        return 1
    
    image_path = sys.argv[1]
    success = test_single_extraction(image_path)
    
    if success:
        print("\n🎉 Test réussi - Coordonnées détectées !")
        return 0
    else:
        print("\n💥 Test échoué - Aucune coordonnée détectée")
        return 1

if __name__ == "__main__":
    exit(main())