#!/usr/bin/env python3
"""
Démonstration simple de l'intégration résultats Gemini avec superposition
Sans dépendances géospatiales lourdes - focus sur l'analyse des données
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import math

class SimpleOverlayDemo:
    """Démonstration simplifiée de l'analyse géospatiale"""
    
    def __init__(self):
        self.utm_bounds = {
            'x_min': 200000, 'x_max': 600000,
            'y_min': 600000, 'y_max': 1400000
        }
        
        print("🗺️ DÉMO SUPERPOSITION SIMPLE INITIALISÉE")
        print("📍 Focus: Analyse des résultats Gemini")
    
    def load_gemini_results(self, results_path: str) -> Dict[str, Any]:
        """Charge et analyse les résultats Gemini"""
        
        print(f"\n📊 ANALYSE RÉSULTATS GEMINI")
        print(f"📄 Fichier: {Path(results_path).name}")
        
        with open(results_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extraire toutes les coordonnées
        all_coordinates = []
        
        if 'results' in data:
            # Format batch
            for result in data['results']:
                if result.get('success') and 'coordinates' in result:
                    image_name = Path(result['image_path']).name
                    
                    for coord in result['coordinates']:
                        coord_data = {
                            'x': coord['x'],
                            'y': coord['y'],
                            'point_id': coord.get('point_id', 'Unknown'),
                            'confidence': coord.get('confidence', 0.0),
                            'image_source': image_name,
                            'coordinate_system': coord.get('coordinate_system', 'EPSG:32631')
                        }
                        all_coordinates.append(coord_data)
        
        elif 'coordinates' in data:
            # Format simple
            image_name = Path(data.get('image_path', 'unknown')).name
            
            for coord in data['coordinates']:
                coord_data = {
                    'x': coord['x'],
                    'y': coord['y'],
                    'point_id': coord.get('point_id', 'Unknown'),
                    'confidence': coord.get('confidence', 0.0),
                    'image_source': image_name,
                    'coordinate_system': coord.get('coordinate_system', 'EPSG:32631')
                }
                all_coordinates.append(coord_data)
        
        # Statistiques
        stats = self._calculate_stats(all_coordinates, data)
        
        return {
            'coordinates': all_coordinates,
            'statistics': stats,
            'original_data': data
        }
    
    def _calculate_stats(self, coordinates: List[Dict], original_data: Dict) -> Dict[str, Any]:
        """Calcule statistiques détaillées"""
        
        if not coordinates:
            return {'total_points': 0}
        
        # Statistiques de base
        x_coords = [c['x'] for c in coordinates]
        y_coords = [c['y'] for c in coordinates]
        confidences = [c['confidence'] for c in coordinates]
        
        # Étendue géographique
        bounds = {
            'min_x': min(x_coords),
            'max_x': max(x_coords),
            'min_y': min(y_coords),
            'max_y': max(y_coords)
        }
        
        # Centre approximatif
        center = {
            'x': (bounds['min_x'] + bounds['max_x']) / 2,
            'y': (bounds['min_y'] + bounds['max_y']) / 2
        }
        
        # Distances entre points
        distances = []
        for i, coord1 in enumerate(coordinates):
            for j, coord2 in enumerate(coordinates[i+1:], i+1):
                dist = math.sqrt(
                    (coord1['x'] - coord2['x'])**2 + 
                    (coord1['y'] - coord2['y'])**2
                )
                distances.append(dist)
        
        # Sources d'images
        image_sources = list(set(c['image_source'] for c in coordinates))
        
        # Statistiques par source
        source_stats = {}
        for source in image_sources:
            source_coords = [c for c in coordinates if c['image_source'] == source]
            source_stats[source] = {
                'count': len(source_coords),
                'avg_confidence': sum(c['confidence'] for c in source_coords) / len(source_coords)
            }
        
        stats = {
            'total_points': len(coordinates),
            'unique_images': len(image_sources),
            'bounds': bounds,
            'center': center,
            'extent_km': {
                'width': (bounds['max_x'] - bounds['min_x']) / 1000,
                'height': (bounds['max_y'] - bounds['min_y']) / 1000
            },
            'confidence': {
                'min': min(confidences),
                'max': max(confidences),
                'avg': sum(confidences) / len(confidences)
            },
            'distances': {
                'min': min(distances) if distances else 0,
                'max': max(distances) if distances else 0,
                'avg': sum(distances) / len(distances) if distances else 0
            },
            'by_source': source_stats
        }
        
        # Ajout stats du pipeline
        if 'statistics' in original_data:
            stats['pipeline'] = original_data['statistics']
        
        return stats
    
    def analyze_coordinate_patterns(self, coordinates: List[Dict]) -> Dict[str, Any]:
        """Analyse les patterns dans les coordonnées"""
        
        print(f"\n🔍 ANALYSE PATTERNS COORDONNÉES")
        
        # Grouper par image source
        by_source = {}
        for coord in coordinates:
            source = coord['image_source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(coord)
        
        patterns = {}
        
        for source, coords in by_source.items():
            print(f"\n  📄 {source}: {len(coords)} points")
            
            # Points triés par ID si possible
            sorted_coords = sorted(coords, key=lambda x: x['point_id'])
            
            # Afficher points
            for coord in sorted_coords:
                print(f"    • {coord['point_id']}: X={coord['x']:.2f}, Y={coord['y']:.2f} (conf: {coord['confidence']:.3f})")
            
            # Pattern géométrique (si c'est un polygone)
            if len(coords) >= 3:
                # Calculer centre approximatif de ces points
                center_x = sum(c['x'] for c in coords) / len(coords)
                center_y = sum(c['y'] for c in coords) / len(coords)
                
                # Distances au centre
                distances_to_center = [
                    math.sqrt((c['x'] - center_x)**2 + (c['y'] - center_y)**2)
                    for c in coords
                ]
                
                pattern_info = {
                    'center': {'x': center_x, 'y': center_y},
                    'avg_radius': sum(distances_to_center) / len(distances_to_center),
                    'geometry_type': 'polygon' if len(coords) >= 3 else 'points'
                }
                
                patterns[source] = pattern_info
                print(f"    🎯 Centre approx: X={center_x:.2f}, Y={center_y:.2f}")
                print(f"    📐 Rayon moyen: {pattern_info['avg_radius']:.1f}m")
        
        return patterns
    
    def discover_available_layers(self, data_path: str = "Data_Hackathon_IA_2025/couche/") -> Dict[str, Dict]:
        """Découvre les couches GeoJSON disponibles"""
        
        print(f"\n🗂️ DÉCOUVERTE COUCHES DISPONIBLES")
        print(f"📂 Dossier: {data_path}")
        
        data_dir = Path(data_path)
        layers = {}
        
        if data_dir.exists():
            for geojson_file in data_dir.glob("*.geojson"):
                layer_name = geojson_file.stem
                file_size_mb = geojson_file.stat().st_size / 1024 / 1024
                
                layer_info = {
                    'path': str(geojson_file),
                    'size_mb': file_size_mb,
                    'name': layer_name
                }
                
                layers[layer_name] = layer_info
                print(f"  📄 {layer_name}: {file_size_mb:.1f} MB")
        
        else:
            print(f"  ❌ Dossier non trouvé: {data_path}")
        
        return layers
    
    def create_summary_report(self, results: Dict[str, Any], 
                             patterns: Dict[str, Any], 
                             layers: Dict[str, Dict]) -> str:
        """Crée un rapport de synthèse"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"superposition_analysis_{timestamp}.json"
        
        coordinates = results['coordinates']
        stats = results['statistics']
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'simple_overlay_demo',
            'gemini_extraction': {
                'total_coordinates': len(coordinates),
                'unique_images': stats['unique_images'],
                'success_rate': stats.get('pipeline', {}).get('success_rate', 'N/A'),
                'avg_confidence': stats['confidence']['avg'],
                'coordinate_system': 'EPSG:32631 (UTM 31N)'
            },
            'spatial_extent': {
                'bounds_utm': stats['bounds'],
                'center_utm': stats['center'],
                'extent_km': stats['extent_km']
            },
            'coordinate_patterns': patterns,
            'available_layers': layers,
            'next_steps': [
                'Installer bibliothèques géospatiales complètes',
                'Effectuer intersections spatiales réelles',
                'Créer cartes interactives',
                'Export formats géospatiaux standards'
            ]
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 RAPPORT SYNTHÈSE CRÉÉ: {report_file}")
        
        return report_file
    
    def export_coordinates_simple(self, coordinates: List[Dict]) -> str:
        """Export simple des coordonnées en CSV"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"coordinates_export_{timestamp}.csv"
        
        # En-têtes CSV
        headers = ['point_id', 'x_utm', 'y_utm', 'confidence', 'image_source', 'coordinate_system']
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            # Écrire en-têtes
            f.write(','.join(headers) + '\n')
            
            # Écrire données
            for coord in coordinates:
                row = [
                    coord['point_id'],
                    str(coord['x']),
                    str(coord['y']),
                    str(coord['confidence']),
                    coord['image_source'],
                    coord['coordinate_system']
                ]
                f.write(','.join(row) + '\n')
        
        print(f"📊 Export CSV: {csv_file}")
        return csv_file


def run_demo():
    """Exécute la démonstration complète"""
    
    print("🚀 DÉMO SIMPLE SUPERPOSITION GÉOSPATIALE")
    print("=" * 60)
    
    try:
        # 1. Initialiser démo
        demo = SimpleOverlayDemo()
        
        # 2. Trouver résultats Gemini les plus récents
        output_dir = Path("output")
        gemini_files = list(output_dir.glob("gemini_*.json"))
        
        if not gemini_files:
            print("❌ Aucun fichier résultats Gemini trouvé dans output/")
            return
        
        # Prioriser les fichiers batch (plus complets)
        batch_files = [f for f in gemini_files if "batch" in f.name]
        
        if batch_files:
            latest_results = max(batch_files, key=lambda x: x.stat().st_mtime)
            print(f"📊 Utilisation résultats BATCH: {latest_results.name}")
        else:
            latest_results = max(gemini_files, key=lambda x: x.stat().st_mtime)
            print(f"📊 Utilisation résultats: {latest_results.name}")
        
        # 3. Charger et analyser résultats Gemini
        results = demo.load_gemini_results(str(latest_results))
        coordinates = results['coordinates']
        stats = results['statistics']
        
        print(f"\n✅ RÉSULTATS CHARGÉS")
        print(f"📍 Total coordonnées: {len(coordinates)}")
        print(f"🖼️ Images sources: {stats['unique_images']}")
        print(f"🎯 Confiance moyenne: {stats['confidence']['avg']:.3f}")
        print(f"📐 Étendue: {stats['extent_km']['width']:.1f} x {stats['extent_km']['height']:.1f} km")
        
        # 4. Analyser patterns
        patterns = demo.analyze_coordinate_patterns(coordinates)
        
        # 5. Découvrir couches disponibles
        layers = demo.discover_available_layers()
        
        print(f"\n🗂️ COUCHES DISPONIBLES: {len(layers)}")
        for name, info in layers.items():
            print(f"  • {name}: {info['size_mb']:.1f} MB")
        
        # 6. Export simple
        csv_file = demo.export_coordinates_simple(coordinates)
        
        # 7. Créer rapport synthèse
        report_file = demo.create_summary_report(results, patterns, layers)
        
        print(f"\n🏆 DÉMO TERMINÉE")
        print(f"📊 CSV: {csv_file}")
        print(f"📋 Rapport: {report_file}")
        
        # 8. Suggestions suite
        print(f"\n💡 ÉTAPES SUIVANTES:")
        print(f"1. Installer: uv add geopandas matplotlib folium shapely")
        print(f"2. Exécuter: python geospatial_overlay.py (version complète)")
        print(f"3. Cartes interactives et intersections spatiales réelles")
        
        return {
            'coordinates': coordinates,
            'statistics': stats,
            'patterns': patterns,
            'available_layers': layers,
            'exports': {
                'csv': csv_file,
                'report': report_file
            }
        }
        
    except Exception as e:
        print(f"❌ Erreur démonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_demo()