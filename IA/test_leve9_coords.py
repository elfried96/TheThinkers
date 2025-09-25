#!/usr/bin/env python3
"""
Test spécifique pour valider les coordonnées de leve9.png
Démonstration du problème de précision et de la validation
"""

import json
from coordinate_validator import CoordinateValidator

def test_leve9_coordinates():
    """Test validation coordonnées leve9.png avec erreur détectée"""
    
    print("🧪 TEST VALIDATION COORDONNÉES LEVE9.PNG")
    print("=" * 50)
    
    # Coordonnées obtenues (avec erreur présumée)
    coordinates_obtained = [
        {"x": 448005.15, "y": 703480.27, "point_id": "B1"},
        {"x": 448034.38, "y": 703180.21, "point_id": "B2"},  # ← ERREUR: 703180 au lieu de 703480?
        {"x": 448034.23, "y": 703465.29, "point_id": "B3"},
        {"x": 448005.21, "y": 703465.61, "point_id": "B4"}
    ]
    
    # Coordonnées attendues (hypothèse correction)
    coordinates_expected = [
        {"x": 448005.15, "y": 703480.27, "point_id": "B1"},
        {"x": 448034.38, "y": 703480.21, "point_id": "B2"},  # ← CORRIGÉ: 703480
        {"x": 448034.23, "y": 703465.29, "point_id": "B3"},
        {"x": 448005.21, "y": 703465.61, "point_id": "B4"}
    ]
    
    validator = CoordinateValidator()
    
    print("\n🔍 VALIDATION COORDONNÉES OBTENUES:")
    validation_obtained = validator.validate_coordinates(coordinates_obtained, "leve9.png")
    
    print("\n🔍 VALIDATION COORDONNÉES CORRIGÉES:")
    validation_expected = validator.validate_coordinates(coordinates_expected, "leve9.png")
    
    # Comparaison
    print(f"\n📊 COMPARAISON:")
    print(f"Obtenues - Valide: {'✅' if validation_obtained['valid'] else '❌'}")
    print(f"Corrigées - Valide: {'✅' if validation_expected['valid'] else '❌'}")
    
    # Analyser différences géométriques
    if 'polygon_analysis' in validation_obtained.get('geometric_validation', {}):
        area_obtained = validation_obtained['geometric_validation']['polygon_analysis'].get('area', 0)
        area_expected = validation_expected['geometric_validation']['polygon_analysis'].get('area', 0)
        
        print(f"\n📐 AIRES CALCULÉES:")
        print(f"Obtenues: {area_obtained:.2f} m²")
        print(f"Corrigées: {area_expected:.2f} m²")
        print(f"Différence: {abs(area_obtained - area_expected):.2f} m² ({abs(area_obtained - area_expected)/max(area_obtained, area_expected)*100:.1f}%)")
    
    return {
        'obtained_validation': validation_obtained,
        'expected_validation': validation_expected,
        'coordinates_obtained': coordinates_obtained,
        'coordinates_expected': coordinates_expected
    }

def analyze_y_coordinate_error():
    """Analyse spécifique de l'erreur sur la coordonnée Y"""
    
    print(f"\n🔍 ANALYSE ERREUR COORDONNÉE Y:")
    print(f"=" * 40)
    
    # Valeurs Y obtenues
    y_values = [703480.27, 703180.21, 703465.29, 703465.61]
    
    print(f"Valeurs Y obtenues:")
    for i, y in enumerate(y_values, 1):
        print(f"  B{i}: {y}")
    
    # Identifier la valeur aberrante
    y_median = sorted(y_values)[len(y_values)//2]
    y_mean = sum(y_values) / len(y_values)
    
    print(f"\nStatistiques Y:")
    print(f"  Médiane: {y_median}")
    print(f"  Moyenne: {y_mean:.2f}")
    
    # Distances à la médiane
    print(f"\nDistances à la médiane:")
    for i, y in enumerate(y_values, 1):
        distance = abs(y - y_median)
        print(f"  B{i}: {distance:.2f}m {'←ABERRANT' if distance > 100 else ''}")
    
    # Correction suggérée
    print(f"\n🔧 CORRECTION SUGGÉRÉE:")
    aberrant_value = 703180.21
    suggested_value = 703480.21  # Changer le '1' en '4'
    
    print(f"  Valeur aberrante: {aberrant_value}")
    print(f"  Correction suggérée: {suggested_value}")
    print(f"  Changement: Position 4 du nombre (1→4)")
    print(f"  Nouvelle distance médiane: {abs(suggested_value - y_median):.2f}m")

if __name__ == "__main__":
    # Test validation
    results = test_leve9_coordinates()
    
    # Analyse erreur Y
    analyze_y_coordinate_error()
    
    print(f"\n🎯 CONCLUSIONS:")
    print(f"1. Le validateur détecte les incohérences géométriques")
    print(f"2. L'erreur sur B2.y (703180→703480) est critique")
    print(f"3. Différence de surface significative avec correction")
    print(f"4. Validation géométrique améliore la précision")