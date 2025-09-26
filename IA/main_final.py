#!/usr/bin/env python3
"""
API FINALE - HACKATHON IA 2025
Pipeline complète d'extraction de coordonnées avec FastAPI
Intègre : Gemini, Preprocessing, Superposition spatiale, Conversion EPSG
"""

import os
import sys
import json
import base64
import tempfile
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Dependencies
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import requests
from dotenv import load_dotenv

# Conversion coordonnées
try:
    import pyproj
    from pyproj import Transformer
    COORDINATE_CONVERSION_AVAILABLE = True
except ImportError:
    COORDINATE_CONVERSION_AVAILABLE = False
    print("⚠️ PyProj non disponible - conversion coordonnées désactivée")

# Géospatial pour superposition
try:
    import geopandas as gpd
    from shapely.geometry import Point
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    print("⚠️ GeoPandas/Shapely non disponible - superposition désactivée")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger variables d'environnement
load_dotenv()

class CoordinateConverter:
    """Convertisseur de coordonnées UTM vers EPSG:4326 (WGS84)"""
    
    def __init__(self):
        self.transformers = {}
        
    def convert_utm_to_wgs84(self, x: float, y: float, utm_zone: int = 31) -> Tuple[float, float]:
        """Convertit UTM vers WGS84 (latitude, longitude)"""
        if not COORDINATE_CONVERSION_AVAILABLE:
            return None, None
            
        try:
            transformer_key = f"utm_{utm_zone}"
            if transformer_key not in self.transformers:
                # UTM Zone 31N vers WGS84 - Correction du format EPSG
                utm_epsg = f"EPSG:326{utm_zone:02d}" if utm_zone < 60 else f"EPSG:327{utm_zone-60:02d}"
                self.transformers[transformer_key] = Transformer.from_crs(
                    utm_epsg,      # UTM 31N = EPSG:32631
                    "EPSG:4326",   # WGS84
                    always_xy=True
                )
            
            transformer = self.transformers[transformer_key]
            lon, lat = transformer.transform(x, y)
            return lat, lon
            
        except Exception as e:
            logger.error(f"Erreur conversion coordonnées: {e}")
            return None, None
    
    def auto_detect_utm_zone(self, x: float) -> int:
        """Détecte automatiquement la zone UTM basée sur la coordonnée X"""
        # Zone UTM approximative basée sur la coordonnée X
        # Zone 31N pour le Bénin/Afrique de l'Ouest
        if 400000 <= x <= 500000:
            return 31
        elif 500000 <= x <= 600000:
            return 32
        else:
            return 31  # Défaut pour le Bénin

