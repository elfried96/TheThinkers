#!/usr/bin/env python3
"""
Module de validation géométrique pour coordonnées cadastrales
Détecte les erreurs de précision et incohérences géométriques
"""

import math
import json
from typing import Dict, List, Tuple, Any
from pathlib import Path
import cv2
import numpy as np

class CoordinateValidator:
    """Validateur géométrique pour coordonnées cadastrales"""
    
    def __init__(self):
        """Initialise le validateur"""
        
        self.utm_bounds = {
            'x_min': 200000, 'x_max': 600000,
            'y_min': 600000, 'y_max': 1400000
        }
        
        # Seuils de validation
        self.max_distance_between_points = 1000  # 1km max entre points
        self.min_distance_between_points = 1     # 1m min entre points
        self.max_polygon_area = 1000000          # 1km² max
        self.min_polygon_area = 1                # 1m² min
        
        print("🔍 VALIDATEUR COORDONNÉES INITIALISÉ")
        print("📐 Validation géométrique, cohérence spatiale")
    
    def validate_coordinates(self, coordinates: List[Dict], image_path: str = None) -> Dict[str, Any]:
        """
        Validation complète des coordonnées extraites
        
        Args:
            coordinates: Liste des coordonnées à valider
            image_path: Chemin image source (optionnel)
            
        Returns:
            Résultat validation avec erreurs détectées
        """
        
        print(f"\n🔍 VALIDATION COORDONNÉES")
        print(f"📍 {len(coordinates)} points à valider")
        
        validation_result = {
            'valid': True,
            'coordinates_count': len(coordinates),
            'errors': [],
            'warnings': [],
            'corrections': [],
            'statistics': {},
            'geometric_analysis': {}
        }
        
        if not coordinates:
            validation_result['valid'] = False
            validation_result['errors'].append("Aucune coordonnée à valider")
            return validation_result
        
        # 1. Validation UTM de base
        utm_validation = self._validate_utm_bounds(coordinates)
        validation_result['utm_validation'] = utm_validation
        
        if not utm_validation['all_valid']:
            validation_result['errors'].extend(utm_validation['errors'])
            validation_result['valid'] = False
        
        # 2. Validation géométrique
        geo_validation = self._validate_geometry(coordinates)
        validation_result['geometric_validation'] = geo_validation
        
        if geo_validation['errors']:
            validation_result['errors'].extend(geo_validation['errors'])
            # Pas forcément invalide si juste des warnings géométriques
        
        validation_result['warnings'].extend(geo_validation['warnings'])
        
        # 3. Détection anomalies de position
        anomaly_detection = self._detect_position_anomalies(coordinates)
        validation_result['anomaly_detection'] = anomaly_detection
        
        if anomaly_detection['critical_anomalies']:
            validation_result['errors'].extend(anomaly_detection['critical_anomalies'])
            validation_result['valid'] = False
        
        validation_result['warnings'].extend(anomaly_detection['warnings'])
        
        # 4. Suggestions de correction
        corrections = self._suggest_corrections(coordinates, validation_result)
        validation_result['corrections'] = corrections
        
        # Marquer comme ayant des corrections potentielles si applicable
        if corrections:
            validation_result['has_corrections'] = True
        
        # 5. Statistiques finales
        validation_result['statistics'] = self._calculate_statistics(coordinates)
        
        # Afficher résumé
        self._print_validation_summary(validation_result)
        
        return validation_result
    
    def _validate_utm_bounds(self, coordinates: List[Dict]) -> Dict[str, Any]:
        """Valide les limites UTM"""
        
        utm_result = {
            'all_valid': True,
            'valid_count': 0,
            'invalid_coordinates': [],
            'errors': []
        }
        
        for i, coord in enumerate(coordinates):
            x, y = coord['x'], coord['y']
            
            valid_x = self.utm_bounds['x_min'] <= x <= self.utm_bounds['x_max']
            valid_y = self.utm_bounds['y_min'] <= y <= self.utm_bounds['y_max']
            
            if valid_x and valid_y:
                utm_result['valid_count'] += 1
            else:
                utm_result['all_valid'] = False
                utm_result['invalid_coordinates'].append({
                    'index': i,
                    'point_id': coord.get('point_id', f'Point_{i+1}'),
                    'x': x,
                    'y': y,
                    'x_valid': valid_x,
                    'y_valid': valid_y
                })
                
                error_msg = f"Point {coord.get('point_id', i+1)}: Coordonnées hors limites UTM 31N Bénin"
                if not valid_x:
                    error_msg += f" (X={x:.2f} hors [{self.utm_bounds['x_min']}-{self.utm_bounds['x_max']}])"
                if not valid_y:
                    error_msg += f" (Y={y:.2f} hors [{self.utm_bounds['y_min']}-{self.utm_bounds['y_max']}])"
                
                utm_result['errors'].append(error_msg)
        
        return utm_result
    
    def _validate_geometry(self, coordinates: List[Dict]) -> Dict[str, Any]:
        """Validation géométrique (distances, angles, surface)"""
        
        geo_result = {
            'errors': [],
            'warnings': [],
            'polygon_analysis': {},
            'distance_analysis': {},
            'angle_analysis': {}
        }
        
        if len(coordinates) < 2:
            geo_result['warnings'].append("Moins de 2 points - validation géométrique limitée")
            return geo_result
        
        # Calculer distances entre points
        distances = []
        distance_pairs = []
        
        for i in range(len(coordinates)):
            for j in range(i+1, len(coordinates)):
                coord1, coord2 = coordinates[i], coordinates[j]
                dist = math.sqrt((coord1['x'] - coord2['x'])**2 + (coord1['y'] - coord2['y'])**2)
                
                distances.append(dist)
                distance_pairs.append({
                    'point1': coord1.get('point_id', f'Point_{i+1}'),
                    'point2': coord2.get('point_id', f'Point_{j+1}'),
                    'distance': dist
                })
        
        # Analyser distances
        if distances:
            min_dist = min(distances)
            max_dist = max(distances)
            avg_dist = sum(distances) / len(distances)
            
            geo_result['distance_analysis'] = {
                'min_distance': min_dist,
                'max_distance': max_dist,
                'average_distance': avg_dist,
                'all_distances': distance_pairs
            }
            
            # Vérifications distances
            if min_dist < self.min_distance_between_points:
                geo_result['errors'].append(f"Points trop proches: distance min={min_dist:.2f}m < {self.min_distance_between_points}m")
            
            if max_dist > self.max_distance_between_points:
                geo_result['warnings'].append(f"Points très éloignés: distance max={max_dist:.2f}m > {self.max_distance_between_points}m")
            
            # Détecter points identiques/quasi-identiques
            for pair in distance_pairs:
                if pair['distance'] < 0.1:  # 10cm
                    geo_result['warnings'].append(f"Points quasi-identiques: {pair['point1']} et {pair['point2']} (distance: {pair['distance']:.3f}m)")
        
        # Analyse polygonale si 3+ points
        if len(coordinates) >= 3:
            polygon_analysis = self._analyze_polygon(coordinates)
            geo_result['polygon_analysis'] = polygon_analysis
            
            if polygon_analysis.get('area', 0) > self.max_polygon_area:
                geo_result['warnings'].append(f"Polygone très grand: {polygon_analysis['area']:.2f}m² > {self.max_polygon_area}m²")
            
            if polygon_analysis.get('area', 0) < self.min_polygon_area:
                geo_result['errors'].append(f"Polygone trop petit: {polygon_analysis['area']:.2f}m² < {self.min_polygon_area}m²")
        
        return geo_result
    
    def _analyze_polygon(self, coordinates: List[Dict]) -> Dict[str, Any]:
        """Analyse géométrique du polygone formé"""
        
        if len(coordinates) < 3:
            return {'area': 0, 'perimeter': 0, 'centroid': None}
        
        # Calculer aire par formule du shoelace
        points = [(coord['x'], coord['y']) for coord in coordinates]
        n = len(points)
        
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        area = abs(area) / 2
        
        # Calculer périmètre
        perimeter = 0
        for i in range(n):
            j = (i + 1) % n
            dist = math.sqrt((points[i][0] - points[j][0])**2 + (points[i][1] - points[j][1])**2)
            perimeter += dist
        
        # Calculer centroïde
        cx = sum(p[0] for p in points) / n
        cy = sum(p[1] for p in points) / n
        
        return {
            'area': area,
            'perimeter': perimeter,
            'centroid': {'x': cx, 'y': cy},
            'point_count': n,
            'is_clockwise': self._is_clockwise(points)
        }
    
    def _is_clockwise(self, points: List[Tuple[float, float]]) -> bool:
        """Détermine si les points sont dans le sens horaire"""
        total = 0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            total += (points[j][0] - points[i][0]) * (points[j][1] + points[i][1])
        return total > 0
    
    def _detect_position_anomalies(self, coordinates: List[Dict]) -> Dict[str, Any]:
        """Détecte les anomalies de position (erreurs probables)"""
        
        anomaly_result = {
            'critical_anomalies': [],
            'warnings': [],
            'suspected_errors': [],
            'geometric_inconsistencies': []
        }
        
        if len(coordinates) < 3:
            return anomaly_result
        
        # Analyser pattern spatial
        x_coords = [c['x'] for c in coordinates]
        y_coords = [c['y'] for c in coordinates]
        
        # Détecter valeurs aberrantes (outliers)
        x_median = sorted(x_coords)[len(x_coords)//2]
        y_median = sorted(y_coords)[len(y_coords)//2]
        
        x_distances = [abs(x - x_median) for x in x_coords]
        y_distances = [abs(y - y_median) for y in y_coords]
        
        x_threshold = sorted(x_distances)[-1] if len(x_distances) > 2 else 1000  # Distance max
        y_threshold = sorted(y_distances)[-1] if len(y_distances) > 2 else 1000
        
        # Détecter si un point est très éloigné des autres
        for i, coord in enumerate(coordinates):
            x_dist = abs(coord['x'] - x_median)
            y_dist = abs(coord['y'] - y_median)
            
            if x_dist > x_threshold * 2 or y_dist > y_threshold * 2:
                anomaly_result['suspected_errors'].append({
                    'point_id': coord.get('point_id', f'Point_{i+1}'),
                    'x': coord['x'],
                    'y': coord['y'],
                    'x_distance_from_median': x_dist,
                    'y_distance_from_median': y_dist,
                    'reason': 'Point très éloigné du groupe'
                })
        
        # Détecter erreurs de chiffres probables (ex: 703180 au lieu de 703480)
        if len(coordinates) >= 3:
            # Analyser Y et X séparément
            for coord_type, coord_values in [('y', y_coords), ('x', x_coords)]:
                # Identifier valeurs aberrantes par distance à la médiane
                median_val = sorted(coord_values)[len(coord_values)//2]
                distances_to_median = [abs(val - median_val) for val in coord_values]
                max_distance = max(distances_to_median)
                avg_distance = sum(distances_to_median) / len(distances_to_median)
                
                # Si une distance est significativement plus grande (>3x la moyenne)
                if max_distance > avg_distance * 3 and max_distance > 50:  # 50m minimum
                    aberrant_index = distances_to_median.index(max_distance)
                    aberrant_value = coord_values[aberrant_index]
                    
                    # Chercher correction par changement de chiffre
                    best_correction = self._find_best_digit_correction(
                        aberrant_value, coord_values, aberrant_index
                    )
                    
                    if best_correction and best_correction['confidence'] > 0.8:
                        anomaly_result['suspected_errors'].append({
                            'point_id': coordinates[aberrant_index].get('point_id', f'Point_{aberrant_index+1}'),
                            f'original_{coord_type}': aberrant_value,
                            f'suggested_{coord_type}': best_correction['new_value'],
                            'reason': best_correction['reason'],
                            'confidence': best_correction['confidence'],
                            'distance_improvement': best_correction['improvement']
                        })
        
        return anomaly_result
    
    def _find_best_digit_correction(self, aberrant_value: float, all_values: List[float], index: int) -> Dict[str, Any]:
        """Trouve la meilleure correction par changement d'un seul chiffre"""
        
        aberrant_str = str(int(aberrant_value))
        best_correction = None
        best_improvement = 0
        
        # Tester changement de chaque chiffre
        for pos in range(len(aberrant_str)):
            for digit in '0123456789':
                if aberrant_str[pos] != digit:
                    new_str = aberrant_str[:pos] + digit + aberrant_str[pos+1:]
                    new_value = float(new_str)
                    
                    # Calculer amélioration
                    improvement = self._calculate_position_improvement(
                        new_value, aberrant_value, all_values, index
                    )
                    
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_correction = {
                            'new_value': new_value,
                            'old_digit': aberrant_str[pos],
                            'new_digit': digit,
                            'position': pos,
                            'improvement': improvement,
                            'reason': f'Correction chiffre: {aberrant_str[pos]}→{digit} à position {pos+1}',
                            'confidence': min(improvement, 1.0)
                        }
        
        return best_correction
    
    def _calculate_position_improvement(self, new_value: float, old_value: float, 
                                       all_values: List[float], index: int) -> float:
        """Calcule l'amélioration de position d'une correction"""
        
        other_values = [v for i, v in enumerate(all_values) if i != index]
        
        if not other_values:
            return 0.0
        
        # Distances avant correction
        old_distances = [abs(old_value - v) for v in other_values]
        old_avg_distance = sum(old_distances) / len(old_distances)
        
        # Distances après correction
        new_distances = [abs(new_value - v) for v in other_values]
        new_avg_distance = sum(new_distances) / len(new_distances)
        
        # Amélioration relative
        if old_avg_distance == 0:
            return 0.0
        
        improvement = (old_avg_distance - new_avg_distance) / old_avg_distance
        return max(improvement, 0.0)

    def _is_more_consistent(self, new_value: float, all_values: List[float], index: int) -> bool:
        """Vérifie si une nouvelle valeur est plus cohérente avec les autres"""
        
        other_values = [v for i, v in enumerate(all_values) if i != index]
        
        if not other_values:
            return False
        
        # Distance à la valeur originale
        original_distances = [abs(new_value - v) for v in other_values]
        current_distances = [abs(all_values[index] - v) for v in other_values]
        
        avg_new_distance = sum(original_distances) / len(original_distances)
        avg_current_distance = sum(current_distances) / len(current_distances)
        
        # Plus cohérent si distance moyenne plus faible
        return avg_new_distance < avg_current_distance * 0.5  # 50% d'amélioration minimum
    
    def _calculate_correction_confidence(self, new_value: float, all_values: List[float], index: int) -> float:
        """Calcule la confiance dans une correction suggérée"""
        
        other_values = [v for i, v in enumerate(all_values) if i != index]
        
        if not other_values:
            return 0.0
        
        current_distances = [abs(all_values[index] - v) for v in other_values]
        new_distances = [abs(new_value - v) for v in other_values]
        
        improvement = (sum(current_distances) - sum(new_distances)) / sum(current_distances)
        return min(max(improvement, 0.0), 1.0)
    
    def _suggest_corrections(self, coordinates: List[Dict], validation_result: Dict) -> List[Dict]:
        """Suggère des corrections basées sur les erreurs détectées"""
        
        corrections = []
        
        # Corrections basées sur les anomalies détectées
        if 'anomaly_detection' in validation_result:
            for error in validation_result['anomaly_detection'].get('suspected_errors', []):
                # Corrections Y
                if 'suggested_y' in error and error.get('confidence', 0) > 0.8:
                    corrections.append({
                        'type': 'coordinate_correction',
                        'point_id': error['point_id'],
                        'field': 'y',
                        'original_value': error['original_y'],
                        'suggested_value': error['suggested_y'],
                        'reason': error['reason'],
                        'confidence': error['confidence']
                    })
                
                # Corrections X
                if 'suggested_x' in error and error.get('confidence', 0) > 0.8:
                    corrections.append({
                        'type': 'coordinate_correction',
                        'point_id': error['point_id'],
                        'field': 'x',
                        'original_value': error['original_x'],
                        'suggested_value': error['suggested_x'],
                        'reason': error['reason'],
                        'confidence': error['confidence']
                    })
        
        return corrections
    
    def _calculate_statistics(self, coordinates: List[Dict]) -> Dict[str, Any]:
        """Calcule statistiques détaillées"""
        
        if not coordinates:
            return {}
        
        x_coords = [c['x'] for c in coordinates]
        y_coords = [c['y'] for c in coordinates]
        
        return {
            'point_count': len(coordinates),
            'x_range': {'min': min(x_coords), 'max': max(x_coords), 'span': max(x_coords) - min(x_coords)},
            'y_range': {'min': min(y_coords), 'max': max(y_coords), 'span': max(y_coords) - min(y_coords)},
            'center': {'x': sum(x_coords) / len(x_coords), 'y': sum(y_coords) / len(y_coords)}
        }
    
    def _print_validation_summary(self, result: Dict[str, Any]) -> None:
        """Affiche résumé de validation"""
        
        print(f"\n📋 RÉSUMÉ VALIDATION:")
        print(f"===========================================")
        
        status = "✅ VALIDE" if result['valid'] else "❌ INVALIDE"
        print(f"🎯 Status: {status}")
        print(f"📍 Points: {result['coordinates_count']}")
        
        if result['errors']:
            print(f"❌ Erreurs: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  • {error}")
        
        if result['warnings']:
            print(f"⚠️ Avertissements: {len(result['warnings'])}")
            for warning in result['warnings'][:3]:  # Top 3
                print(f"  • {warning}")
            if len(result['warnings']) > 3:
                print(f"  ... et {len(result['warnings'])-3} autres")
        
        if result['corrections']:
            print(f"🔧 Corrections suggérées: {len(result['corrections'])}")
            for correction in result['corrections']:
                conf_pct = correction['confidence'] * 100
                print(f"  • {correction['point_id']}: {correction['original_value']:.2f} → {correction['suggested_value']:.2f} ({conf_pct:.1f}% confiance)")
        
        print(f"===========================================")


def validate_gemini_results(results_file: str) -> Dict[str, Any]:
    """Valide les résultats d'un fichier d'extraction Gemini"""
    
    print(f"🔍 VALIDATION FICHIER: {Path(results_file).name}")
    
    validator = CoordinateValidator()
    
    # Charger résultats
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    validations = {}
    
    # Traiter selon format (batch ou simple)
    if 'results' in data:
        # Format batch
        for result in data['results']:
            if result.get('success') and 'coordinates' in result:
                image_name = Path(result['image_path']).name
                coordinates = result['coordinates']
                
                print(f"\n📄 Validation {image_name}:")
                validation = validator.validate_coordinates(coordinates, result['image_path'])
                validations[image_name] = validation
    
    elif 'coordinates' in data:
        # Format simple
        image_name = Path(data.get('image_path', 'unknown')).name
        coordinates = data['coordinates']
        
        validation = validator.validate_coordinates(coordinates, data.get('image_path'))
        validations[image_name] = validation
    
    # Résumé global
    total_valid = sum(1 for v in validations.values() if v['valid'])
    total_files = len(validations)
    
    print(f"\n🎯 RÉSUMÉ GLOBAL:")
    print(f"📊 Fichiers validés: {total_valid}/{total_files}")
    print(f"📈 Taux de validité: {total_valid/total_files*100:.1f}%")
    
    return {
        'global_valid': total_valid == total_files,
        'valid_count': total_valid,
        'total_count': total_files,
        'validations': validations
    }


if __name__ == "__main__":
    # Test sur les derniers résultats
    import sys
    from pathlib import Path
    
    output_dir = Path("output")
    
    if len(sys.argv) > 1:
        # Fichier spécifique
        results_file = sys.argv[1]
    else:
        # Dernier fichier généré
        gemini_files = list(output_dir.glob("gemini_*.json"))
        if not gemini_files:
            print("❌ Aucun fichier résultats trouvé dans output/")
            sys.exit(1)
        results_file = max(gemini_files, key=lambda x: x.stat().st_mtime)
    
    validate_gemini_results(str(results_file))