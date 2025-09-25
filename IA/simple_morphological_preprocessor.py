#!/usr/bin/env python3
"""
Préprocesseur morphologique simplifié pour OCR
Sans dépendances externes (scipy, skimage)
Spécialisé pour résoudre les confusions 0/6, 4/1, 9/0
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any, List
import logging

class SimpleMorphologicalPreprocessor:
    """
    Préprocesseur avec opérations morphologiques simples
    pour améliorer l'OCR sur documents cadastraux
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Kernels morphologiques spécialisés
        self.kernels = {
            'digit_enhance': cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
            'text_clean': cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1)),
            'noise_removal': cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)),
            'skeleton': cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)),
            'fine_detail': cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1)),
            'vertical': cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3)),
            'horizontal': cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        }
        
        self.logger.info("🔧 Simple Morphological Preprocessor initialized")
    
    def enhance_for_ocr(self, image: np.ndarray, difficulty_score: float = 0.5) -> np.ndarray:
        """
        Pipeline principal d'enhancement morphologique
        """
        print(f"🔧 ENHANCEMENT MORPHOLOGIQUE SIMPLE - Difficulté: {difficulty_score:.3f}")
        
        # Conversion en niveaux de gris
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        processed = gray.copy()
        steps_applied = []
        
        # 1. Débruitage préliminaire
        if difficulty_score > 0.4:
            processed = self._simple_denoising(processed)
            steps_applied.append("denoising")
        
        # 2. Enhancement de contraste
        processed = self._enhance_contrast(processed)
        steps_applied.append("contrast")
        
        # 3. Correction des défauts de caractères
        if difficulty_score > 0.3:
            processed = self._fix_character_defects(processed)
            steps_applied.append("char_fix")
        
        # 4. Sharpening final
        processed = self._sharpen_image(processed, difficulty_score)
        steps_applied.append("sharpen")
        
        print(f"✅ Enhancement terminé: {len(steps_applied)} étapes")
        return processed
    
    def _simple_denoising(self, image: np.ndarray) -> np.ndarray:
        """Débruitage simple avec opérations morphologiques"""
        
        # Opening pour enlever le bruit
        denoised = cv2.morphologyEx(image, cv2.MORPH_OPEN, self.kernels['noise_removal'])
        
        # Closing pour fermer les trous
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, self.kernels['noise_removal'])
        
        # Filtre médian
        denoised = cv2.medianBlur(denoised, 3)
        
        return denoised
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhancement de contraste"""
        
        # CLAHE adaptatif
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # Gradient morphologique
        gradient = cv2.morphologyEx(enhanced, cv2.MORPH_GRADIENT, self.kernels['fine_detail'])
        
        # Combiner
        result = cv2.add(enhanced, gradient // 4)  # Gradient atténué
        
        return result
    
    def _fix_character_defects(self, image: np.ndarray) -> np.ndarray:
        """
        Correction des défauts de caractères pour éviter confusions 0/6, 4/1, 9/0
        """
        
        # Binarisation adaptative double
        binary1 = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        binary2 = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
            cv2.THRESH_BINARY, 15, 5
        )
        
        # Combiner les binarisations
        binary = cv2.bitwise_and(binary1, binary2)
        
        # Corrections spécialisées par direction
        
        # 1. Fermer les gaps verticaux (aide pour 0 vs 6)
        closed_v = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, self.kernels['vertical'])
        
        # 2. Fermer les gaps horizontaux (aide pour 4 vs 1)
        closed_h = cv2.morphologyEx(closed_v, cv2.MORPH_CLOSE, self.kernels['horizontal'])
        
        # 3. Nettoyer les artéfacts
        cleaned = cv2.morphologyEx(closed_h, cv2.MORPH_OPEN, self.kernels['fine_detail'])
        
        # 4. Épaissir légèrement les traits
        thickened = cv2.dilate(cleaned, self.kernels['fine_detail'], iterations=1)
        
        # 5. Corrections spécifiques aux chiffres
        corrected = self._digit_specific_corrections(thickened)
        
        # Reconversion en niveaux de gris
        result = cv2.bitwise_not(corrected) if np.mean(corrected) > 127 else corrected
        
        return result
    
    def _digit_specific_corrections(self, binary_image: np.ndarray) -> np.ndarray:
        """
        Corrections spécialisées pour les confusions de chiffres
        """
        
        # Analyser les composantes connectées
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        result = binary_image.copy()
        
        for contour in contours:
            # Filtrer les contours trop petits
            area = cv2.contourArea(contour)
            if area < 50:
                continue
            
            # Boîte englobante
            x, y, w, h = cv2.boundingRect(contour)
            
            if w < 5 or h < 5:
                continue
            
            # Extraire la région
            roi = binary_image[y:y+h, x:x+w]
            
            # Appliquer corrections basées sur la forme
            corrected_roi = self._analyze_and_correct_digit(roi, w, h)
            
            # Replacer dans l'image
            result[y:y+h, x:x+w] = corrected_roi
        
        return result
    
    def _analyze_and_correct_digit(self, roi: np.ndarray, width: int, height: int) -> np.ndarray:
        """
        Analyse et corrige un chiffre individual
        """
        
        aspect_ratio = height / width if width > 0 else 1.0
        
        # Projections pour analyser la structure
        h_projection = np.sum(roi == 0, axis=1)  # Noir = caractère
        v_projection = np.sum(roi == 0, axis=0)
        
        corrected = roi.copy()
        
        # Cas 1: Caractère vertical étroit (possiblement 1 ou I)
        if aspect_ratio > 2.0 and width < height // 3:
            # Renforcer la continuité verticale
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2))
            corrected = cv2.morphologyEx(corrected, cv2.MORPH_CLOSE, kernel)
        
        # Cas 2: Caractère avec variation horizontale (possiblement 4)
        elif len(h_projection) > 0 and np.max(h_projection) > 1.8 * np.mean(h_projection):
            # Renforcer les connexions horizontales
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
            corrected = cv2.morphologyEx(corrected, cv2.MORPH_CLOSE, kernel)
        
        # Cas 3: Caractère circulaire (possiblement 0, 6, 8, 9)
        elif aspect_ratio < 1.5 and len(v_projection) > 0:
            v_var = np.var(v_projection) if len(v_projection) > 1 else 0
            
            if v_var > width / 4:  # Variation suggère forme circulaire
                # Préserver les ouvertures naturelles avec opening modéré
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
                corrected = cv2.morphologyEx(corrected, cv2.MORPH_OPEN, kernel)
        
        return corrected
    
    def _sharpen_image(self, image: np.ndarray, difficulty_score: float) -> np.ndarray:
        """Sharpening adaptatif"""
        
        intensity = min(1.5, 0.5 + difficulty_score)
        
        if difficulty_score > 0.6:
            # Sharpening agressif
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]]) * intensity / 8
        else:
            # Sharpening modéré
            kernel = np.array([[ 0, -1,  0],
                              [-1,  5, -1],
                              [ 0, -1,  0]]) * intensity / 4
        
        sharpened = cv2.filter2D(image, -1, kernel)
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return sharpened
    
    def analyze_character_quality(self, image: np.ndarray) -> Dict[str, float]:
        """
        Analyse la qualité des caractères
        """
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        metrics = {}
        
        # 1. Netteté (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        metrics['sharpness'] = min(1.0, laplacian_var / 1000.0)
        
        # 2. Contraste
        metrics['contrast'] = min(1.0, np.std(gray) / 128.0)
        
        # 3. Uniformité
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        metrics['uniformity'] = 1.0 - (np.sum(hist ** 2) / (gray.size ** 2))
        
        # 4. Densité du texte
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text_density = np.sum(binary == 0) / binary.size
        metrics['text_density'] = text_density
        
        # Score global
        metrics['overall_difficulty'] = 1.0 - np.mean([
            metrics['sharpness'],
            metrics['contrast'],
            metrics['uniformity']
        ])
        
        return metrics

def test_simple_morphological():
    """Test du préprocesseur simple"""
    preprocessor = SimpleMorphologicalPreprocessor()
    
    # Image de test
    test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    
    # Enhancement
    enhanced = preprocessor.enhance_for_ocr(test_image, 0.7)
    
    # Analyse qualité
    metrics = preprocessor.analyze_character_quality(enhanced)
    
    print("🧪 Test Simple Morphological Preprocessor")
    print(f"📊 Métriques: {metrics}")
    print("✅ Test réussi")

if __name__ == "__main__":
    test_simple_morphological()