class GeminiExtractor:
    """Extracteur Gemini simplifié avec API HTTP directe"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY non trouvée dans .env")
        
        # URLs pour différents modèles Gemini (basé sur les modèles disponibles)
        # Ordre de préférence : gemini-2.0-flash fonctionne !
        self.model_urls = [
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-002:generateContent?key={self.api_key}",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        ]
        self.current_model_index = 0
    
    def extract_coordinates(self, image_path: str) -> List[Dict]:
        """Extrait coordonnées d'une image via Gemini"""
        try:
            # Encoder l'image en base64
            with open(image_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Prompt ultra-précis pour éviter les coordonnées fausses
            prompt = """
            Tu es un expert en OCR de coordonnées géographiques. Extrait UNIQUEMENT les coordonnées qui sont CLAIREMENT VISIBLES et LISIBLES dans cette image.
            
            RÈGLES STRICTES :
            1. Extrait SEULEMENT les coordonnées UTM explicitement écrites dans l'image
            2. Format UTM : X (6-7 chiffres), Y (6-7 chiffres) avec décimales
            3. NE PAS inventer, calculer ou estimer de coordonnées
            4. NE PAS extraire de nombres qui ne sont pas des coordonnées (dates, références, etc.)
            5. Ignore les valeurs rondes suspectes (ex: 427122.0) sauf si clairement écrites
            
            EXEMPLES VALIDES (si visible dans l'image) :
            - 427094.7, 712773.67
            - X: 427110.61 Y: 712767.66
            - 427103.58 ; 712748.94
            
            EXEMPLES INVALIDES (à ignorer) :
            - Dates : 2025, 2024
            - Références : REF123, N°456
            - Valeurs estimées ou calculées
            
            RETOURNE EXACTEMENT au format JSON :
            [{"x": 427094.7, "y": 712773.67}]
            
            Si aucune coordonnée visible, retourne : []
            IMPORTANT : Sois conservateur, mieux vaut manquer une coordonnée que d'en inventer une fausse.
            """
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_data
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.0,  # Plus déterministe
                    "topK": 1,
                    "topP": 0.1,
                    "maxOutputTokens": 2000  # Plus de tokens pour réponses longues
                }
            }
            
            # Essayer différents endpoints Gemini si nécessaire
            response = None
            last_error = None
            
            for i, api_url in enumerate(self.model_urls):
                try:
                    logger.info(f"Tentative avec modèle {i+1}/{len(self.model_urls)}")
                    response = requests.post(
                        api_url, 
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=45
                    )
                    
                    if response.status_code == 200:
                        self.current_model_index = i  # Se souvenir du modèle qui marche
                        break
                    else:
                        last_error = f"Erreur {response.status_code}: {response.text}"
                        logger.warning(f"Modèle {i+1} échoué: {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    logger.warning(f"Erreur réseau modèle {i+1}: {e}")
                    continue
            
            if not response or response.status_code != 200:
                logger.error(f"Tous les modèles Gemini ont échoué. Dernière erreur: {last_error}")
                return []
            
            result = response.json()
            text_response = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            # Parser et valider les coordonnées
            raw_coords = self._parse_coordinates_response(text_response)
            validated_coords = self._validate_coordinates(raw_coords)
            
            logger.info(f"Coordonnées brutes: {len(raw_coords)}, Validées: {len(validated_coords)}")
            return validated_coords
            
        except Exception as e:
            logger.error(f"Erreur extraction Gemini: {e}")
            return []
    
    def _parse_coordinates_response(self, text: str) -> List[Dict]:
        """Parse la réponse texte pour extraire coordonnées JSON avec fallbacks multiples"""
        logger.info(f"Réponse Gemini brute: {text[:200]}...")  # Log pour debug
        
        try:
            # Nettoyer le texte
            text = text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            # Essayer de parser le JSON directement
            coords = json.loads(text)
            if isinstance(coords, list):
                logger.info(f"JSON parsing réussi: {len(coords)} coordonnées")
                return coords
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing échoué: {e}")
            
            # Fallback 1: Extraction regex format JSON
            import re
            json_pattern = r'["\']?x["\']?\s*:\s*([0-9]+\.?[0-9]*),?\s*["\']?y["\']?\s*:\s*([0-9]+\.?[0-9]*)'
            matches = re.findall(json_pattern, text, re.IGNORECASE)
            if matches:
                coords = [{"x": float(x), "y": float(y)} for x, y in matches]
                logger.info(f"Regex JSON réussi: {len(coords)} coordonnées")
                return coords
                
            # Fallback 2: Extraction coordonnées UTM brutes
            utm_pattern = r'(4[0-5][0-9]{4}[\.,]?[0-9]*)[\s,;:\-_]+(7[0-8][0-9]{4}[\.,]?[0-9]*)'
            utm_matches = re.findall(utm_pattern, text)
            if utm_matches:
                coords = [{"x": float(x.replace(',', '.')), "y": float(y.replace(',', '.'))} for x, y in utm_matches]
                logger.info(f"Regex UTM réussi: {len(coords)} coordonnées")
                return coords
            
            # Fallback 3: Extraction plus flexible
            flex_pattern = r'(4[0-9]{5,6}[\.,]?[0-9]*)\D+(7[0-9]{5,6}[\.,]?[0-9]*)'
            flex_matches = re.findall(flex_pattern, text)
            if flex_matches:
                coords = [{"x": float(x.replace(',', '.')), "y": float(y.replace(',', '.'))} for x, y in flex_matches]
                logger.info(f"Regex flexible réussi: {len(coords)} coordonnées")
                return coords
        
        logger.warning("Aucune coordonnée extraite avec toutes les méthodes")
        return []
    
    def _validate_coordinates(self, coordinates: List[Dict]) -> List[Dict]:
        """Valide les coordonnées pour éliminer les fausses détections"""
        if not coordinates:
            return []
        
        validated = []
        
        for coord in coordinates:
            try:
                x = float(coord.get('x', 0))
                y = float(coord.get('y', 0))
                
                # Critères de validation pour coordonnées UTM Bénin/Afrique de l'Ouest
                valid = True
                
                # 1. Plages valides pour UTM Zone 31N (Bénin)
                if not (400000 <= x <= 500000):
                    logger.warning(f"Coordonnée X invalide: {x} (hors plage 400000-500000)")
                    valid = False
                    
                if not (700000 <= y <= 800000):
                    logger.warning(f"Coordonnée Y invalide: {y} (hors plage 700000-800000)")
                    valid = False
                
                # 2. Éviter les valeurs trop rondes (souvent fausses)
                # Sauf si c'est exactement une valeur attendue
                if x == int(x) and y == int(y):  # Les deux sont des entiers
                    # Vérifier si c'est une coordonnée "suspecte" ronde
                    if str(x).endswith('22.0') or str(y).endswith('35.0') or str(y).endswith('85.0'):
                        logger.warning(f"Coordonnée suspecte (trop ronde): X={x}, Y={y}")
                        valid = False
                
                # 3. Éviter les doublons exacts
                for existing in validated:
                    if (abs(existing['x'] - x) < 0.01 and abs(existing['y'] - y) < 0.01):
                        logger.warning(f"Coordonnée dupliquée ignorée: X={x}, Y={y}")
                        valid = False
                        break
                
                # 4. Vérifier cohérence des décimales
                # Les vraies coordonnées UTM ont généralement 1-3 décimales maximum
                x_decimals = len(str(x).split('.')[-1]) if '.' in str(x) else 0
                y_decimals = len(str(y).split('.')[-1]) if '.' in str(y) else 0
                
                if x_decimals > 3 or y_decimals > 3:
                    logger.warning(f"Trop de décimales (suspect): X={x} ({x_decimals}), Y={y} ({y_decimals})")
                    # Ne pas rejeter, juste signaler
                
                if valid:
                    validated.append({'x': x, 'y': y})
                    logger.info(f"Coordonnée validée: X={x}, Y={y}")
                else:
                    logger.warning(f"Coordonnée rejetée: X={x}, Y={y}")
                    
            except (ValueError, TypeError) as e:
                logger.error(f"Erreur validation coordonnée {coord}: {e}")
                continue
        
        logger.info(f"Validation terminée: {len(coordinates)} -> {len(validated)} coordonnées")
        return validated

class SpatialOverlay:
    """Superposition spatiale avec données GeoJSON"""
    
    def __init__(self, geojson_dir: str = "Data_Hackathon_IA_2025/couche"):
        self.geojson_dir = Path(geojson_dir)
        self.layer_names = [
            'aif', 'air_proteges', 'dpl', 'dpm', 'enregistrement individuel',
            'litige', 'parcelles', 'restriction', 'tf_demembres', 'tf_en_cours',
            'tf_etat', 'titre_reconstitue', 'zone_inondable'
        ]
        self.layers_cache = {}
        
    def check_overlays(self, coordinates: List[Dict]) -> Dict[str, str]:
        """Vérifie superposition coordonnées avec couches géographiques"""
        if not GEOSPATIAL_AVAILABLE or not coordinates:
            return {layer: "NON" for layer in self.layer_names}
        
        overlays = {layer: "NON" for layer in self.layer_names}
        
        try:
            # Charger les couches si nécessaire
            self._load_layers()
            
            # Créer points à partir des coordonnées
            points = [Point(coord["x"], coord["y"]) for coord in coordinates]
            
            # Vérifier intersection avec chaque couche
            for layer_name in self.layer_names:
                if layer_name in self.layers_cache:
                    layer_gdf = self.layers_cache[layer_name]
                    for point in points:
                        if layer_gdf.contains(point).any():
                            overlays[layer_name] = "OUI"
                            break
            
        except Exception as e:
            logger.error(f"Erreur superposition spatiale: {e}")
        
        return overlays
    
    def _load_layers(self):
        """Charge les couches GeoJSON en cache"""
        for layer_name in self.layer_names:
            if layer_name not in self.layers_cache:
                geojson_file = self.geojson_dir / f"{layer_name}.geojson"
                if geojson_file.exists():
                    try:
                        self.layers_cache[layer_name] = gpd.read_file(geojson_file)
                    except Exception as e:
                        logger.warning(f"Impossible de charger {layer_name}: {e}")

class ImagePreprocessor:
    """Préprocessing d'images pour améliorer l'extraction"""
    
    @staticmethod
    def enhance_image(image_path: str, output_path: str) -> str:
        """Améliore une image pour l'extraction OCR/Gemini"""
        try:
            # Charger image
            img = cv2.imread(image_path)
            if img is None:
                return image_path
            
            # Préprocessing basique
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Amélioration contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Débruitage
            denoised = cv2.fastNlMeansDenoising(enhanced)
            
            # Seuillage adaptatif
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Sauvegarder
            cv2.imwrite(output_path, thresh)
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur préprocessing: {e}")
            return image_path

# Initialisation composants
app = FastAPI(
    title="API Extraction Coordonnées - Hackathon IA 2025",
    description="Pipeline complète d'extraction de coordonnées géographiques",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instances globales
gemini_extractor = GeminiExtractor()
spatial_overlay = SpatialOverlay()
coordinate_converter = CoordinateConverter()
preprocessor = ImagePreprocessor()

@app.get("/")
async def root():
    """Endpoint racine - informations API"""
    return {
        "message": "API Extraction Coordonnées - Hackathon IA 2025",
        "version": "1.0.0",
        "endpoints": {
            "/extract": "POST - Upload fichier (image/PDF) pour extraction",
            "/health": "GET - Statut de l'API"
        },
        "features": {
            "gemini_extraction": True,
            "coordinate_conversion": COORDINATE_CONVERSION_AVAILABLE,
            "spatial_overlay": GEOSPATIAL_AVAILABLE
        }
    }

@app.get("/health")
async def health_check():
    """Vérification santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini_api": bool(os.getenv('GOOGLE_API_KEY')),
            "coordinate_conversion": COORDINATE_CONVERSION_AVAILABLE,
            "spatial_overlay": GEOSPATIAL_AVAILABLE
        }
    }

@app.post("/extract")
async def extract_coordinates(file: UploadFile = File(...)):
    """
    Extraction complète de coordonnées depuis image/PDF
    
    Retourne format JSON avec :
    - Coordonnées UTM originales
    - Coordonnées EPSG:4326 (lat/lon)
    - Superposition avec couches géographiques
    """
    
    # Validation fichier
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier manquant")
    
    # Extensions supportées
    supported_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.pdf'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Format non supporté. Formats acceptés: {supported_extensions}"
        )
    
    # Traitement du fichier
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Sauvegarder fichier temporaire
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Si PDF, convertir en image (logique simplifiée)
            if file_extension == '.pdf':
                # Pour l'instant, retourner erreur - implémenter conversion PDF si nécessaire
                raise HTTPException(status_code=400, detail="Support PDF en cours de développement")
            
            # Préprocessing de l'image
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as processed_file:
                processed_path = preprocessor.enhance_image(temp_file_path, processed_file.name)
            
            # Extraction coordonnées avec Gemini
            coordinates_utm = gemini_extractor.extract_coordinates(processed_path)
            
            if not coordinates_utm:
                return {
                    "filename": file.filename,
                    "timestamp": datetime.now().isoformat(),
                    "extraction_success": False,
                    "error": "Aucune coordonnée détectée",
                    "coordinates": "[]",
                    "coordinates_wgs84": [],
                    # Toutes les couches à NON par défaut
                    "aif": "NON",
                    "air_proteges": "NON",
                    "dpl": "NON",
                    "dpm": "NON",
                    "enregistrement_individuel": "NON",
                    "litige": "NON",
                    "parcelles": "NON",
                    "restriction": "NON",
                    "tf_demembres": "NON",
                    "tf_en_cours": "NON",
                    "tf_etat": "NON",
                    "titre_reconstitue": "NON",
                    "zone_inondable": "NON",
                    "metadata": {
                        "coordinate_count": 0
                    }
                }
            
            # Conversion EPSG:4326 si disponible avec détection automatique zone UTM
            coordinates_wgs84 = []
            if COORDINATE_CONVERSION_AVAILABLE and coordinates_utm:
                for coord in coordinates_utm:
                    # Auto-détection zone UTM
                    utm_zone = coordinate_converter.auto_detect_utm_zone(coord["x"])
                    lat, lon = coordinate_converter.convert_utm_to_wgs84(coord["x"], coord["y"], utm_zone)
                    if lat is not None and lon is not None:
                        coordinates_wgs84.append({
                            "latitude": round(lat, 8),
                            "longitude": round(lon, 8),
                            "utm_zone_detected": utm_zone
                        })
            
            # Superposition spatiale
            spatial_overlays = spatial_overlay.check_overlays(coordinates_utm)
            
            # Format de sortie final - Compatible avec submissions_reordered.csv
            result = {
                "filename": file.filename,
                "timestamp": datetime.now().isoformat(),
                "extraction_success": True,
                
                # Coordonnées au format JSON string (comme dans le CSV)
                "coordinates": json.dumps(coordinates_utm),
                
                # Coordonnées converties EPSG:4326 (WGS84)
                "coordinates_wgs84": coordinates_wgs84,
                
                # Couches d'appartenance (format CSV)
                "aif": spatial_overlays.get("aif", "NON"),
                "air_proteges": spatial_overlays.get("air_proteges", "NON"),
                "dpl": spatial_overlays.get("dpl", "NON"),
                "dpm": spatial_overlays.get("dpm", "NON"),
                "enregistrement_individuel": spatial_overlays.get("enregistrement individuel", "NON"),
                "litige": spatial_overlays.get("litige", "NON"),
                "parcelles": spatial_overlays.get("parcelles", "NON"),
                "restriction": spatial_overlays.get("restriction", "NON"),
                "tf_demembres": spatial_overlays.get("tf_demembres", "NON"),
                "tf_en_cours": spatial_overlays.get("tf_en_cours", "NON"),
                "tf_etat": spatial_overlays.get("tf_etat", "NON"),
                "titre_reconstitue": spatial_overlays.get("titre_reconstitue", "NON"),
                "zone_inondable": spatial_overlays.get("zone_inondable", "NON"),
                
                # Métadonnées
                "metadata": {
                    "coordinate_count": len(coordinates_utm),
                    "coordinate_system_utm": "EPSG:32631",  # UTM 31N
                    "coordinate_system_wgs84": "EPSG:4326",
                    "preprocessing_applied": True,
                    "extraction_method": "gemini-1.5-flash"
                }
            }
            
            return JSONResponse(content=result)
            
        finally:
            # Nettoyage fichiers temporaires
            try:
                os.unlink(temp_file_path)
                if processed_path != temp_file_path:
                    os.unlink(processed_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Erreur traitement fichier {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur traitement: {str(e)}")

@app.post("/batch_extract")
async def batch_extract(files: List[UploadFile] = File(...)):
    """Extraction par lot de plusieurs fichiers"""
    
    if len(files) > 10:  # Limite sécurité
        raise HTTPException(status_code=400, detail="Maximum 10 fichiers par batch")
    
    results = []
    
    for file in files:
        try:
            # Réutiliser la logique d'extraction individuelle
            result = await extract_coordinates(file)
            results.append(result)
        except Exception as e:
            results.append({
                "filename": file.filename,
                "extraction_success": False,
                "error": str(e)
            })
    
    return {
        "batch_timestamp": datetime.now().isoformat(),
        "total_files": len(files),
        "successful_extractions": sum(1 for r in results if r.get("extraction_success", False)),
        "results": results
    }

if __name__ == "__main__":
    # Vérification configuration
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY manquante dans .env")
        sys.exit(1)
    
    print("🚀 Lancement API Extraction Coordonnées...")
    print(f"📍 Conversion coordonnées: {'✅' if COORDINATE_CONVERSION_AVAILABLE else '❌'}")
    print(f"🗺️ Superposition spatiale: {'✅' if GEOSPATIAL_AVAILABLE else '❌'}")
    
    # Lancement serveur
    uvicorn.run(
        "main_final:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )