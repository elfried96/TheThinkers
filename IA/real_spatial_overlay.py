#!/usr/bin/env python3
"""
Module de superposition spatiale RÉELLE 
Utilise les vraies données GeoJSON du hackathon pour les intersections
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
import logging

try:
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Point, Polygon
    from shapely.ops import transform
    GEOSPATIAL_AVAILABLE = True
    print("✅ Bibliothèques géospatiales disponibles")
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    print("❌ Bibliothèques géospatiales manquantes")
    print("Installation: pip install geopandas shapely")

logger = logging.getLogger(__name__)

class RealSpatialOverlay:
    """Superposition spatiale avec vraies données GeoJSON"""
    
    def __init__(self, geojson_path: str = "Data_Hackathon_IA_2025/couche/"):
        """
        Initialise avec le dossier des couches GeoJSON
        
        Args:
            geojson_path: Chemin vers les fichiers GeoJSON
        """
        
        if not GEOSPATIAL_AVAILABLE:
            raise ImportError("❌ Bibliothèques géospatiales manquantes")
        
        self.geojson_path = Path(geojson_path)
        if not self.geojson_path.exists():
            raise FileNotFoundError(f"❌ Dossier GeoJSON non trouvé: {geojson_path}")
        
        # Système de coordonnées
        self.utm_crs = "EPSG:32631"  # UTM 31N Bénin
        self.wgs84_crs = "EPSG:4326"
        
        # Découvrir couches disponibles
        self.available_layers = self._discover_geojson_layers()
        
        # Cache pour les couches chargées (éviter rechargement)
        self._layer_cache = {}
        
        print(f"🗺️ SUPERPOSITION SPATIALE RÉELLE INITIALISÉE")
        print(f"📂 Couches GeoJSON trouvées: {len(self.available_layers)}")
        print(f"📍 Système coordonnées: {self.utm_crs}")
        
        # Afficher tailles des couches
        for name, info in self.available_layers.items():
            print(f"  📄 {name}: {info['size_mb']:.1f} MB")
    
    def _discover_geojson_layers(self) -> Dict[str, Dict]:
        """Découvre les couches GeoJSON disponibles"""
        
        layers = {}
        
        # Colonnes attendues du format groundtruth
        expected_columns = [
            'aif', 'air_proteges', 'dpl', 'dpm', 'enregistrement individuel',
            'litige', 'parcelles', 'restriction', 'tf_demembres', 
            'tf_en_cours', 'tf_etat', 'titre_reconstitue', 'zone_inondable'
        ]
        
        for geojson_file in self.geojson_path.glob("*.geojson"):
            layer_name = geojson_file.name.replace('.geojson', '')
            
            # Normaliser nom (espaces → underscores)
            normalized_name = layer_name.replace(' ', ' ')  # Garder espaces pour compatibilité Excel
            
            if normalized_name in expected_columns:
                file_size_mb = geojson_file.stat().st_size / 1024 / 1024
                
                layers[normalized_name] = {
                    'file_path': str(geojson_file),
                    'size_mb': file_size_mb,
                    'original_name': layer_name
                }
        
        return layers
    
    def calculate_real_intersections(self, coordinates: List[Dict], image_name: str = None) -> Dict[str, str]:
        """
        Calcule les vraies intersections spatiales avec les couches GeoJSON
        
        Args:
            coordinates: Liste des coordonnées extraites
            image_name: Nom de l'image (pour debug)
            
        Returns:
            Dictionnaire avec OUI/NON pour chaque couche
        """
        
        if not coordinates:
            print("⚠️ Aucune coordonnée à analyser")
            return {layer: 'NON' for layer in self.available_layers.keys()}
        
        print(f"\n🔍 CALCUL INTERSECTIONS RÉELLES")
        print(f"📍 {len(coordinates)} points à analyser")
        if image_name:
            print(f"📄 Image source: {image_name}")
        
        # Créer géométries points
        points = self._create_point_geometries(coordinates)
        
        # Calculer intersections pour chaque couche
        intersections = {}
        
        for layer_name in self.available_layers.keys():
            try:
                has_intersection = self._check_layer_intersection(points, layer_name)
                intersections[layer_name] = 'OUI' if has_intersection else 'NON'
                
                status = "✅" if has_intersection else "❌"
                print(f"  {status} {layer_name}: {intersections[layer_name]}")
                
            except Exception as e:
                logger.warning(f"Erreur intersection {layer_name}: {e}")
                intersections[layer_name] = 'NON'
                print(f"  ⚠️ {layer_name}: ERREUR ({str(e)[:50]})")
        
        # Statistiques
        oui_count = list(intersections.values()).count('OUI')
        total_count = len(intersections)
        
        print(f"📊 Résultat: {oui_count}/{total_count} intersections détectées")
        
        return intersections
    
    def _create_point_geometries(self, coordinates: List[Dict]) -> gpd.GeoDataFrame:
        """Crée GeoDataFrame des points en UTM 31N"""
        
        # Extraire coordonnées
        points_data = []
        geometries = []
        
        for i, coord in enumerate(coordinates):
            points_data.append({
                'point_id': coord.get('point_id', f'P{i+1}'),
                'x': coord['x'],
                'y': coord['y']
            })
            geometries.append(Point(coord['x'], coord['y']))
        
        # Créer GeoDataFrame en UTM 31N
        gdf = gpd.GeoDataFrame(points_data, geometry=geometries, crs=self.utm_crs)
        
        return gdf
    
    def _check_layer_intersection(self, points_gdf: gpd.GeoDataFrame, layer_name: str) -> bool:
        """
        Vérifie intersection avec une couche spécifique
        
        Args:
            points_gdf: GeoDataFrame des points
            layer_name: Nom de la couche à vérifier
            
        Returns:
            True si au moins une intersection trouvée
        """
        
        # Charger couche (avec cache)
        layer_gdf = self._load_layer_cached(layer_name)
        
        if layer_gdf is None or layer_gdf.empty:
            return False
        
        # S'assurer même CRS
        if layer_gdf.crs != points_gdf.crs:
            layer_gdf = layer_gdf.to_crs(points_gdf.crs)
        
        # Intersection spatiale
        intersection = gpd.sjoin(points_gdf, layer_gdf, how='inner', predicate='within')
        
        # Au moins un point dans la couche = intersection
        return len(intersection) > 0
    
    def _load_layer_cached(self, layer_name: str) -> gpd.GeoDataFrame:
        """Charge une couche avec mise en cache"""
        
        if layer_name in self._layer_cache:
            return self._layer_cache[layer_name]
        
        if layer_name not in self.available_layers:
            logger.warning(f"Couche '{layer_name}' non trouvée")
            return None
        
        layer_info = self.available_layers[layer_name]
        file_path = layer_info['file_path']
        
        try:
            print(f"    📂 Chargement {layer_name} ({layer_info['size_mb']:.1f} MB)...")
            
            # Stratégie de chargement selon taille
            if layer_info['size_mb'] > 100:  # Fichiers très volumineux
                gdf = self._load_large_layer(file_path, layer_name)
            else:
                gdf = gpd.read_file(file_path)
            
            # Mise en cache
            self._layer_cache[layer_name] = gdf
            
            print(f"    ✅ {len(gdf)} entités chargées")
            return gdf
            
        except Exception as e:
            logger.error(f"Erreur chargement {layer_name}: {e}")
            self._layer_cache[layer_name] = None
            return None
    
    def _load_large_layer(self, file_path: str, layer_name: str) -> gpd.GeoDataFrame:
        """Chargement optimisé pour gros fichiers"""
        
        print(f"    ⚡ Chargement optimisé fichier volumineux...")
        
        # Pour les gros fichiers comme parcelles.geojson (351MB)
        # On peut utiliser des techniques d'optimisation
        
        try:
            # Essayer chargement direct d'abord
            gdf = gpd.read_file(file_path)
            
            # Si trop volumineux, simplifier géométries
            if len(gdf) > 50000:
                print(f"    🔧 Simplification géométries ({len(gdf)} entités)")
                gdf['geometry'] = gdf['geometry'].simplify(tolerance=1.0)  # 1m de tolérance
            
            return gdf
            
        except MemoryError:
            print(f"    ⚠️ Mémoire insuffisante pour {layer_name}")
            # Fallback: échantillonnage
            return self._sample_large_layer(file_path)
    
    def _sample_large_layer(self, file_path: str, sample_size: int = 10000) -> gpd.GeoDataFrame:
        """Échantillonnage pour très gros fichiers"""
        
        print(f"    📊 Échantillonnage ({sample_size} entités max)")
        
        # Charger par chunks et échantillonner
        try:
            gdf = gpd.read_file(file_path)
            if len(gdf) > sample_size:
                sampled = gdf.sample(n=sample_size, random_state=42)
                print(f"    ✂️ Échantillonné: {len(gdf)} → {len(sampled)} entités")
                return sampled
            return gdf
        except:
            # Derniers recours: retourner None
            print(f"    ❌ Échec chargement - couche ignorée")
            return None
    
    def get_intersection_summary(self, intersections: Dict[str, str]) -> Dict[str, Any]:
        """Génère un résumé des intersections"""
        
        oui_layers = [layer for layer, value in intersections.items() if value == 'OUI']
        non_layers = [layer for layer, value in intersections.items() if value == 'NON']
        
        return {
            'total_layers': len(intersections),
            'intersecting_layers': len(oui_layers),
            'non_intersecting_layers': len(non_layers),
            'intersection_rate': len(oui_layers) / len(intersections) if intersections else 0,
            'oui_layers': oui_layers,
            'non_layers': non_layers
        }
    
    def batch_process_coordinates(self, coordinates_list: List[Dict], 
                                 image_names: List[str] = None) -> List[Dict[str, str]]:
        """
        Traite plusieurs jeux de coordonnées en lot
        
        Args:
            coordinates_list: Liste de listes de coordonnées
            image_names: Noms des images correspondantes
            
        Returns:
            Liste des dictionnaires d'intersections
        """
        
        print(f"🚀 TRAITEMENT LOT: {len(coordinates_list)} jeux de coordonnées")
        
        results = []
        
        for i, coordinates in enumerate(coordinates_list):
            image_name = image_names[i] if image_names and i < len(image_names) else f"Image_{i+1}"
            
            print(f"\n[{i+1}/{len(coordinates_list)}] {'-'*30}")
            intersections = self.calculate_real_intersections(coordinates, image_name)
            results.append(intersections)
        
        # Statistiques globales
        all_oui_counts = [list(r.values()).count('OUI') for r in results]
        avg_intersections = sum(all_oui_counts) / len(all_oui_counts) if all_oui_counts else 0
        
        print(f"\n📊 RÉSUMÉ LOT:")
        print(f"🎯 Intersections moyenne: {avg_intersections:.1f}/13")
        print(f"📈 Min: {min(all_oui_counts) if all_oui_counts else 0}, Max: {max(all_oui_counts) if all_oui_counts else 0}")
        
        return results


def test_real_spatial_overlay():
    """Test du module de superposition réelle"""
    
    if not GEOSPATIAL_AVAILABLE:
        print("❌ Test impossible - bibliothèques manquantes")
        return
    
    print("🧪 TEST SUPERPOSITION SPATIALE RÉELLE")
    print("=" * 50)
    
    try:
        # Initialiser
        overlay = RealSpatialOverlay()
        
        # Coordonnées de test (leve9)
        test_coordinates = [
            {"x": 448005.15, "y": 703480.27, "point_id": "B1"},
            {"x": 448034.38, "y": 703480.00, "point_id": "B2"},  # Corrigée
            {"x": 448034.23, "y": 703465.29, "point_id": "B3"},
            {"x": 448005.21, "y": 703465.61, "point_id": "B4"}
        ]
        
        # Calcul intersections réelles
        real_intersections = overlay.calculate_real_intersections(test_coordinates, "leve9.png")
        
        # Résumé
        summary = overlay.get_intersection_summary(real_intersections)
        
        print(f"\n📋 RÉSUMÉ FINAL:")
        print(f"🎯 Intersections: {summary['intersecting_layers']}/{summary['total_layers']}")
        print(f"📈 Taux: {summary['intersection_rate']:.1%}")
        
        if summary['oui_layers']:
            print(f"✅ Couches intersectantes:")
            for layer in summary['oui_layers']:
                print(f"  • {layer}")
        
        return real_intersections
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_real_spatial_overlay()