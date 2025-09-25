#!/usr/bin/env python3
"""
Ultra-Preprocessor pour images cadastrales difficiles
Traitement spécialisé pour cas extrêmes comme leve262
"""

import cv2
import numpy as np
from pathlib import Path
import math
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class UltraPreprocessor:
    """Préprocesseur ultra-avancé pour cas difficiles"""
    
    def __init__(self):
        """Initialise l'ultra-preprocesseur"""
        
        self.target_dpi = 600
        self.min_size = 2000
        
        print("🚀 ULTRA-PREPROCESSOR INITIALISÉ")
        print("🎯 Spécialisé pour cas extrêmes")
        print("💪 Correction ombres, déformation, contraste")
    
    def enhance_difficult_image(self, image: np.ndarray, 
                               difficulty_score: float = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Amélioration spécialisée pour images difficiles
        
        Args:
            image: Image source
            difficulty_score: Score de difficulté (0-1)
            
        Returns:
            Tuple (image améliorée, métadonnées)
        """
        
        if difficulty_score is None:
            difficulty_score = self._assess_difficulty(image)
        
        print(f"🔍 ULTRA-PREPROCESSING - Difficulté: {difficulty_score:.3f}")
        
        metadata = {
            'original_shape': image.shape,
            'difficulty_score': difficulty_score,
            'steps_applied': [],
            'improvements': {}
        }
        
        # Pipeline adaptatif selon difficulté (seuils ajustés)
        if difficulty_score > 0.6:
            enhanced = self._extreme_processing(image, metadata)
        elif difficulty_score > 0.25:
            enhanced = self._aggressive_processing(image, metadata)
        else:
            enhanced = self._standard_plus_processing(image, metadata)
        
        # Post-traitement final
        enhanced = self._final_polish(enhanced, metadata)
        
        print(f"✅ Ultra-preprocessing terminé: {len(metadata['steps_applied'])} étapes")
        
        return enhanced, metadata
    
    def _assess_difficulty(self, image: np.ndarray) -> float:
        """Évalue la difficulté de traitement de l'image"""
        
        print("🔍 Évaluation difficulté image...")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 1. Contraste global
        contrast_score = gray.std() / 128.0  # Normalisé 0-1
        
        # 2. Netteté (variance Laplacien)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 1000, 1.0)
        
        # 3. Zones sombres (potentielles ombres)
        dark_pixels = (gray < 50).sum() / gray.size
        shadow_score = min(dark_pixels * 2, 1.0)  # Plus d'ombres = plus difficile
        
        # 4. Uniformité éclairage
        mean_brightness = gray.mean()
        brightness_variance = ((gray - mean_brightness) ** 2).mean()
        lighting_score = min(brightness_variance / 10000, 1.0)
        
        # 5. Détection bordures document
        edges = cv2.Canny(gray, 50, 150)
        edge_density = edges.sum() / edges.size / 255.0
        structure_score = min(edge_density * 5, 1.0)
        
        # Score combiné (plus élevé = plus difficile)
        difficulty = (
            (1 - contrast_score) * 0.3 +      # Faible contraste = difficile
            (1 - sharpness_score) * 0.2 +     # Flou = difficile
            shadow_score * 0.2 +              # Ombres = difficile
            lighting_score * 0.2 +            # Éclairage non-uniforme = difficile
            (1 - structure_score) * 0.1       # Peu de structure = difficile
        )
        
        print(f"  📊 Contraste: {contrast_score:.3f}")
        print(f"  🔍 Netteté: {sharpness_score:.3f}")
        print(f"  🌑 Ombres: {shadow_score:.3f}")
        print(f"  💡 Éclairage: {lighting_score:.3f}")
        print(f"  📐 Structure: {structure_score:.3f}")
        print(f"  🎯 Difficulté finale: {difficulty:.3f}")
        
        return min(max(difficulty, 0.0), 1.0)
    
    def _extreme_processing(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Traitement extrême pour images très difficiles"""
        
        print("🔥 TRAITEMENT EXTRÊME activé")
        
        # Convertir en couleur si nécessaire pour traitement avancé
        if len(image.shape) == 3:
            bgr = image.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # 1. Correction perspective agressive
        corrected = self._aggressive_perspective_correction(bgr, metadata)
        gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)
        
        # 2. Correction éclairage CLAHE multi-échelle
        enhanced = self._multi_scale_clahe(gray, metadata)
        
        # 3. Suppression ombres avancée
        shadow_free = self._advanced_shadow_removal(enhanced, metadata)
        
        # 4. Super-résolution par interpolation bi-cubique
        super_res = self._super_resolution(shadow_free, metadata)
        
        # 5. Débruitage ultra-agressif
        denoised = self._ultra_denoising(super_res, metadata)
        
        # 6. Amélioration contraste adaptatif
        contrast_enhanced = self._adaptive_contrast_enhancement(denoised, metadata)
        
        # 7. Binarisation optimisée pour cadastre
        binary = self._cadastral_binarization(contrast_enhanced, metadata)
        
        return binary
    
    def _aggressive_processing(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Traitement agressif pour images moyennement difficiles"""
        
        print("⚡ TRAITEMENT AGRESSIF activé")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Pipeline agressif mais plus rapide
        corrected = self._perspective_correction(gray, metadata)
        enhanced = self._clahe_enhancement(corrected, metadata)
        shadow_corrected = self._shadow_correction(enhanced, metadata)
        upscaled = self._intelligent_upscaling(shadow_corrected, metadata)
        denoised = self._advanced_denoising(upscaled, metadata)
        final = self._adaptive_binarization(denoised, metadata)
        
        return final
    
    def _standard_plus_processing(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Traitement standard amélioré"""
        
        print("✨ TRAITEMENT STANDARD+ activé")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Pipeline standard optimisé
        enhanced = self._standard_enhancement(gray, metadata)
        upscaled = self._smart_upscaling(enhanced, metadata)
        cleaned = self._noise_reduction(upscaled, metadata)
        binary = self._optimized_binarization(cleaned, metadata)
        
        return binary
    
    def _aggressive_perspective_correction(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Correction perspective ultra-agressive"""
        
        print("  📐 Correction perspective ultra-agressive")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Détection contours du document
        edges = cv2.Canny(gray, 50, 200)
        
        # Fermeture morphologique pour connecter les bords
        kernel = np.ones((5, 5), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Trouver contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Plus grand contour = document
            largest = max(contours, key=cv2.contourArea)
            
            # Approximation polygonale
            epsilon = 0.02 * cv2.arcLength(largest, True)
            approx = cv2.approxPolyDP(largest, epsilon, True)
            
            if len(approx) >= 4:
                # Transformation perspective si 4 coins détectés
                approx = approx.reshape(-1, 2)
                
                # Ordonner les points (haut-gauche, haut-droit, bas-droit, bas-gauche)
                rect = self._order_points(approx[:4])
                
                # Calculer dimensions cible
                width = int(max(
                    np.linalg.norm(rect[1] - rect[0]),
                    np.linalg.norm(rect[2] - rect[3])
                ))
                height = int(max(
                    np.linalg.norm(rect[3] - rect[0]),
                    np.linalg.norm(rect[2] - rect[1])
                ))
                
                # Points destination
                dst = np.array([
                    [0, 0],
                    [width - 1, 0],
                    [width - 1, height - 1],
                    [0, height - 1]
                ], dtype=np.float32)
                
                # Transformation
                M = cv2.getPerspectiveTransform(rect.astype(np.float32), dst)
                corrected = cv2.warpPerspective(image, M, (width, height))
                
                metadata['steps_applied'].append('aggressive_perspective_correction')
                metadata['improvements']['perspective_correction'] = {
                    'corners_detected': len(approx),
                    'correction_applied': True,
                    'new_size': (width, height)
                }
                
                return corrected
        
        # Fallback: correction rotation simple
        angle = self._detect_rotation_angle(gray)
        if abs(angle) > 0.1:
            corrected = self._rotate_image(image, -angle)
            metadata['steps_applied'].append('rotation_correction')
            metadata['improvements']['rotation_correction'] = {'angle': angle}
            return corrected
        
        return image
    
    def _order_points(self, pts):
        """Ordonne les points dans l'ordre: haut-gauche, haut-droit, bas-droit, bas-gauche"""
        rect = np.zeros((4, 2), dtype=np.float32)
        
        # Somme: haut-gauche = min, bas-droit = max
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        # Différence: haut-droit = min, bas-gauche = max
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        return rect
    
    def _multi_scale_clahe(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """CLAHE multi-échelle pour correction éclairage avancée"""
        
        print("  💡 CLAHE multi-échelle")
        
        # CLAHE à différentes échelles
        scales = [8, 16, 32]
        results = []
        
        for scale in scales:
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(scale, scale))
            enhanced = clahe.apply(image)
            results.append(enhanced)
        
        # Moyenne pondérée des résultats
        final = (results[0] * 0.5 + results[1] * 0.3 + results[2] * 0.2).astype(np.uint8)
        
        metadata['steps_applied'].append('multi_scale_clahe')
        return final
    
    def _advanced_shadow_removal(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Suppression ombres avancée"""
        
        print("  🌑 Suppression ombres avancée")
        
        # Détection zones sombres
        kernel = np.ones((50, 50), np.float32) / (50 * 50)
        background = cv2.filter2D(image, -1, kernel)
        
        # Correction additive pour égaliser
        correction = cv2.medianBlur(background, 19)
        corrected = cv2.addWeighted(image, 1.5, correction, -0.5, 0)
        
        # Limiter les valeurs
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        
        metadata['steps_applied'].append('advanced_shadow_removal')
        return corrected
    
    def _super_resolution(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Super-résolution par interpolation avancée"""
        
        print("  🔍 Super-résolution")
        
        height, width = image.shape[:2]
        
        # Calculer facteur d'agrandissement nécessaire
        target_size = max(self.min_size, int(self.target_dpi * 8.5))  # 8.5" = page A4
        factor = max(target_size / width, target_size / height)
        
        if factor > 1.1:  # Seulement si agrandissement significatif
            new_width = int(width * factor)
            new_height = int(height * factor)
            
            # Interpolation bi-cubique pour meilleure qualité
            upscaled = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            metadata['steps_applied'].append('super_resolution')
            metadata['improvements']['super_resolution'] = {
                'factor': factor,
                'new_size': (new_width, new_height)
            }
            
            return upscaled
        
        return image
    
    def _ultra_denoising(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Débruitage ultra-agressif"""
        
        print("  🧹 Débruitage ultra-agressif")
        
        # Multi-pass débruitage
        denoised = image.copy()
        
        # Pass 1: Non-local means
        denoised = cv2.fastNlMeansDenoising(denoised, None, 15, 7, 21)
        
        # Pass 2: Filtre bilatéral
        denoised = cv2.bilateralFilter(denoised, 9, 80, 80)
        
        # Pass 3: Médian pour éliminer bruit impulsif
        denoised = cv2.medianBlur(denoised, 3)
        
        metadata['steps_applied'].append('ultra_denoising')
        return denoised
    
    def _adaptive_contrast_enhancement(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Amélioration contraste adaptatif"""
        
        print("  🌟 Contraste adaptatif")
        
        # Égalisation histogramme adaptatif local
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # Renforcement gamma adaptatif
        mean_val = enhanced.mean()
        if mean_val < 100:  # Image sombre
            gamma = 0.7
        elif mean_val > 180:  # Image claire
            gamma = 1.3
        else:
            gamma = 1.0
        
        if gamma != 1.0:
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
            enhanced = cv2.LUT(enhanced, table)
        
        metadata['steps_applied'].append('adaptive_contrast_enhancement')
        return enhanced
    
    def _cadastral_binarization(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Binarisation optimisée pour documents cadastraux"""
        
        print("  ⚫ Binarisation cadastrale optimisée")
        
        # Méthode adaptative avec post-traitement
        binary = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 15, 8
        )
        
        # Nettoyage morphologique spécialisé
        # Éliminer petits points de bruit
        kernel_noise = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_noise)
        
        # Connecter caractères fragmentés
        kernel_connect = np.ones((2, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_connect)
        
        metadata['steps_applied'].append('cadastral_binarization')
        return binary
    
    def _detect_rotation_angle(self, image: np.ndarray) -> float:
        """Détecte angle de rotation du document"""
        
        # Détection lignes par transformée de Hough
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        angles = []
        if lines is not None:
            for line in lines[:10]:  # Top 10 lignes
                rho, theta = line[0]
                angle = theta * 180 / np.pi
                if angle > 90:
                    angle -= 180
                angles.append(angle)
        
        if angles:
            # Angle médian pour robustesse
            return np.median(angles)
        
        return 0.0
    
    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotation d'image avec préservation du contenu"""
        
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        # Matrice de rotation
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculer nouvelles dimensions
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        
        # Ajuster translation
        M[0, 2] += (new_width / 2) - center[0]
        M[1, 2] += (new_height / 2) - center[1]
        
        # Appliquer rotation
        rotated = cv2.warpAffine(image, M, (new_width, new_height), 
                                borderMode=cv2.BORDER_CONSTANT, 
                                borderValue=(255, 255, 255))
        
        return rotated
    
    def _final_polish(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Polissage final de l'image"""
        
        print("  ✨ Polissage final")
        
        # Dernière passe de nettoyage très légère
        polished = cv2.medianBlur(image, 3)
        
        # Assurer bonne taille finale
        height, width = polished.shape[:2]
        if width < self.min_size or height < self.min_size:
            factor = max(self.min_size / width, self.min_size / height)
            new_width = int(width * factor)
            new_height = int(height * factor)
            polished = cv2.resize(polished, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        metadata['steps_applied'].append('final_polish')
        metadata['final_shape'] = polished.shape
        
        return polished
    
    # Méthodes simplifiées pour traitement standard
    def _perspective_correction(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Correction perspective standard"""
        angle = self._detect_rotation_angle(image)
        if abs(angle) > 0.5:
            corrected = self._rotate_image(image, -angle)
            metadata['steps_applied'].append('perspective_correction')
            return corrected
        return image
    
    def _clahe_enhancement(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Amélioration CLAHE standard"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        metadata['steps_applied'].append('clahe_enhancement')
        return enhanced
    
    def _shadow_correction(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Correction ombres standard"""
        kernel = np.ones((30, 30), np.float32) / (30 * 30)
        background = cv2.filter2D(image, -1, kernel)
        corrected = cv2.addWeighted(image, 1.2, background, -0.2, 0)
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        metadata['steps_applied'].append('shadow_correction')
        return corrected
    
    def _intelligent_upscaling(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Agrandissement intelligent"""
        height, width = image.shape[:2]
        if width < self.min_size:
            factor = self.min_size / width
            new_size = (int(width * factor), int(height * factor))
            upscaled = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)
            metadata['steps_applied'].append('intelligent_upscaling')
            return upscaled
        return image
    
    def _advanced_denoising(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Débruitage avancé"""
        denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        denoised = cv2.medianBlur(denoised, 3)
        metadata['steps_applied'].append('advanced_denoising')
        return denoised
    
    def _adaptive_binarization(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Binarisation adaptative"""
        binary = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 6
        )
        metadata['steps_applied'].append('adaptive_binarization')
        return binary
    
    def _standard_enhancement(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Amélioration standard"""
        enhanced = cv2.equalizeHist(image)
        metadata['steps_applied'].append('standard_enhancement')
        return enhanced
    
    def _smart_upscaling(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Agrandissement intelligent simple"""
        return self._intelligent_upscaling(image, metadata)
    
    def _noise_reduction(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Réduction bruit simple"""
        denoised = cv2.medianBlur(image, 3)
        metadata['steps_applied'].append('noise_reduction')
        return denoised
    
    def _optimized_binarization(self, image: np.ndarray, metadata: Dict) -> np.ndarray:
        """Binarisation optimisée"""
        return self._adaptive_binarization(image, metadata)


def test_ultra_preprocessor():
    """Test de l'ultra-preprocesseur sur leve262"""
    
    print("🧪 TEST ULTRA-PREPROCESSOR SUR LEVE262")
    print("=" * 50)
    
    image_path = "Data_Hackathon_IA_2025/Testing_Data/leve262.png"
    
    if not Path(image_path).exists():
        print(f"❌ Image non trouvée: {image_path}")
        return
    
    # Charger image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Impossible de charger: {image_path}")
        return
    
    print(f"📄 Image chargée: {image.shape}")
    
    # Initialiser ultra-preprocessor
    ultra = UltraPreprocessor()
    
    # Traitement ultra
    enhanced, metadata = ultra.enhance_difficult_image(image)
    
    print(f"\n✅ TRAITEMENT TERMINÉ")
    print(f"📐 Forme finale: {enhanced.shape}")
    print(f"🔧 Étapes appliquées: {len(metadata['steps_applied'])}")
    
    for step in metadata['steps_applied']:
        print(f"  • {step}")
    
    # Sauvegarder résultat
    output_path = "leve262_ultra_preprocessed.png"
    cv2.imwrite(output_path, enhanced)
    print(f"💾 Image sauvée: {output_path}")
    
    return enhanced, metadata


if __name__ == "__main__":
    test_ultra_preprocessor()