#!/usr/bin/env python3
"""
GeoJSON Layer Intersection Analysis
Analyzes coordinate intersections between CSV submissions and GeoJSON layers
"""

import json
import pandas as pd
import os
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import transform
import numpy as np
from typing import Dict, List, Tuple, Any
import ast


def load_csv_data(csv_path: str) -> pd.DataFrame:
    """Load and parse the CSV file with coordinate data."""
    df = pd.read_csv(csv_path)
    
    # Parse coordinate strings to actual coordinate lists
    def parse_coordinates(coord_str):
        try:
            # Convert string representation to actual list
            coords = ast.literal_eval(coord_str)
            return coords
        except:
            return []
    
    df['parsed_coordinates'] = df['Coordonnées'].apply(parse_coordinates)
    return df


def load_geojson_file(geojson_path: str) -> Dict[str, Any]:
    """Load a GeoJSON file and return its contents."""
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {geojson_path}: {e}")
        return None


def create_polygon_from_coordinates(coordinates: List[Dict[str, float]]) -> Polygon:
    """Create a Shapely Polygon from coordinate list."""
    if not coordinates or len(coordinates) < 3:
        return None
    
    # Extract x, y coordinates and close the polygon if needed
    points = [(coord['x'], coord['y']) for coord in coordinates]
    
    # Close polygon if first and last points are different
    if points[0] != points[-1]:
        points.append(points[0])
    
    if len(points) < 4:  # Need at least 4 points for a valid polygon (including closure)
        return None
    
    return Polygon(points)


def geometry_from_geojson_feature(feature: Dict) -> Any:
    """Convert GeoJSON geometry to Shapely geometry."""
    geom = feature.get('geometry')
    if not geom:
        return None
    
    geom_type = geom.get('type')
    coordinates = geom.get('coordinates')
    
    if not coordinates:
        return None
    
    try:
        if geom_type == 'Polygon':
            if len(coordinates) > 0:
                # Handle exterior ring only for simplicity
                exterior = coordinates[0]
                return Polygon([(x, y) for x, y, *_ in exterior])
        
        elif geom_type == 'MultiPolygon':
            polygons = []
            for polygon_coords in coordinates:
                if polygon_coords:
                    # Handle exterior ring only
                    exterior = polygon_coords[0]
                    poly = Polygon([(x, y) for x, y, *_ in exterior])
                    if poly.is_valid:
                        polygons.append(poly)
            if polygons:
                return MultiPolygon(polygons)
        
        elif geom_type == 'LineString':
            return LineString([(x, y) for x, y, *_ in coordinates])
        
        elif geom_type == 'MultiLineString':
            lines = []
            for line_coords in coordinates:
                if line_coords:
                    line = LineString([(x, y) for x, y, *_ in line_coords])
                    if line.is_valid:
                        lines.append(line)
            if lines:
                return MultiLineString(lines)
        
        elif geom_type == 'Point':
            if len(coordinates) >= 2:
                return Point(coordinates[0], coordinates[1])
    
    except Exception as e:
        print(f"Error converting geometry {geom_type}: {e}")
        return None
    
    return None


def check_intersection(image_polygon: Polygon, geojson_geometry: Any) -> bool:
    """Check if image polygon intersects with GeoJSON geometry."""
    if not image_polygon or not geojson_geometry:
        return False
    
    try:
        # For point geometries, check if they're within the image polygon
        if hasattr(geojson_geometry, 'geom_type') and geojson_geometry.geom_type == 'Point':
            return image_polygon.contains(geojson_geometry) or image_polygon.intersects(geojson_geometry)
        
        # For line geometries, use buffer to create area for intersection
        elif hasattr(geojson_geometry, 'geom_type') and 'Line' in geojson_geometry.geom_type:
            # Create a small buffer around lines for intersection testing
            buffered_line = geojson_geometry.buffer(1.0)  # 1 meter buffer
            return image_polygon.intersects(buffered_line)
        
        # For polygon geometries, direct intersection
        else:
            return image_polygon.intersects(geojson_geometry)
    
    except Exception as e:
        print(f"Error checking intersection: {e}")
        return False


