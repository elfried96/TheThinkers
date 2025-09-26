#!/usr/bin/env python3
"""
Script de test complet pour l'API d'extraction de coordonnées
Teste toutes les fonctionnalités : extraction, conversion EPSG:4326, superposition spatiale
"""

import requests
import json
import os
from pathlib import Path
import time

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self):
        """Test de l'endpoint /health"""
        print("🔍 Test endpoint /health...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ API en bonne santé")
                print(f"   - Gemini API: {'✅' if data['services']['gemini_api'] else '❌'}")
                print(f"   - Conversion coordonnées: {'✅' if data['services']['coordinate_conversion'] else '❌'}")
                print(f"   - Superposition spatiale: {'✅' if data['services']['spatial_overlay'] else '❌'}")
                return True
            else:
                print(f"❌ Erreur health check: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Impossible de contacter l'API: {e}")
            return False
    
    def test_root(self):
        """Test de l'endpoint racine"""
        print("🔍 Test endpoint racine...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print("✅ Endpoint racine OK")
                print(f"   Version: {data.get('version', 'N/A')}")
                return True
            else:
                print(f"❌ Erreur endpoint racine: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erreur endpoint racine: {e}")
            return False
    
    def test_extract_single_file(self, image_path):
        """Test extraction d'un fichier unique"""
        print(f"🔍 Test extraction fichier: {image_path}")
        
        if not Path(image_path).exists():
            print(f"❌ Fichier introuvable: {image_path}")
            return False
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (Path(image_path).name, f, 'image/jpeg')}
                response = self.session.post(
                    f"{self.base_url}/extract",
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Extraction réussie")
                
                # Afficher les résultats
                self._print_extraction_results(data)
                return True
            else:
                print(f"❌ Erreur extraction: {response.status_code}")
                print(f"   Détails: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction: {e}")
            return False
    
    def test_batch_extract(self, image_paths):
        """Test extraction par lot"""
        print(f"🔍 Test extraction par lot ({len(image_paths)} fichiers)...")
        
        existing_files = [p for p in image_paths if Path(p).exists()]
        if not existing_files:
            print("❌ Aucun fichier valide trouvé pour le test batch")
            return False
        
        try:
            files = []
            file_objects = []
            
            for image_path in existing_files[:3]:  # Limite à 3 fichiers pour le test
                f = open(image_path, 'rb')
                file_objects.append(f)
                files.append(('files', (Path(image_path).name, f, 'image/jpeg')))
            
            response = self.session.post(
                f"{self.base_url}/batch_extract",
                files=files,
                timeout=120
            )
            
            # Fermer les fichiers
            for f in file_objects:
                f.close()
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Extraction batch réussie")
                print(f"   Fichiers traités: {data.get('total_files', 0)}")
                print(f"   Extractions réussies: {data.get('successful_extractions', 0)}")
                return True
            else:
                print(f"❌ Erreur extraction batch: {response.status_code}")
                print(f"   Détails: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction batch: {e}")
            return False
    
    def _print_extraction_results(self, data):
        """Affiche les résultats d'extraction de manière formatée"""
        print(f"   📄 Fichier: {data.get('filename', 'N/A')}")
        print(f"   ✅ Succès: {data.get('extraction_success', False)}")
        
        if data.get('extraction_success'):
            # Coordonnées
            coords_raw = data.get('coordinates', '[]')
            if isinstance(coords_raw, str):
                try:
                    coords = json.loads(coords_raw)
                    print(f"   📍 Coordonnées détectées: {len(coords)}")
                    if coords:
                        print(f"      Première coord: X={coords[0].get('x', 'N/A')}, Y={coords[0].get('y', 'N/A')}")
                except:
                    print(f"   📍 Coordonnées brutes: {coords_raw}")
            
            # Coordonnées WGS84
            wgs84_coords = data.get('coordinates_wgs84', [])
            if wgs84_coords:
                print(f"   🌍 Coordonnées WGS84: {len(wgs84_coords)}")
                first_wgs = wgs84_coords[0]
                print(f"      Première coord WGS84: Lat={first_wgs.get('latitude', 'N/A')}, Lon={first_wgs.get('longitude', 'N/A')}")
            
            # Couches d'appartenance
            layers = ['aif', 'air_proteges', 'dpl', 'dpm', 'enregistrement_individuel', 
                     'litige', 'parcelles', 'restriction', 'tf_demembres', 'tf_en_cours',
                     'tf_etat', 'titre_reconstitue', 'zone_inondable']
            
            oui_layers = [layer for layer in layers if data.get(layer) == "OUI"]
            if oui_layers:
                print(f"   🗺️ Couches détectées: {', '.join(oui_layers)}")
            else:
                print("   🗺️ Aucune couche géographique détectée")
        else:
            print(f"   ❌ Erreur: {data.get('error', 'Erreur inconnue')}")

def main():
    print("🚀 Test complet de l'API d'extraction de coordonnées")
    print("=" * 60)
    
    # Initialiser le testeur
    tester = APITester()
    
    # Tests de base
    if not tester.test_health():
        print("❌ API non disponible, arrêt des tests")
        return
    
    if not tester.test_root():
        print("❌ Problème avec l'endpoint racine")
        return
    
    print("\n" + "=" * 60)
    
    # Tests d'extraction
    # Chercher des images de test dans le dossier courant
    test_images_dir = Path(".")
    possible_images = list(test_images_dir.glob("*.jpg")) + \
                     list(test_images_dir.glob("*.jpeg")) + \
                     list(test_images_dir.glob("*.png"))
    
    # Chercher aussi dans les dossiers parents
    for parent in [Path("../"), Path("../../")]:
        if parent.exists():
            possible_images.extend(parent.glob("**/*.jpg"))
            possible_images.extend(parent.glob("**/*.jpeg"))
            possible_images.extend(parent.glob("**/*.png"))
    
    # Limiter à 5 images pour les tests
    test_images = possible_images[:5]
    
    if test_images:
        print(f"📁 Images de test trouvées: {len(test_images)}")
        
        # Test extraction simple
        success = tester.test_extract_single_file(str(test_images[0]))
        
        if success and len(test_images) > 1:
            print("\n" + "-" * 40)
            # Test extraction batch
            tester.test_batch_extract([str(img) for img in test_images])
    else:
        print("⚠️ Aucune image de test trouvée")
        print("   Placez des images .jpg, .jpeg ou .png dans le dossier pour tester")
    
    print("\n" + "=" * 60)
    print("🎯 Tests terminés")

if __name__ == "__main__":
    main()