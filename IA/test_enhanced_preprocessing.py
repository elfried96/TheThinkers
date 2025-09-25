#!/usr/bin/env python3
"""
Script de test pour le préprocesseur morphologique amélioré
Teste spécifiquement les corrections des confusions 0/6, 4/1, 9/0
"""

import cv2
import numpy as np
from simple_morphological_preprocessor import SimpleMorphologicalPreprocessor
import matplotlib.pyplot as plt

def test_digit_confusions():
    """Test avec une image réelle pour voir les améliorations"""
    
    # Initialiser le préprocesseur
    preprocessor = SimpleMorphologicalPreprocessor()
    
    # Charger une image de test
    test_image_path = "Data_Hackathon_IA_2025/Testing_Data/leve218.png"
    
    try:
        image = cv2.imread(test_image_path)
        if image is None:
            print(f"❌ Impossible de charger: {test_image_path}")
            return
        
        print(f"🧪 TEST PREPROCESSING AMÉLIORÉ")
        print(f"📄 Image: {test_image_path}")
        print(f"📐 Dimensions: {image.shape}")
        
        # Analyser la qualité initiale
        metrics_original = preprocessor.analyze_character_quality(image)
        print(f"\n📊 MÉTRIQUES ORIGINALES:")
        for key, value in metrics_original.items():
            print(f"  • {key}: {value:.3f}")
        
        # Appliquer le préprocessing amélioré
        enhanced = preprocessor.enhance_for_ocr(image, metrics_original['overall_difficulty'])
        
        # Analyser la qualité après enhancement
        metrics_enhanced = preprocessor.analyze_character_quality(enhanced)
        print(f"\n📊 MÉTRIQUES APRÈS ENHANCEMENT:")
        for key, value in metrics_enhanced.items():
            print(f"  • {key}: {value:.3f}")
        
        # Calculer les améliorations
        print(f"\n🎯 AMÉLIORATIONS:")
        improvements = {
            'netteté': metrics_enhanced['sharpness'] - metrics_original['sharpness'],
            'contraste': metrics_enhanced['contrast'] - metrics_original['contrast'],
            'difficulté': metrics_original['overall_difficulty'] - metrics_enhanced['overall_difficulty']
        }
        
        for key, value in improvements.items():
            symbol = "📈" if value > 0 else "📉" if value < 0 else "➡️"
            print(f"  {symbol} {key}: {value:+.3f}")
        
        # Sauvegarder les résultats pour comparaison
        cv2.imwrite("test_original.png", image)
        cv2.imwrite("test_enhanced.png", enhanced)
        
        print(f"\n✅ Images sauvées:")
        print(f"  📄 test_original.png")
        print(f"  📄 test_enhanced.png")
        
        return enhanced, metrics_enhanced
        
    except Exception as e:
        print(f"❌ Erreur durant le test: {e}")
        return None, None

def test_specific_digit_regions():
    """Test sur des régions spécifiques contenant des chiffres"""
    
    preprocessor = SimpleMorphologicalPreprocessor()
    
    # Créer une image synthétique avec des chiffres problématiques
    test_digits = create_problematic_digits()
    
    print(f"\n🔍 TEST RÉGIONS SPÉCIFIQUES")
    
    for digit_name, digit_image in test_digits.items():
        print(f"\n📄 Test digit: {digit_name}")
        
        # Analyser avant
        metrics_before = preprocessor.analyze_character_quality(digit_image)
        
        # Appliquer correction
        corrected = preprocessor._fix_character_defects(digit_image)
        
        # Analyser après
        metrics_after = preprocessor.analyze_character_quality(corrected)
        
        improvement = metrics_after['sharpness'] - metrics_before['sharpness']
        symbol = "📈" if improvement > 0 else "📉" if improvement < 0 else "➡️"
        
        print(f"  {symbol} Netteté: {improvement:+.3f}")
        
        # Sauvegarder
        cv2.imwrite(f"test_digit_{digit_name}_before.png", digit_image)
        cv2.imwrite(f"test_digit_{digit_name}_after.png", corrected)

def create_problematic_digits():
    """Crée des images synthétiques de chiffres avec défauts typiques"""
    
    digits = {}
    
    # Simuler un "0" avec ouverture qui pourrait être confondu avec "6"
    zero_img = np.ones((50, 30), dtype=np.uint8) * 255
    cv2.ellipse(zero_img, (15, 25), (10, 20), 0, 0, 360, 0, 2)
    digits['zero_defective'] = zero_img
    
    # Simuler un "4" avec trait horizontal cassé qui pourrait être confondu avec "1"
    four_img = np.ones((50, 30), dtype=np.uint8) * 255
    cv2.line(four_img, (5, 10), (5, 25), 0, 2)  # Trait vertical gauche
    cv2.line(four_img, (20, 5), (20, 45), 0, 2)  # Trait vertical droit
    cv2.line(four_img, (5, 25), (15, 25), 0, 2)  # Trait horizontal cassé
    cv2.line(four_img, (17, 25), (20, 25), 0, 2)  # Suite du trait
    digits['four_defective'] = four_img
    
    return digits

if __name__ == "__main__":
    print("🚀 LANCEMENT DES TESTS PREPROCESSING AMÉLIORÉ")
    print("=" * 60)
    
    # Test principal
    enhanced, metrics = test_digit_confusions()
    
    # Tests spécifiques
    test_specific_digit_regions()
    
    print(f"\n🏁 TESTS TERMINÉS")
    print(f"📁 Vérifiez les fichiers de sortie pour voir les améliorations")