def analyze_intersections(csv_path: str, geojson_dir: str) -> Dict[str, Any]:
    """Main function to analyze intersections."""
    
    # Load CSV data
    print("Loading CSV data...")
    df = load_csv_data(csv_path)
    
    # Define the layers to check
    layer_files = {
        'aif': 'aif.geojson',
        'air_proteges': 'air_proteges.geojson',
        'dpl': 'dpl.geojson',
        'dpm': 'dpm.geojson',
        'enregistrement individuel': 'enregistrement individuel.geojson',
        'litige': 'litige.geojson',
        'parcelles': 'parcelles.geojson',
        'restriction': 'restriction.geojson',
        'tf_demembres': 'tf_demembres.geojson',
        'tf_en_cours': 'tf_en_cours.geojson',
        'tf_etat': 'tf_etat.geojson',
        'titre_reconstitue': 'titre_reconstitue.geojson',
        'zone_inondable': 'zone_inondable.geojson'
    }
    
    # Load all GeoJSON files
    print("Loading GeoJSON layers...")
    geojson_layers = {}
    processed_layers = []
    
    for layer_name, filename in layer_files.items():
        file_path = os.path.join(geojson_dir, filename)
        if os.path.exists(file_path):
            geojson_data = load_geojson_file(file_path)
            if geojson_data:
                geojson_layers[layer_name] = geojson_data
                processed_layers.append(layer_name)
                print(f"  ✓ Loaded {layer_name}")
            else:
                print(f"  ✗ Failed to load {layer_name}")
        else:
            print(f"  ✗ File not found: {filename}")
    
    # Initialize results
    results = {}
    layer_stats = {layer: 0 for layer in processed_layers}
    
    # Process each image
    print("\nAnalyzing intersections...")
    for idx, row in df.iterrows():
        image_name = row['Nom_du_levé']
        coordinates = row['parsed_coordinates']
        
        print(f"Processing {image_name}...")
        
        # Create polygon from coordinates
        image_polygon = create_polygon_from_coordinates(coordinates)
        
        if not image_polygon:
            print(f"  ⚠ Could not create polygon for {image_name}")
            continue
        
        # Initialize results for this image
        image_results = {}
        
        # Check intersection with each layer
        for layer_name in processed_layers:
            has_intersection = False
            
            if layer_name in geojson_layers:
                geojson_data = geojson_layers[layer_name]
                features = geojson_data.get('features', [])
                
                # Check intersection with each feature in the layer
                for feature in features:
                    geometry = geometry_from_geojson_feature(feature)
                    if geometry and check_intersection(image_polygon, geometry):
                        has_intersection = True
                        break
            
            image_results[layer_name] = "OUI" if has_intersection else "NON"
            if has_intersection:
                layer_stats[layer_name] += 1
        
        results[image_name] = image_results
        
        # Print results for this image
        intersections = [layer for layer, result in image_results.items() if result == "OUI"]
        if intersections:
            print(f"  ✓ Intersections: {', '.join(intersections)}")
        else:
            print(f"  ✗ No intersections found")
    
    return {
        'results': results,
        'layer_stats': layer_stats,
        'processed_layers': processed_layers,
        'total_images': len(df)
    }


def create_updated_csv(original_csv_path: str, results: Dict[str, Any], output_path: str):
    """Create updated CSV with intersection results."""
    df = pd.read_csv(original_csv_path)
    
    # Update intersection columns with new results
    for idx, row in df.iterrows():
        image_name = row['Nom_du_levé']
        if image_name in results['results']:
            image_results = results['results'][image_name]
            for layer_name in results['processed_layers']:
                if layer_name in df.columns:
                    df.at[idx, layer_name] = image_results.get(layer_name, 'NON')
    
    # Save updated CSV
    df.to_csv(output_path, index=False)
    print(f"\nUpdated CSV saved to: {output_path}")


def print_summary(results: Dict[str, Any]):
    """Print summary statistics."""
    print("\n" + "="*60)
    print("INTERSECTION ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nProcessed Layers ({len(results['processed_layers'])}):")
    for layer in sorted(results['processed_layers']):
        print(f"  ✓ {layer}")
    
    print(f"\nTotal Images Analyzed: {results['total_images']}")
    
    print(f"\nIntersection Statistics:")
    print(f"{'Layer Name':<25} {'Intersections':<15} {'Percentage':<10}")
    print("-" * 50)
    
    for layer_name in sorted(results['processed_layers']):
        count = results['layer_stats'][layer_name]
        percentage = (count / results['total_images']) * 100 if results['total_images'] > 0 else 0
        print(f"{layer_name:<25} {count:<15} {percentage:<10.1f}%")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # File paths
    csv_file = "/home/elfried-kinzoun/HackAsini/IA/submissions_TheThinkers.csv"
    geojson_directory = "/home/elfried-kinzoun/HackAsini/IA/Data_Hackathon_IA_2025/couche/"
    output_csv = "/home/elfried-kinzoun/HackAsini/IA/submissions_TheThinkers_updated.csv"
    
    # Run analysis
    results = analyze_intersections(csv_file, geojson_directory)
    
    # Print summary
    print_summary(results)
    
    # Create updated CSV
    create_updated_csv(csv_file, results, output_csv)
    
    # Print detailed results for first few images as examples
    print("\nDETAILED RESULTS (first 5 images):")
    print("-" * 60)
    count = 0
    for image_name, image_results in results['results'].items():
        if count >= 5:
            break
        print(f"\n{image_name}:")
        for layer, result in image_results.items():
            status = "✓" if result == "OUI" else "✗"
            print(f"  {status} {layer}: {result}")
        count += 1