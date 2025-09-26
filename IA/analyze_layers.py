#!/usr/bin/env python3
import json
import csv
from pathlib import Path
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union
# import pandas as pd

def load_geojson_layer(file_path):
    """Load and parse a GeoJSON layer file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        geometries = []
        for feature in data.get('features', []):
            geom = feature.get('geometry', {})
            if geom.get('type') == 'MultiPolygon':
                coords = geom.get('coordinates', [])
                # Convert MultiPolygon coordinates to Shapely MultiPolygon
                polygons = []
                for polygon_coords in coords:
                    # Each polygon_coords is a list of rings (exterior + holes)
                    if polygon_coords:
                        exterior = polygon_coords[0]
                        # Remove Z coordinates if present (keep only X, Y)
                        exterior_2d = [[pt[0], pt[1]] for pt in exterior]
                        if len(exterior_2d) >= 3:
                            polygons.append(Polygon(exterior_2d))
                
                if polygons:
                    if len(polygons) == 1:
                        geometries.append(polygons[0])
                    else:
                        geometries.append(MultiPolygon(polygons))
            
            elif geom.get('type') == 'Polygon':
                coords = geom.get('coordinates', [])
                if coords and coords[0]:
                    # Remove Z coordinates if present
                    exterior_2d = [[pt[0], pt[1]] for pt in coords[0]]
                    if len(exterior_2d) >= 3:
                        geometries.append(Polygon(exterior_2d))
        
        # Union all geometries for faster intersection checking
        if geometries:
            return unary_union(geometries)
        return None
        
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def point_in_geometry(point_coords, geometry):
    """Check if a point intersects with the geometry."""
    if geometry is None:
        return False
    
    try:
        x, y = point_coords
        point = Point(x, y)
        return geometry.intersects(point)
    except:
        return False

def parse_coordinates_from_csv(coord_string):
    """Parse coordinates from CSV format."""
    try:
        if not coord_string or coord_string.strip() == '':
            return []
        
        # Remove outer quotes and parse JSON
        coord_string = coord_string.strip('"')
        coords_data = json.loads(coord_string)
        
        # Extract x, y coordinates
        points = []
        for point in coords_data:
            if isinstance(point, dict) and 'x' in point and 'y' in point:
                points.append((float(point['x']), float(point['y'])))
        
        return points
    except Exception as e:
        print(f"Error parsing coordinates: {coord_string[:100]}... Error: {e}")
        return []

# Layer file mapping
layer_files = {
    'aif': 'aif.geojson',
    'air_proteges': 'air_proteges.geojson', 
    'dpl': 'dpl.geojson',
    'dpm': 'dpm.geojson',
    'enregistrement_individuel': 'enregistrement individuel.geojson',
    'litige': 'litige.geojson',
    'parcelles': 'parcelles.geojson',
    'restriction': 'restriction.geojson',
    'tf_demembres': 'tf_demembres.qmd',  # This might not exist
    'tf_en_cours': 'tf_en_cours.geojson',
    'tf_etat': 'tf_etat.qmd',  # This might not exist
    'titre_reconstitue': 'titre_reconstitue.geojson',  # This might not exist
    'zone_inondable': 'zone_inondable.geojson'
}

# CSV column mapping
csv_columns = {
    'aif': 2,
    'air_proteges': 3, 
    'dpl': 4,
    'dpm': 5,
    'enregistrement_individuel': 6,
    'litige': 7,
    'parcelles': 8,
    'restriction': 9,
    'tf_demembres': 10,
    'tf_en_cours': 11,
    'tf_etat': 12,
    'titre_reconstitue': 13,
    'zone_inondable': 14
}

def main():
    # Paths
    couche_dir = Path('/home/elfried-kinzoun/HackAsini/IA/Data_Hackathon_IA_2025/couche')
    csv_file = Path('/home/elfried-kinzoun/HackAsini/IA/submissions_TheThinkers.csv')
    
    # Load all layer geometries
    print("Loading layer geometries...")
    layer_geometries = {}
    for layer_name, filename in layer_files.items():
        file_path = couche_dir / filename
        if file_path.exists() and filename.endswith('.geojson'):
            print(f"Loading {layer_name}...")
            geometry = load_geojson_layer(file_path)
            if geometry:
                layer_geometries[layer_name] = geometry
                print(f"  ✓ Loaded {layer_name}")
            else:
                print(f"  ✗ Failed to load {layer_name}")
        else:
            print(f"  ✗ File not found or not GeoJSON: {filename}")
    
    print(f"Successfully loaded {len(layer_geometries)} layers")
    
    # Read and process CSV
    print("\nProcessing CSV...")
    
    # Read CSV data
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        rows = list(csv_reader)
    
    # Process each row (skip header)
    header = rows[0]
    updated_rows = [header]
    
    for i, row in enumerate(rows[1:], 1):
        if len(row) < 15:  # Ensure row has enough columns
            continue
            
        image_name = row[0]
        coordinates_str = row[1]
        
        print(f"Processing {image_name}...")
        
        # Parse coordinates
        coordinates = parse_coordinates_from_csv(coordinates_str)
        
        if not coordinates:
            print(f"  No valid coordinates found for {image_name}")
            updated_rows.append(row)
            continue
        
        # Check intersection with each layer
        updated_row = row[:]
        for layer_name, geometry in layer_geometries.items():
            col_index = csv_columns.get(layer_name)
            if col_index is None:
                continue
                
            # Check if any coordinate point intersects with this layer
            intersects = False
            for coord in coordinates:
                if point_in_geometry(coord, geometry):
                    intersects = True
                    break
            
            # Update the row
            if col_index < len(updated_row):
                updated_row[col_index] = 'OUI' if intersects else 'NON'
                if intersects:
                    print(f"  ✓ {layer_name}: OUI")
        
        updated_rows.append(updated_row)
    
    # Write updated CSV
    print("\nWriting updated CSV...")
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(updated_rows)
    
    print("✓ CSV updated successfully!")

if __name__ == "__main__":
    main()