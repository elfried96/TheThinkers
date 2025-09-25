#!/usr/bin/env python3
"""
Test spécifique du validateur avec détection automatique d'erreurs
"""

from coordinate_validator import CoordinateValidator

def test_automatic_correction():
    """Test de correction automatique d'erreur"""
    
    print("🧪 TEST CORRECTION AUTOMATIQUE")
    print("=" * 40)
    
    # Coordonnées avec erreur évidente
    coordinates_with_error = [
        {"x": 448005.15, "y": 703480.27, "point_id": "B1"},
        {"x": 448034.38, "y": 703180.21, "point_id": "B2"},  # ERREUR: 1 au lieu de 4
        {"x": 448034.23, "y": 703465.29, "point_id": "B3"},
        {"x": 448005.21, "y": 703465.61, "point_id": "B4"}
    ]
    
    validator = CoordinateValidator()
    
    # Validation complète avec détection d'erreurs
    validation = validator.validate_coordinates(coordinates_with_error, "leve9.png")
    
    # Afficher détails de détection
    print(f"\n🔍 DÉTECTION D'ANOMALIES:")
    if 'anomaly_detection' in validation:
        anomalies = validation['anomaly_detection']
        
        print(f"Erreurs critiques: {len(anomalies.get('critical_anomalies', []))}")
        print(f"Erreurs suspectées: {len(anomalies.get('suspected_errors', []))}")
        print(f"Avertissements: {len(anomalies.get('warnings', []))}")
        
        # Détailler erreurs suspectées
        for i, error in enumerate(anomalies.get('suspected_errors', []), 1):
            print(f"\n📍 Erreur suspectée #{i}:")
            for key, value in error.items():
                print(f"  {key}: {value}")
            
            # Test manuel de conversion en correction
            print(f"  Test conversion:")
            has_suggested_y = 'suggested_y' in error
            confidence = error.get('confidence', 0)
            threshold_met = confidence > 0.8
            print(f"    suggested_y présent: {has_suggested_y}")
            print(f"    confidence: {confidence:.3f}")
            print(f"    seuil 0.8 atteint: {threshold_met}")
    
    # Afficher corrections suggérées
    print(f"\n🔧 CORRECTIONS SUGGÉRÉES:")
    if validation.get('corrections'):
        for correction in validation['corrections']:
            print(f"Point {correction['point_id']}:")
            print(f"  Champ: {correction['field']}")
            print(f"  {correction['original_value']:.2f} → {correction['suggested_value']:.2f}")
            print(f"  Confiance: {correction['confidence']:.1%}")
            print(f"  Raison: {correction['reason']}")
    else:
        print("Aucune correction suggérée")
    
    return validation

def test_with_enhanced_detection():
    """Test avec seuils de détection plus sensibles"""
    
    print(f"\n🔬 TEST DÉTECTION AMÉLIORÉE")
    print("=" * 40)
    
    coordinates = [
        {"x": 448005.15, "y": 703480.27, "point_id": "B1"},
        {"x": 448034.38, "y": 703180.21, "point_id": "B2"},
        {"x": 448034.23, "y": 703465.29, "point_id": "B3"},
        {"x": 448005.21, "y": 703465.61, "point_id": "B4"}
    ]
    
    # Analyse manuelle pour vérifier logique
    y_coords = [c['y'] for c in coordinates]
    median_y = sorted(y_coords)[len(y_coords)//2]
    distances = [abs(y - median_y) for y in y_coords]
    
    print(f"Coordonnées Y: {y_coords}")
    print(f"Médiane Y: {median_y}")
    print(f"Distances médiane: {distances}")
    print(f"Distance max: {max(distances):.2f}m")
    print(f"Distance moyenne: {sum(distances)/len(distances):.2f}m")
    print(f"Ratio max/moyenne: {max(distances)/(sum(distances)/len(distances)):.1f}")
    
    # Identifier valeur aberrante
    aberrant_index = distances.index(max(distances))
    aberrant_value = y_coords[aberrant_index]
    
    print(f"\nValeur aberrante: Y={aberrant_value} (Point B{aberrant_index+1})")
    
    # Tester correction manuelle
    validator = CoordinateValidator()
    best_correction = validator._find_best_digit_correction(aberrant_value, y_coords, aberrant_index)
    
    if best_correction:
        print(f"\nMeilleure correction trouvée:")
        print(f"  {aberrant_value} → {best_correction['new_value']}")
        print(f"  {best_correction['reason']}")
        print(f"  Confiance: {best_correction['confidence']:.1%}")
        print(f"  Amélioration: {best_correction['improvement']:.1%}")
    else:
        print(f"\nAucune correction trouvée")

if __name__ == "__main__":
    # Test validation standard
    validation = test_automatic_correction()
    
    # Test détection améliorée
    test_with_enhanced_detection()
    
    # Résumé
    has_corrections = bool(validation.get('corrections'))
    print(f"\n🎯 RÉSULTAT:")
    print(f"Corrections détectées: {'✅' if has_corrections else '❌'}")
    
    if has_corrections:
        print("Le validateur fonctionne correctement!")
    else:
        print("Le validateur nécessite des ajustements...")