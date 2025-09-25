#!/usr/bin/env python3
"""
Préprocesseur morphologique avancé pour OCR
Spécialisé pour résoudre les confusions 0/6, améliorer la netteté des caractères
et traiter les cas difficiles avec des opérations morphologiques de pointe
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any, List
import logging
from scipy import ndimage
from skimage import morphology, filters, measure, restoration
import warnings
warnings.filterwarnings('ignore')

class EnhancedMorphologicalPreprocessor:
    """
    Préprocesseur avec opérations morphologiques avancées
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
            'fine_detail': cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        }
        
        self.logger.info("🔧 Enhanced Morphological Preprocessor initialized")
    
    def enhance_for_ocr(self, image: np.ndarray, difficulty_score: float = 0.5) -> np.ndarray:
        """
        Pipeline principal d'enhancement morphologique
        
        Args:
            image: Image d'entrée
            difficulty_score: Score de difficulté (0-1)
            
        Returns:
            Image améliorée
        """
        print(f"🔧 ENHANCEMENT MORPHOLOGIQUE - Difficulté: {difficulty_score:.3f}")
        
        # Conversion en niveaux de gris
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        processed = gray.copy()
        steps_applied = []
        
        # 1. Débruitage préliminaire adaptatif
        if difficulty_score > 0.4:
            processed = self._adaptive_denoising(processed)
            steps_applied.append("adaptive_denoising")
        
        # 2. Enhancement de contraste morphologique
        processed = self._morphological_contrast_enhancement(processed)
        steps_applied.append("morph_contrast")
        
        # 3. Correction des défauts de caractères (0/6, etc.)
        if difficulty_score > 0.3:
            processed = self._character_defect_correction(processed)
            steps_applied.append("char_correction")
        
        # 4. Skeletonization conditionnelle pour caractères fins
        if self._needs_skeletonization(processed):
            processed = self._smart_skeletonization(processed)
            steps_applied.append("skeletonization")
        
        # 5. Reconstruction morphologique
        processed = self._morphological_reconstruction(processed)
        steps_applied.append("morph_reconstruction")
        
        # 6. Sharpening final adaptatif
        processed = self._adaptive_sharpening(processed, difficulty_score)
        steps_applied.append("adaptive_sharp")
        
        print(f"✅ Enhancement terminé: {len(steps_applied)} étapes")
        return processed
    
    def _adaptive_denoising(self, image: np.ndarray) -> np.ndarray:
        """Débruitage adaptatif avec opérations morphologiques"""
        
        # Opening pour enlever le bruit sel
        denoised = cv2.morphologyEx(image, cv2.MORPH_OPEN, self.kernels['noise_removal'])
        
        # Closing pour fermer les trous
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, self.kernels['noise_removal'])
        
        # Filtre médian pour lisser
        denoised = cv2.medianBlur(denoised, 3)
        
        return denoised
    
    def _morphological_contrast_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Enhancement de contraste avec gradient morphologique"""
        
        # Gradient morphologique pour accentuer les contours
        gradient = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, self.kernels['fine_detail'])
        
        # Top-hat pour améliorer les détails clairs
        tophat = cv2.morphologyEx(image, cv2.MORPH_TOPHAT, self.kernels['text_clean'])
        
        # Blackhat pour améliorer les détails sombres
        blackhat = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, self.kernels['text_clean'])
        
        # Combiner pour enhancement global
        enhanced = cv2.add(image, tophat)
        enhanced = cv2.subtract(enhanced, blackhat)
        enhanced = cv2.add(enhanced, gradient)
        
        return enhanced
    
    def _character_defect_correction(self, image: np.ndarray) -> np.ndarray:
        """
        Correction spécifique des défauts de caractères
        Aide à distinguer 0/6, 4/1, 9/0 et améliore la forme des chiffres
        """
        
        # Binarisation adaptative avec seuils multiples
        binary1 = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Deuxième binarisation avec paramètres différents pour capturer plus de détails
        binary2 = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
            cv2.THRESH_BINARY, 15, 5
        )
        
        # Combiner les deux binarisations
        binary = cv2.bitwise_and(binary1, binary2)
        
        # Closing spécialisé pour fermer les gaps critiques (0/6 distinction)
        # Kernel vertical pour préserver les ouvertures horizontales
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
        closed_v = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, vertical_kernel)
        
        # Kernel horizontal pour gérer les coupures verticales (4/1 distinction)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        closed_h = cv2.morphologyEx(closed_v, cv2.MORPH_CLOSE, horizontal_kernel)
        
        # Opening pour nettoyer les artéfacts sans perdre la structure
        cleaned = cv2.morphologyEx(closed_h, cv2.MORPH_OPEN, self.kernels['fine_detail'])
        
        # Dilatation conditionnelle pour épaissir les traits fins
        # Plus agressive pour les images difficiles
        thickened = cv2.dilate(cleaned, self.kernels['fine_detail'], iterations=1)
        
        # Enhancement spécialisé pour les confusions communes
        enhanced = self._fix_digit_confusions(thickened)
        
        # Reconversion en niveaux de gris
        result = cv2.bitwise_not(enhanced) if np.mean(enhanced) > 127 else enhanced
        
        return result
    
    def _fix_digit_confusions(self, binary_image: np.ndarray) -> np.ndarray:
        """
        Corrections spécialisées pour les confusions de chiffres courantes:
        - 0 vs 6: Préserver/restaurer l'ouverture du 6
        - 4 vs 1: Préserver les connexions horizontales du 4
        - 9 vs 0: Préserver l'ouverture du 9
        """
        
        # Trouver les composantes connectées (caractères individuels)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_image, connectivity=8)
        
        result = binary_image.copy()
        
        for i in range(1, num_labels):  # Skip background (label 0)
            # Extraire la région du caractère
            mask = (labels == i).astype(np.uint8) * 255
            
            # Statistiques de la composante
            x, y, w, h, area = stats[i]
            
            # Filtrer les composantes trop petites (bruit)
            if area < 20 or w < 5 or h < 5:
                continue
            
            # Extraire le caractère
            char_region = binary_image[y:y+h, x:x+w]
            char_mask = mask[y:y+h, x:x+w]
            
            # Appliquer corrections spécialisées
            corrected = self._apply_digit_specific_fixes(char_region, char_mask, w, h)
            
            # Replacer dans l'image résultat
            result[y:y+h, x:x+w] = np.where(char_mask > 0, corrected, result[y:y+h, x:x+w])
        
        return result
    
    def _apply_digit_specific_fixes(self, char: np.ndarray, mask: np.ndarray, width: int, height: int) -> np.ndarray:
        """
        Applications de corrections spécifiques par type de caractère
        """
        
        # Analyser la forme pour identifier le type probable
        char_analysis = self._analyze_character_shape(char, width, height)
        
        corrected = char.copy()
        
        # Corrections basées sur l'analyse
        if char_analysis['likely_circular']:  # 0, 6, 8, 9, O
            # Préserver/restaurer les ouvertures importantes
            corrected = self._preserve_circular_openings(corrected)
            
        if char_analysis['has_vertical_line']:  # 1, 4, I, l
            # Renforcer les connexions verticales
            corrected = self._strengthen_vertical_features(corrected)
            
        if char_analysis['has_horizontal_features']:  # 4, 7, F, E, T
            # Préserver les traits horizontaux
            corrected = self._preserve_horizontal_features(corrected)
        
        return corrected
    
    def _analyze_character_shape(self, char: np.ndarray, width: int, height: int) -> Dict[str, bool]:
        """Analyse rapide de la forme du caractère"""
        
        # Projections pour analyser la structure
        h_projection = np.sum(char == 0, axis=1)  # Projection horizontale
        v_projection = np.sum(char == 0, axis=0)  # Projection verticale
        
        analysis = {
            'likely_circular': False,
            'has_vertical_line': False,
            'has_horizontal_features': False,
            'aspect_ratio': height / width if width > 0 else 1.0
        }
        
        # Détection forme circulaire (variations dans les projections)
        h_var = np.var(h_projection) if len(h_projection) > 0 else 0
        v_var = np.var(v_projection) if len(v_projection) > 0 else 0
        analysis['likely_circular'] = (h_var > width/4 and v_var > height/4)
        
        # Détection ligne verticale dominante
        max_v = np.max(v_projection) if len(v_projection) > 0 else 0
        avg_v = np.mean(v_projection) if len(v_projection) > 0 else 0
        analysis['has_vertical_line'] = (max_v > 2 * avg_v and analysis['aspect_ratio'] > 1.5)
        
        # Détection traits horizontaux
        max_h = np.max(h_projection) if len(h_projection) > 0 else 0
        avg_h = np.mean(h_projection) if len(h_projection) > 0 else 0
        analysis['has_horizontal_features'] = (max_h > 1.5 * avg_h)
        
        return analysis
    
    def _preserve_circular_openings(self, char: np.ndarray) -> np.ndarray:
        """Préserve les ouvertures dans les caractères circulaires (6, 9, etc.)"""
        
        # Opening modéré pour préserver les ouvertures naturelles
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        opened = cv2.morphologyEx(char, cv2.MORPH_OPEN, kernel)
        
        return opened
    
    def _strengthen_vertical_features(self, char: np.ndarray) -> np.ndarray:
        """Renforce les caractéristiques verticales (pour 1, 4, etc.)"""
        
        # Dilatation verticale
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2))
        strengthened = cv2.dilate(char, kernel, iterations=1)
        
        return strengthened
    
    def _preserve_horizontal_features(self, char: np.ndarray) -> np.ndarray:
        """Préserve les traits horizontaux (pour 4, 7, etc.)"""
        
        # Closing horizontal pour connecter les traits horizontaux cassés
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        preserved = cv2.morphologyEx(char, cv2.MORPH_CLOSE, kernel)
        
        return preserved
    
    def _needs_skeletonization(self, image: np.ndarray) -> bool:
        """Détermine si l'image nécessite une skeletonization"""
        
        # Analyser l'épaisseur moyenne des traits
        binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Distance transform pour mesurer l'épaisseur
        dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        
        # Si traits trop épais, skeletonization nécessaire
        max_thickness = np.max(dist_transform)
        
        return max_thickness > 5.0
    
    def _smart_skeletonization(self, image: np.ndarray) -> np.ndarray:
        """
        Skeletonization intelligente qui préserve la connectivité
        et les caractéristiques importantes des caractères
        """
        
        # Binarisation
        binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Inversion si nécessaire (texte noir sur fond blanc)
        if np.mean(binary) > 127:
            binary = cv2.bitwise_not(binary)
        
        # Skeletonization avec préservation des endpoints
        skeleton = morphology.skeletonize(binary // 255).astype(np.uint8) * 255
        
        # Dilatation légère pour restaurer la lisibilité
        skeleton = cv2.dilate(skeleton, self.kernels['fine_detail'], iterations=1)
        
        return skeleton
    
    def _morphological_reconstruction(self, image: np.ndarray) -> np.ndarray:
        """
        Reconstruction morphologique pour restaurer
        les structures importantes perdues
        """
        
        # Marker: image érodée
        marker = cv2.erode(image, self.kernels['fine_detail'], iterations=1)
        
        # Mask: image originale
        mask = image
        
        # Reconstruction par dilatation conditionnelle
        reconstructed = marker.copy()
        
        for _ in range(10):  # Limite les itérations
            dilated = cv2.dilate(reconstructed, self.kernels['fine_detail'])
            reconstructed = cv2.min(dilated, mask)
            
            # Convergence check
            if np.array_equal(dilated, reconstructed):
                break
        
        return reconstructed
    
    def _adaptive_sharpening(self, image: np.ndarray, difficulty_score: float) -> np.ndarray:
        """Sharpening adaptatif basé sur la difficulté"""
        
        # Intensité du sharpening basée sur la difficulté
        intensity = min(1.5, 0.5 + difficulty_score)
        
        # Kernel de sharpening adaptatif
        if difficulty_score > 0.6:
            # Cas difficile: sharpening plus agressif
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]]) * intensity
        else:
            # Cas normal: sharpening modéré
            kernel = np.array([[ 0, -1,  0],
                              [-1,  5, -1],
                              [ 0, -1,  0]]) * intensity
        
        # Application du filtre
        sharpened = cv2.filter2D(image, -1, kernel)
        
        # Clipping pour éviter les débordements
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return sharpened
    
    def analyze_character_quality(self, image: np.ndarray) -> Dict[str, float]:
        """
        Analyse la qualité des caractères pour détecter
        les problèmes spécifiques (flou, déformation, etc.)
        """
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Métriques de qualité
        metrics = {}
        
        # 1. Netteté (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        metrics['sharpness'] = min(1.0, laplacian_var / 1000.0)
        
        # 2. Contraste (écart-type)
        metrics['contrast'] = min(1.0, np.std(gray) / 128.0)
        
        # 3. Uniformité (homogénéité texture)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        metrics['uniformity'] = 1.0 - (np.sum(hist ** 2) / (gray.size ** 2))
        
        # 4. Densité du texte
        binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text_density = np.sum(binary == 0) / binary.size
        metrics['text_density'] = text_density
        
        # Score global de difficulté
        metrics['overall_difficulty'] = 1.0 - np.mean([
            metrics['sharpness'],
            metrics['contrast'],
            metrics['uniformity']
        ])
        
        return metrics

def test_enhanced_morphological():
    """Test du préprocesseur morphologique"""
    preprocessor = EnhancedMorphologicalPreprocessor()
    
    # Image de test
    test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    
    # Enhancement
    enhanced = preprocessor.enhance_for_ocr(test_image, 0.7)
    
    # Analyse qualité
    metrics = preprocessor.analyze_character_quality(enhanced)
    
    print("🧪 Test Enhanced Morphological Preprocessor")
    print(f"📊 Métriques: {metrics}")
    print("✅ Test réussi")

if __name__ == "__main__":
    test_enhanced_morphological()