#!/usr/bin/env python3
"""
Debug avancé pour comprendre pourquoi Gemini invente des coordonnées
"""

import os
import json
import tempfile
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configuration logging détaillé
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Importer les classes
from main_final import GeminiExtractor, ImagePreprocessor

def debug_extraction_detailed(image_path: str):
    """Debug détaillé de l'extraction"""
    
    print(f"🔍 DEBUG EXTRACTION: {image_path}")
    print("=" * 80)
    
    if not Path(image_path).exists():
        print(f"❌ Image introuvable: {image_path}")
        return
    
    try:
        extractor = GeminiExtractor()
        preprocessor = ImagePreprocessor()
        
        print("📋 Coordonnées attendues selon CSV:")
        expected_coords = [
            {"x": 427094.7, "y": 712773.67},
            {"x": 427110.61, "y": 712767.66}, 
            {"x": 427103.58, "y": 712748.94},
            {"x": 427099.06, "y": 712746.69},
            {"x": 427084.21, "y": 712750.65}
        ]
        for i, coord in enumerate(expected_coords, 1):
            print(f"   {i}. X={coord['x']}, Y={coord['y']}")
        
        print(f"\n🖼️ Test 1: Extraction SANS préprocessing")
        print("-" * 50)
        
        # Test sans preprocessing
        coords_original = extractor.extract_coordinates(image_path)
        print(f"Résultat: {len(coords_original)} coordonnées détectées")
        for i, coord in enumerate(coords_original, 1):
            print(f"   {i}. X={coord.get('x', 'N/A')}, Y={coord.get('y', 'N/A')}")
        
        print(f"\n🔧 Test 2: Extraction AVEC préprocessing")
        print("-" * 50)
        
        # Test avec preprocessing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            processed_path = preprocessor.enhance_image(image_path, tmp_file.name)
            print(f"Image préprocessée sauvée: {processed_path}")
        
        coords_processed = extractor.extract_coordinates(processed_path)
        print(f"Résultat: {len(coords_processed)} coordonnées détectées")
        for i, coord in enumerate(coords_processed, 1):
            print(f"   {i}. X={coord.get('x', 'N/A')}, Y={coord.get('y', 'N/A')}")
        
        # Analyser les différences
        print(f"\n📊 ANALYSE DES DIFFÉRENCES")
        print("-" * 50)
        print(f"Sans preprocessing: {len(coords_original)} coordonnées")
        print(f"Avec preprocessing: {len(coords_processed)} coordonnées")
        print(f"Attendu (CSV): {len(expected_coords)} coordonnées")
        
        # Vérifier quelles coordonnées sont exactes
        print(f"\n✅ VÉRIFICATION PRÉCISION")
        print("-" * 50)
        
        def check_accuracy(detected, expected, label):
            print(f"{label}:")
            exact_matches = 0
            for exp in expected:
                found = False
                for det in detected:
                    if (abs(float(det.get('x', 0)) - exp['x']) < 0.1 and 
                        abs(float(det.get('y', 0)) - exp['y']) < 0.1):
                        found = True
                        exact_matches += 1
                        break
                if found:
                    print(f"   ✅ {exp['x']}, {exp['y']} - TROUVÉ")
                else:
                    print(f"   ❌ {exp['x']}, {exp['y']} - MANQUANT")
            
            # Coordonnées supplémentaires (fausses)
            extra_coords = []
            for det in detected:
                found = False
                for exp in expected:
                    if (abs(float(det.get('x', 0)) - exp['x']) < 0.1 and 
                        abs(float(det.get('y', 0)) - exp['y']) < 0.1):
                        found = True
                        break
                if not found:
                    extra_coords.append(det)
            
            if extra_coords:
                print(f"   ⚠️ COORDONNÉES SUPPLÉMENTAIRES (fausses):")
                for coord in extra_coords:
                    print(f"      X={coord.get('x', 'N/A')}, Y={coord.get('y', 'N/A')}")
            
            accuracy = (exact_matches / len(expected)) * 100 if expected else 0
            print(f"   📈 Précision: {exact_matches}/{len(expected)} ({accuracy:.1f}%)")
            return accuracy
        
        acc_original = check_accuracy(coords_original, expected_coords, "SANS preprocessing")
        acc_processed = check_accuracy(coords_processed, expected_coords, "AVEC preprocessing")
        
        print(f"\n🎯 CONCLUSION")
        print("-" * 50)
        if acc_original > acc_processed:
            print("✅ L'image ORIGINALE donne de meilleurs résultats")
            print("💡 Le préprocessing semble DÉGRADER l'extraction")
        elif acc_processed > acc_original:
            print("✅ Le PREPROCESSING améliore l'extraction")
        else:
            print("⚖️ Pas de différence significative")
        
        # Nettoyage
        try:
            os.unlink(processed_path)
        except:
            pass
            
    except Exception as e:
        print(f"❌ Erreur durant le debug: {e}")
        import traceback
        print(traceback.format_exc())

def main():
    """Fonction principale"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python debug_extraction.py <chemin_image>")
        return 1
    
    image_path = sys.argv[1]
    debug_extraction_detailed(image_path)
    return 0

if __name__ == "__main__":
    exit(main())