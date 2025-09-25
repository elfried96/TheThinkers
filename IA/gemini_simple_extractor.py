#!/usr/bin/env python3
"""
Extracteur Gemini simplifié avec requêtes HTTP directes
Évite les problèmes d'installation de dépendances
"""

import os
import sys
import cv2
import numpy as np
import base64
import json
import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
# MORPHOLOGICAL_ENHANCEMENT - Intégration preprocessing amélioré
import cv2
import numpy as np


# Import preprocessing avancé (garder existant)
try:
    from advanced_preprocessor import AdvancedImagePreprocessor
except ImportError:
    print("⚠️ Advanced preprocessor non trouvé, utilisation preprocessing simple")
    AdvancedImagePreprocessor = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiSimpleExtractor:
    """Extracteur Gemini avec API HTTP directe"""
    
    def __init__(self, api_key: str = None):
        """Initialise l'extracteur Gemini simple"""
        
        # Charger clé API depuis .env
        if api_key:
            self.api_key = api_key
        else:
            # Lire directement le fichier .env
            try:
                with open('.env', 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if line.startswith('GOOGLE_API_KEY='):
                            self.api_key = line.split('=', 1)[1].strip().strip('"')
                            break
                    else:
                        raise ValueError("GOOGLE_API_KEY non trouvée dans .env")
            except FileNotFoundError:
                raise ValueError("Fichier .env non trouvé")
        
        if not self.api_key:
            raise ValueError("❌ Clé API Google manquante")
        
        # URL API Gemini
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        # Preprocessing avancé si disponible
        if AdvancedImagePreprocessor:
            self.preprocessor = AdvancedImagePreprocessor()
            print("✅ Preprocessing avancé activé")
        else:
            self.preprocessor = None
            print("⚠️ Preprocessing simple utilisé")
        
        # Patterns coordonnées (garder optimisés)
        self.coordinate_patterns = [
            r'([BP]\d+)[:\s]*(\d{6,7}[\.,]?\d*)[,\s]+(\d{6,8}[\.,]?\d*)',
            r'(\d{6,7}[\.,]?\d*)[,\s]+(\d{6,8}[\.,]?\d*)',
            r'X[:\s]*(\d{6,7}[\.,]?\d*)[,\s]*Y[:\s]*(\d{6,8}[\.,]?\d*)',
        ]
        
        # Limites UTM 31N Bénin
        self.utm_bounds = {
            'x_min': 200000, 'x_max': 600000,
            'y_min': 600000, 'y_max': 1400000
        }
        
        logger.info("✅ Gemini Simple Extractor initialisé")
    
    def extract_coordinates(self, image_path: str, use_preprocessing: bool = True) -> Dict[str, Any]:
        """Extraction coordonnées avec Gemini API directe"""
        
        print(f"\n🎯 GEMINI SIMPLE EXTRACTION")
        print(f"📄 Image: {Path(image_path).name}")
        
        start_time = datetime.now()
        
        try:
            # 1. Charger image
            image = cv2.imread(image_path)
            if image is None:
                return self._create_error_result(f"Impossible de charger: {image_path}")
            
            print(f"✅ Image chargée: {image.shape[1]}x{image.shape[0]}")
            
            # 2. Preprocessing ultra-adaptatif
            if use_preprocessing:
                # Essayer ultra-preprocessor d'abord
                try:
                    from ultra_preprocessor import UltraPreprocessor
                    ultra = UltraPreprocessor()
                    enhanced_image, ultra_metadata = ultra.enhance_difficult_image(image)
                    print(f"✅ Ultra-preprocessing: {len(ultra_metadata['steps_applied'])} étapes (difficulté: {ultra_metadata['difficulty_score']:.3f})")
                    
                except ImportError:
                    print("⚠️ Ultra-preprocessor non disponible")
                    if self.preprocessor:
                        quality_score = self._estimate_quality(image)
                        enhanced_image = self.preprocessor.enhance_image_for_ocr(image, quality_score)
                        print(f"✅ Preprocessing avancé (qualité: {quality_score:.3f})")
                    else:
                        enhanced_image = self._simple_preprocessing(image)
                        print("✅ Preprocessing simple appliqué")
                except Exception as e:
                    print(f"⚠️ Erreur ultra-preprocessing: {e}")
                    if self.preprocessor:
                        quality_score = self._estimate_quality(image)
                        enhanced_image = self.preprocessor.enhance_image_for_ocr(image, quality_score)
                        print(f"✅ Fallback preprocessing avancé (qualité: {quality_score:.3f})")
                    else:
                        enhanced_image = self._simple_preprocessing(image)
                        print("✅ Fallback preprocessing simple")
                        
                        # Enhancement morphologique supplémentaire pour cas difficiles
                        try:
                            quality_score = self._estimate_quality(image)
                            if quality_score < 0.6:  # Image difficile
                                morpho_enhanced = self._morphological_enhancement(enhanced_image, 1.0 - quality_score)
                                enhanced_image = morpho_enhanced
                                print("✅ Enhancement morphologique appliqué")
                        except Exception as morph_e:
                            print(f"⚠️ Erreur morphologique: {morph_e}")
            else:
                enhanced_image = image
            
            # 3. Préparer pour API
            image_base64 = self._image_to_base64(enhanced_image)
            
            # 4. Appel API Gemini
            gemini_response = self._call_gemini_api(image_base64, image_path)
            
            # 5. Parser coordonnées
            coordinates = self._parse_coordinates(gemini_response['text'])
            
            # 6. Validation géométrique des coordonnées
            if len(coordinates) > 0:
                try:
                    from coordinate_validator import CoordinateValidator
                    validator = CoordinateValidator()
                    validation = validator.validate_coordinates(coordinates, image_path)
                    
                    # Appliquer corrections si confiance élevée
                    if validation.get('corrections'):
                        corrected_coordinates = coordinates.copy()
                        applied_corrections = []
                        
                        for correction in validation['corrections']:
                            if correction.get('confidence', 0) > 0.8:  # 80% confiance minimum
                                point_id = correction['point_id']
                                field = correction['field']
                                new_value = correction['suggested_value']
                                
                                # Appliquer correction
                                for coord in corrected_coordinates:
                                    if coord.get('point_id') == point_id:
                                        old_value = coord[field]
                                        coord[field] = new_value
                                        applied_corrections.append({
                                            'point_id': point_id,
                                            'field': field,
                                            'old_value': old_value,
                                            'new_value': new_value,
                                            'confidence': correction['confidence']
                                        })
                                        print(f"🔧 CORRECTION APPLIQUÉE: {point_id}.{field} {old_value:.2f} → {new_value:.2f} (conf: {correction['confidence']:.1%})")
                        
                        if applied_corrections:
                            coordinates = corrected_coordinates
                            print(f"✅ {len(applied_corrections)} corrections appliquées")
                    
                except ImportError:
                    print("⚠️ Validateur non disponible - coordonnées non validées")
                    validation = None
                except Exception as e:
                    print(f"⚠️ Erreur validation: {e}")
                    validation = None
            else:
                validation = None
            
            # 7. Résultat final
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': len(coordinates) > 0,
                'coordinates': coordinates,
                'coordinate_count': len(coordinates),
                'ocr_text': gemini_response['text'][:500] + "..." if len(gemini_response['text']) > 500 else gemini_response['text'],
                'processing_time': processing_time,
                'method': 'gemini_simple',
                'image_path': image_path,
                'timestamp': datetime.now().isoformat(),
                'validation': validation
            }
            
            print(f"🏆 TERMINÉ: {len(coordinates)} coordonnées trouvées en {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Erreur extraction: {e}")
            return self._create_error_result(str(e))
    
    def _estimate_quality(self, image: np.ndarray) -> float:
        """Estimation rapide de la qualité d'image"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Netteté (variance Laplacien)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(sharpness / 1000, 1.0)
            
            # Contraste
            contrast = gray.std()
            contrast_score = min(contrast / 100, 1.0)
            
            # Score combiné
            quality = (sharpness_score * 0.6 + contrast_score * 0.4)
            return quality
            
        except:
            return 0.5  # Qualité moyenne par défaut
    
    def _simple_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing simple sans dépendances avancées"""
        
        # Convertir en niveaux de gris
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Amélioration contraste simple
        enhanced = cv2.equalizeHist(gray)
        
        # Débruitage léger
        denoised = cv2.medianBlur(enhanced, 3)
        
        # Redimensionnement si trop petit
        height, width = denoised.shape
        if width < 1000 or height < 1000:
            scale = max(1000/width, 1000/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            denoised = cv2.resize(denoised, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        return denoised
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """Convertit image en base64 pour API"""
        
        # Encoder en JPEG
        success, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        if not success:
            raise ValueError("Erreur encodage image")
        
        # Base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        print(f"📤 Image encodée: {len(image_base64)} caractères base64")
        
        return image_base64
    
    def _call_gemini_api(self, image_base64: str, image_path: str) -> Dict[str, Any]:
        """Appel direct API Gemini avec requêtes HTTP"""
        
        # Prompt spécialisé cadastral
        prompt = f'''Analyse ce document cadastral/foncier et extrait TOUTES les coordonnées UTM.

TÂCHES SPÉCIFIQUES:
1. Trouve tous les tableaux de coordonnées
2. Cherche les points: B1, B2, B3, P1, P2, Point 1, etc.
3. Extrait TOUTES les paires de nombres 6-8 chiffres (coordonnées X,Y)
4. Sois très précis avec les décimales (utilise . comme séparateur)
5. Ignore surfaces, échelles, numéros de titre

RÉPONSE FORMAT JSON:
{{
  "coordonnees": [
    {{"point": "B1", "x": 396027.30, "y": 726474.99}},
    {{"point": "B2", "x": 396098.92, "y": 726433.00}}
  ],
  "texte_complet": "tout le texte extrait..."
}}

Document: {Path(image_path).name}'''
        
        # Payload API
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 4096,
            }
        }
        
        print("🔍 Appel API Gemini...")
        
        try:
            # Convertir payload en JSON
            data = json.dumps(payload).encode('utf-8')
            
            # Créer requête
            req = urllib.request.Request(
                self.api_url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(len(data))
                }
            )
            
            # Appel API
            with urllib.request.urlopen(req, timeout=60) as response:
                response_data = response.read().decode('utf-8')
                result = json.loads(response_data)
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ Réponse reçue: {len(text)} caractères")
                    
                    return {
                        'text': text,
                        'success': True
                    }
                else:
                    raise ValueError("Pas de candidat dans la réponse Gemini")
                
        except Exception as e:
            logger.error(f"Erreur appel API: {e}")
            raise
    
    def _parse_coordinates(self, gemini_text: str) -> List[Dict[str, Any]]:
        """Parse coordonnées depuis réponse Gemini"""
        
        coordinates = []
        print("🔍 Parsing coordonnées...")
        
        # 1. Essayer de parser JSON si présent
        try:
            # Chercher bloc JSON dans la réponse
            json_match = re.search(r'```json\s*({.*?})\s*```', gemini_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r'({.*?"coordonnees".*?})', gemini_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                if 'coordonnees' in data:
                    for coord in data['coordonnees']:
                        if 'x' in coord and 'y' in coord:
                            x, y = float(coord['x']), float(coord['y'])
                            
                            if self._validate_utm(x, y):
                                coordinates.append({
                                    'point_id': coord.get('point', f'Point_{len(coordinates)+1}'),
                                    'x': x,
                                    'y': y,
                                    'format': 'UTM',
                                    'coordinate_system': 'EPSG:32631',
                                    'confidence': 0.95,
                                    'source': 'gemini_json'
                                })
                                print(f"  ✅ JSON: {coord.get('point')}: X={x:.2f}, Y={y:.2f}")
                
                if coordinates:
                    return coordinates
        
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ⚠️ Parsing JSON échoué: {e}")
        
        # 2. Fallback: patterns regex classiques
        print("  🔄 Fallback patterns regex...")
        
        for pattern in self.coordinate_patterns:
            matches = re.finditer(pattern, gemini_text)
            
            for match in matches:
                try:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        point_id, x_str, y_str = groups
                    else:
                        point_id = f"Point_{len(coordinates)+1}"
                        x_str, y_str = groups
                    
                    x = float(x_str.replace(',', '.'))
                    y = float(y_str.replace(',', '.'))
                    
                    if self._validate_utm(x, y):
                        # Éviter doublons
                        if not any(abs(c['x'] - x) < 0.1 and abs(c['y'] - y) < 0.1 
                                 for c in coordinates):
                            coordinates.append({
                                'point_id': point_id,
                                'x': x,
                                'y': y,
                                'format': 'UTM',
                                'coordinate_system': 'EPSG:32631',
                                'confidence': 0.85,
                                'source': 'gemini_regex'
                            })
                            print(f"  ✅ Regex: {point_id}: X={x:.2f}, Y={y:.2f}")
                
                except (ValueError, IndexError):
                    continue
        
        return coordinates
    
    def _validate_utm(self, x: float, y: float) -> bool:
        """Validation coordonnées UTM"""
        return (self.utm_bounds['x_min'] <= x <= self.utm_bounds['x_max'] and 
                self.utm_bounds['y_min'] <= y <= self.utm_bounds['y_max'])
    

    
    def _morphological_enhancement(self, image: np.ndarray, difficulty: float) -> np.ndarray:
        """
        Enhancement morphologique pour corriger confusions 0/6, 4/1, 9/0
        MORPHOLOGICAL_ENHANCEMENT
        """
        
        print(f"🔧 Enhancement morphologique (difficulté: {difficulty:.3f})")
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 1. Débruitage morphologique si nécessaire
        if difficulty > 0.4:
            # Opening + Closing pour nettoyer
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            cleaned = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.medianBlur(cleaned, 3)
            gray = cleaned
        
        # 2. Enhancement de contraste adaptatif
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # 3. Corrections spécialisées pour chiffres
        if difficulty > 0.3:
            enhanced = self._fix_digit_confusions(enhanced)
        
        # 4. Sharpening final adaptatif
        intensity = min(1.5, 0.5 + difficulty)
        if difficulty > 0.6:
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * intensity / 8
        else:
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) * intensity / 4
        
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        result = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return result
    
    def _fix_digit_confusions(self, image: np.ndarray) -> np.ndarray:
        """
        Corrections spécialisées pour confusions 0/6, 4/1, 9/0
        """
        
        # Binarisation double
        binary1 = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        binary2 = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 5)
        binary = cv2.bitwise_and(binary1, binary2)
        
        # Kernels spécialisés
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        fine_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        
        # Fermer les gaps critiques
        closed_v = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, vertical_kernel)
        closed_h = cv2.morphologyEx(closed_v, cv2.MORPH_CLOSE, horizontal_kernel)
        
        # Nettoyer et épaissir légèrement
        cleaned = cv2.morphologyEx(closed_h, cv2.MORPH_OPEN, fine_kernel)
        thickened = cv2.dilate(cleaned, fine_kernel, iterations=1)
        
        # Reconvertir en niveaux de gris
        result = cv2.bitwise_not(thickened) if np.mean(thickened) > 127 else thickened
        return result
    
    def _create_error_result(self, error: str) -> Dict[str, Any]:
        """Résultat d'erreur"""
        return {
            'success': False,
            'error': error,
            'coordinates': [],
            'coordinate_count': 0,
            'method': 'gemini_simple',
            'timestamp': datetime.now().isoformat()
        }


def test_gemini_simple():
    """Test extracteur Gemini simple"""
    
    try:
        # Initialiser
        extractor = GeminiSimpleExtractor()
        
        # Images test
        test_images = [
            "Data_Hackathon_IA_2025/Training_Data/leve124.png",  # Référence (6 points)
            "Data_Hackathon_IA_2025/Training_Data/leve2.jpg",    # Difficile (0 avec Tesseract)
        ]
        
        for image_path in test_images:
            if Path(image_path).exists():
                print(f"\n{'='*60}")
                result = extractor.extract_coordinates(image_path)
                
                if result['success']:
                    print(f"🎯 {Path(image_path).name}: {result['coordinate_count']} coordonnées")
                    for coord in result['coordinates'][:5]:  # Top 5
                        print(f"  - {coord['point_id']}: X={coord['x']:.2f}, Y={coord['y']:.2f}")
                else:
                    print(f"❌ {Path(image_path).name}: {result.get('error', 'Échec')}")
            else:
                print(f"❌ Non trouvé: {image_path}")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")


if __name__ == "__main__":
    test_gemini_simple()