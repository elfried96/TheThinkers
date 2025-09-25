#!/usr/bin/env python3
"""
Démonstration visuelle simplifiée pour leve9.png
Crée visualisation basique des coordonnées extraites
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import math

# Import du pipeline principal pour extraction
from main import MainPipeline

class VisualOverlayDemo:
    """Démonstration visuelle simple sans bibliothèques lourdes"""
    
    def __init__(self):
        print("🎨 DÉMONSTRATION VISUELLE SIMPLIFIÉE")
        print("📍 Focus: Visualisation coordonnées extraites")
        
    def process_single_image(self, image_path: str) -> Dict[str, Any]:
        """Traite une image et génère visualisation"""
        
        print(f"\n📄 TRAITEMENT IMAGE: {Path(image_path).name}")
        
        # 1. Vérifier que l'image existe
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image non trouvée: {image_path}")
        
        # 2. Extraction coordonnées avec pipeline principale
        print("🎯 EXTRACTION COORDONNÉES...")
        pipeline = MainPipeline()
        
        # Générer CSV temporaire
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_csv = f"temp_visual_{timestamp}.csv"
        
        try:
            csv_file = pipeline.process_input(image_path, temp_csv)
            
            # 3. Charger et analyser résultats
            results = self._load_csv_results(csv_file)
            
            # 4. Créer visualisations
            visualizations = self._create_visualizations(results)
            
            # 5. Nettoyer fichier temporaire
            if Path(temp_csv).exists():
                os.remove(temp_csv)
            
            return {
                'image_path': image_path,
                'coordinates': results['coordinates'],
                'analysis': results['analysis'],
                'visualizations': visualizations
            }
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            if Path(temp_csv).exists():
                os.remove(temp_csv)
            raise e
    
    def _load_csv_results(self, csv_file: str) -> Dict[str, Any]:
        """Charge et analyse résultats CSV"""
        
        import pandas as pd
        
        print(f"📊 ANALYSE RÉSULTATS CSV: {Path(csv_file).name}")
        
        df = pd.read_csv(csv_file)
        
        if len(df) == 0:
            raise ValueError("Aucun résultat dans le CSV")
        
        # Extraire première ligne (image unique)
        row = df.iloc[0]
        image_name = row['Nom_du_levé']
        coords_json = row['Coordonnées']
        
        # Parser coordonnées JSON
        coordinates = json.loads(coords_json)
        
        # Analyser intersections
        layer_columns = [
            'aif', 'air_proteges', 'dpl', 'dpm', 'enregistrement individuel',
            'litige', 'parcelles', 'restriction', 'tf_demembres', 
            'tf_en_cours', 'tf_etat', 'titre_reconstitue', 'zone_inondable'
        ]
        
        intersections = {}
        for col in layer_columns:
            intersections[col] = row[col]
        
        # Statistiques coordonnées
        x_coords = [c['x'] for c in coordinates]
        y_coords = [c['y'] for c in coordinates]
        
        analysis = {
            'total_points': len(coordinates),
            'bounds': {
                'min_x': min(x_coords),
                'max_x': max(x_coords),
                'min_y': min(y_coords),
                'max_y': max(y_coords)
            },
            'center': {
                'x': sum(x_coords) / len(x_coords),
                'y': sum(y_coords) / len(y_coords)
            },
            'intersections': intersections,
            'intersections_count': list(intersections.values()).count('OUI')
        }
        
        # Calculer étendue
        analysis['extent'] = {
            'width_m': analysis['bounds']['max_x'] - analysis['bounds']['min_x'],
            'height_m': analysis['bounds']['max_y'] - analysis['bounds']['min_y']
        }
        
        print(f"✅ {len(coordinates)} coordonnées analysées")
        print(f"📐 Étendue: {analysis['extent']['width_m']:.1f} x {analysis['extent']['height_m']:.1f} m")
        print(f"🎯 Centre: X={analysis['center']['x']:.2f}, Y={analysis['center']['y']:.2f}")
        print(f"🗂️ Intersections: {analysis['intersections_count']}/13")
        
        return {
            'image_name': image_name,
            'coordinates': coordinates,
            'analysis': analysis
        }
    
    def _create_visualizations(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Crée visualisations textuelles et fichiers de sortie"""
        
        print(f"\n🎨 CRÉATION VISUALISATIONS")
        
        coordinates = results['coordinates']
        analysis = results['analysis']
        image_name = results['image_name']
        
        visualizations = {}
        
        # 1. Rapport textuel détaillé
        report_file = self._create_text_report(image_name, coordinates, analysis)
        visualizations['text_report'] = report_file
        
        # 2. Coordonnées formatées pour SIG
        coord_file = self._create_coordinates_file(image_name, coordinates)
        visualizations['coordinates_file'] = coord_file
        
        # 3. Visualisation ASCII simple
        ascii_viz = self._create_ascii_visualization(coordinates, analysis)
        visualizations['ascii_map'] = ascii_viz
        
        # 4. Fichier KML simple (pour Google Earth)
        kml_file = self._create_simple_kml(image_name, coordinates)
        visualizations['kml_file'] = kml_file
        
        return visualizations
    
    def _create_text_report(self, image_name: str, coordinates: List[Dict], analysis: Dict) -> str:
        """Crée rapport textuel détaillé"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"visual_report_{Path(image_name).stem}_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("RAPPORT VISUEL - EXTRACTION COORDONNÉES\n")
            f.write("=" * 60 + "\n")
            f.write(f"Image: {image_name}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Système: EPSG:32631 (UTM 31N Bénin)\n\n")
            
            f.write("COORDONNÉES EXTRAITES\n")
            f.write("-" * 30 + "\n")
            for i, coord in enumerate(coordinates, 1):
                f.write(f"Point {i}: X={coord['x']:,.2f}m, Y={coord['y']:,.2f}m\n")
            
            f.write(f"\nSTATISTIQUES SPATIALES\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total points: {analysis['total_points']}\n")
            f.write(f"Centre X: {analysis['center']['x']:,.2f}m\n")
            f.write(f"Centre Y: {analysis['center']['y']:,.2f}m\n")
            f.write(f"Étendue: {analysis['extent']['width_m']:.1f} x {analysis['extent']['height_m']:.1f} m\n")
            
            f.write(f"\nINTERSECTIONS THÉMATIQUES\n")
            f.write("-" * 30 + "\n")
            for layer, value in analysis['intersections'].items():
                status = "✅" if value == "OUI" else "❌"
                f.write(f"{status} {layer}: {value}\n")
            
            f.write(f"\nTotal intersections: {analysis['intersections_count']}/13\n")
        
        print(f"📄 Rapport détaillé: {report_file}")
        return report_file
    
    def _create_coordinates_file(self, image_name: str, coordinates: List[Dict]) -> str:
        """Crée fichier coordonnées pour SIG"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        coord_file = f"coordinates_{Path(image_name).stem}_{timestamp}.txt"
        
        with open(coord_file, 'w', encoding='utf-8') as f:
            f.write("# Coordonnées UTM 31N (EPSG:32631)\n")
            f.write("# Format: Point_ID, X, Y\n")
            f.write("# Source: " + image_name + "\n\n")
            
            for i, coord in enumerate(coordinates, 1):
                point_id = f"B{i}" if f"B{i}" not in str(coordinates) else f"Point_{i}"
                f.write(f"{point_id},{coord['x']:.2f},{coord['y']:.2f}\n")
        
        print(f"📊 Coordonnées SIG: {coord_file}")
        return coord_file
    
    def _create_ascii_visualization(self, coordinates: List[Dict], analysis: Dict) -> str:
        """Crée visualisation ASCII simple"""
        
        print("🗺️ Génération carte ASCII...")
        
        # Normaliser coordonnées pour grille ASCII
        bounds = analysis['bounds']
        center = analysis['center']
        
        # Grille 20x10
        grid_width, grid_height = 20, 10
        ascii_map = []
        
        # Initialiser grille
        for _ in range(grid_height):
            ascii_map.append(['.'] * grid_width)
        
        # Placer points
        for i, coord in enumerate(coordinates):
            # Normaliser position (0-1)
            if bounds['max_x'] != bounds['min_x']:
                norm_x = (coord['x'] - bounds['min_x']) / (bounds['max_x'] - bounds['min_x'])
            else:
                norm_x = 0.5
                
            if bounds['max_y'] != bounds['min_y']:
                norm_y = (coord['y'] - bounds['min_y']) / (bounds['max_y'] - bounds['min_y'])
            else:
                norm_y = 0.5
            
            # Convertir en position grille
            grid_x = int(norm_x * (grid_width - 1))
            grid_y = int((1 - norm_y) * (grid_height - 1))  # Inverser Y
            
            # Placer marqueur
            ascii_map[grid_y][grid_x] = str((i % 9) + 1)
        
        # Placer centre approximatif
        if bounds['max_x'] != bounds['min_x'] and bounds['max_y'] != bounds['min_y']:
            center_norm_x = (center['x'] - bounds['min_x']) / (bounds['max_x'] - bounds['min_x'])
            center_norm_y = (center['y'] - bounds['min_y']) / (bounds['max_y'] - bounds['min_y'])
            center_grid_x = int(center_norm_x * (grid_width - 1))
            center_grid_y = int((1 - center_norm_y) * (grid_height - 1))
            
            if ascii_map[center_grid_y][center_grid_x] == '.':
                ascii_map[center_grid_y][center_grid_x] = '+'
        
        # Convertir en string
        ascii_str = "\n"
        ascii_str += "CARTE ASCII APPROXIMATIVE\n"
        ascii_str += f"Étendue: {analysis['extent']['width_m']:.0f}m x {analysis['extent']['height_m']:.0f}m\n"
        ascii_str += "-" * (grid_width + 2) + "\n"
        
        for row in ascii_map:
            ascii_str += "|" + "".join(row) + "|\n"
        
        ascii_str += "-" * (grid_width + 2) + "\n"
        ascii_str += "Légende: 1-9=Points, +=Centre, .=Vide\n"
        
        print(ascii_str)
        return ascii_str
    
    def _create_simple_kml(self, image_name: str, coordinates: List[Dict]) -> str:
        """Crée fichier KML simple pour Google Earth"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        kml_file = f"coordinates_{Path(image_name).stem}_{timestamp}.kml"
        
        # Convertir UTM vers WGS84 (approximation simple)
        # Note: Conversion approximative pour zone UTM 31N
        wgs84_coords = []
        for coord in coordinates:
            # Conversion approximative UTM 31N -> WGS84
            # Plus précis avec pyproj mais non disponible
            lat = (coord['y'] - 1000000) / 111320  # Approximation
            lon = (coord['x'] - 500000) / (111320 * math.cos(math.radians(lat))) + 3  # Zone 31N
            wgs84_coords.append({'lat': lat, 'lon': lon})
        
        # Générer KML
        kml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Coordonnées {image_name}</name>
    <description>Extraction coordonnées cadastrales - UTM 31N</description>
    
'''
        
        for i, (coord, wgs84) in enumerate(zip(coordinates, wgs84_coords), 1):
            kml_content += f'''    <Placemark>
      <name>Point {i}</name>
      <description>
        UTM 31N: X={coord['x']:.2f}m, Y={coord['y']:.2f}m
        Source: {image_name}
      </description>
      <Point>
        <coordinates>{wgs84['lon']:.6f},{wgs84['lat']:.6f},0</coordinates>
      </Point>
    </Placemark>
    
'''
        
        kml_content += '''  </Document>
</kml>'''
        
        with open(kml_file, 'w', encoding='utf-8') as f:
            f.write(kml_content)
        
        print(f"🌍 KML Google Earth: {kml_file}")
        return kml_file


def demo_leve9():
    """Démonstration spécifique pour leve9.png"""
    
    print("🚀 DÉMONSTRATION VISUELLE - LEVE9.PNG")
    print("=" * 50)
    
    image_path = "Data_Hackathon_IA_2025/Testing_Data/leve9.png"
    
    if not Path(image_path).exists():
        print(f"❌ Image non trouvée: {image_path}")
        print("Vérifiez le chemin vers le fichier")
        return
    
    try:
        demo = VisualOverlayDemo()
        
        # Traitement complet
        results = demo.process_single_image(image_path)
        
        print(f"\n🎨 VISUALISATIONS CRÉÉES:")
        for viz_type, viz_file in results['visualizations'].items():
            if viz_type != 'ascii_map':  # ASCII déjà affiché
                print(f"  📄 {viz_type}: {viz_file}")
        
        print(f"\n🏆 DÉMONSTRATION TERMINÉE")
        print(f"📊 {len(results['coordinates'])} coordonnées extraites")
        print(f"🎯 {results['analysis']['intersections_count']} intersections détectées")
        
        # Suggestions ouverture fichiers
        print(f"\n💡 POUR VISUALISER:")
        print(f"1. Ouvrir {results['visualizations']['text_report']} (rapport détaillé)")
        print(f"2. Ouvrir {results['visualizations']['kml_file']} dans Google Earth")
        print(f"3. Importer {results['visualizations']['coordinates_file']} dans QGIS/ArcGIS")
        
        return results
        
    except Exception as e:
        print(f"❌ Erreur démonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_leve9()