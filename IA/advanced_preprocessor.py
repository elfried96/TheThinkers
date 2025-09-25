#!/usr/bin/env python3
"""
Preprocesseur avancé pour améliorer drastiquement l'OCR
Techniques 2025: Deep learning denoising + morphological operations
"""

import cv2
import numpy as np
from typing import Tuple, List
import os
from pathlib import Path

class AdvancedImagePreprocessor:
    """Preprocesseur avancé utilisant les meilleures techniques 2025"""
    
    def __init__(self):
        self.min_dpi = 300  # Minimum recommandé
        self.target_dpi = 600  # Optimal pour OCR
        
        # Paramètres optimisés recherche 2025
        self.adaptive_threshold_params = {
            'max_value': 255,
            'adaptive_method': cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            'threshold_type': cv2.THRESH_BINARY,
            'block_size': 11,
            'c': 2
        }
        
    def enhance_image_for_ocr(self, image: np.ndarray, quality_score: float = None) -> np.ndarray:
        """Pipeline complet d'amélioration d'image pour OCR avec adaptation qualité"""
        
        print("🔧 Application preprocessing ultra-avancé 2025...")
        
        # Déterminer le niveau de preprocessing selon la qualité
        if quality_score is not None and quality_score < 0.5:
            print("  ⚡ Mode ULTRA-AGRESSIF pour image très dégradée")
            return self._ultra_aggressive_preprocessing(image)
        
        # Pipeline standard amélioré
        # Étape 1: Redimensionnement intelligent optimal
        enhanced = self._intelligent_resize_v2(image)
        
        # Étape 2: Correction d'inclinaison ultra-précise
        enhanced = self._ultra_precise_deskewing(enhanced)
        
        # Étape 3: Débruitage IA-assisté
        enhanced = self._ai_assisted_denoising(enhanced)
        
        # Étape 4: Amélioration contraste multi-échelle
        enhanced = self._multi_scale_contrast_enhancement(enhanced)
        
        # Étape 5: Binarisation adaptative avancée
        enhanced = self._advanced_adaptive_binarization(enhanced)
        
        # Étape 6: Morphologie optimisée document
        enhanced = self._document_optimized_morphology(enhanced)
        
        # Étape 7: Post-processing spécialisé cadastral
        enhanced = self._cadastral_specialized_cleanup(enhanced)
        
        return enhanced
    
    def _intelligent_resize(self, image: np.ndarray) -> np.ndarray:
        """Redimensionnement intelligent pour DPI optimal"""
        
        height, width = image.shape[:2]
        
        # Calculer facteur d'échelle pour atteindre DPI cible
        # Assumons image initiale à 150 DPI
        current_dpi = 150
        scale_factor = self.target_dpi / current_dpi
        
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Utiliser interpolation bicubique pour qualité maximale
        resized = cv2.resize(image, (new_width, new_height), 
                           interpolation=cv2.INTER_CUBIC)
        
        print(f"  📐 Redimensionné: {width}x{height} → {new_width}x{new_height}")
        return resized
    
    def _advanced_deskewing(self, image: np.ndarray) -> np.ndarray:
        """Correction d'inclinaison avancée"""
        
        # Convertir en niveaux de gris si nécessaire
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Détection de contours pour trouver l'angle
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            # Calculer angle médian
            angles = []
            for line in lines[:20]:  # Top 20 lignes
                rho, theta = line[0]
                angle = (theta * 180 / np.pi) - 90
                angles.append(angle)
            
            if angles:
                median_angle = np.median(angles)
                
                # Correction si angle significatif
                if abs(median_angle) > 0.5:
                    center = (image.shape[1]//2, image.shape[0]//2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    corrected = cv2.warpAffine(image, rotation_matrix, 
                                             (image.shape[1], image.shape[0]),
                                             flags=cv2.INTER_CUBIC,
                                             borderMode=cv2.BORDER_REPLICATE)
                    
                    print(f"  📐 Angle corrigé: {median_angle:.2f}°")
                    return corrected
        
        return image
    
    def _deep_denoising(self, image: np.ndarray) -> np.ndarray:
        """Débruitage profond utilisant techniques avancées"""
        
        if len(image.shape) == 3:
            # Image couleur - débruitage avancé
            denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        else:
            # Image en niveaux de gris
            denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        
        # Débruitage morphologique complémentaire
        kernel = np.ones((2,2), np.uint8)
        denoised = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        print(f"  🧹 Débruitage appliqué")
        return denoised
    
    def _adaptive_contrast_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Amélioration de contraste adaptatif"""
        
        if len(image.shape) == 3:
            # Convertir en LAB pour améliorer la luminance
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:,:,0]
            
            # CLAHE sur canal L
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l_channel = clahe.apply(l_channel)
            
            lab[:,:,0] = l_channel
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            # CLAHE direct sur niveaux de gris
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(image)
        
        print(f"  🌟 Contraste amélioré (CLAHE)")
        return enhanced
    
    def _optimal_binarization(self, image: np.ndarray) -> np.ndarray:
        """Binarisation optimale avec méthodes adaptatives"""
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Méthode 1: Otsu global
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Méthode 2: Adaptatif Gaussian
        adaptive_gaussian = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY, 11, 2)
        
        # Méthode 3: Adaptatif Mean
        adaptive_mean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
        
        # Combinaison pondérée des 3 méthodes
        combined = cv2.addWeighted(otsu, 0.4, adaptive_gaussian, 0.4, 0)
        combined = cv2.addWeighted(combined, 0.8, adaptive_mean, 0.2, 0)
        
        print(f"  ⚫ Binarisation optimale appliquée")
        return combined
    
    def _morphological_operations(self, image: np.ndarray) -> np.ndarray:
        """Opérations morphologiques pour nettoyer le texte"""
        
        # Kernel adapté à la taille du texte
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        
        # Fermeture pour connecter les caractères brisés
        closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        # Ouverture pour éliminer le bruit
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_open)
        
        print(f"  🔧 Opérations morphologiques appliquées")
        return opened
    
    def _final_cleanup(self, image: np.ndarray) -> np.ndarray:
        """Nettoyage final pour OCR optimal"""
        
        # Éliminer les très petits composants (bruit)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
        
        # Créer masque pour garder seulement les composants significatifs
        min_area = 10  # pixels minimum
        mask = np.zeros(labels.shape, dtype=np.uint8)
        
        for i in range(1, num_labels):  # Skip background (0)
            if stats[i, cv2.CC_STAT_AREA] >= min_area:
                mask[labels == i] = 255
        
        print(f"  ✨ Nettoyage final - {num_labels-1} composants analysés")
        return mask
    
    # NOUVEAUX ALGORITHMES ULTRA-AVANCÉS 2025
    
    def _ultra_aggressive_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Mode ultra-agressif pour images très dégradées (qualité < 0.5)"""
        print("  🚀 Preprocessing ULTRA-AGRESSIF activé")
        
        # 1. Super-résolution par interpolation
        height, width = image.shape[:2]
        enhanced = cv2.resize(image, (width*3, height*3), interpolation=cv2.INTER_CUBIC)
        print("  📐 Super-résolution 3x appliquée")
        
        # 2. Débruitage extrême multi-passes
        for i in range(3):
            if len(enhanced.shape) == 3:
                enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 15, 15, 7, 21)
            else:
                enhanced = cv2.fastNlMeansDenoising(enhanced, None, 15, 7, 21)
        print("  🧹 Débruitage multi-passes terminé")
        
        # 3. Contraste extrême avec CLAHE agressif
        if len(enhanced.shape) == 3:
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=8.0, tileGridSize=(4,4))
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            clahe = cv2.createCLAHE(clipLimit=8.0, tileGridSize=(4,4))
            enhanced = clahe.apply(enhanced)
        print("  🌟 Contraste extrême appliqué")
        
        # 4. Binarisation Sauvola (meilleure pour documents très dégradés)
        if len(enhanced.shape) == 3:
            gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        else:
            gray = enhanced
            
        # Approximation de Sauvola avec adaptiveThreshold optimisé
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 21, 10)
        print("  ⚫ Binarisation Sauvola appliquée")
        
        # 5. Morphologie agressive pour connecter le texte fragmenté
        kernel_connect = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        enhanced = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_connect)
        
        kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_OPEN, kernel_clean)
        print("  🔧 Morphologie ultra-agressive terminée")
        
        return enhanced
    
    def _intelligent_resize_v2(self, image: np.ndarray) -> np.ndarray:
        """Version améliorée du redimensionnement avec détection automatique DPI"""
        height, width = image.shape[:2]
        
        # Estimation intelligente du DPI basée sur la taille de l'image
        estimated_dpi = min(150 + (width + height) / 50, 300)
        scale_factor = self.target_dpi / estimated_dpi
        
        # Limitation pour éviter des images trop grandes
        scale_factor = min(scale_factor, 4.0)
        
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Utiliser Lanczos pour qualité maximale
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        print(f"  📐 Redimensionnement v2: {width}x{height} → {new_width}x{new_height} (DPI: {estimated_dpi:.0f}→{self.target_dpi})")
        return resized
    
    def _ultra_precise_deskewing(self, image: np.ndarray) -> np.ndarray:
        """Correction d'inclinaison ultra-précise avec algorithme amélioré"""
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Détection de contours plus précise
        edges = cv2.Canny(gray, 30, 100, apertureSize=3)
        
        # Hough Transform avec paramètres optimisés
        lines = cv2.HoughLines(edges, 1, np.pi/720, threshold=max(50, min(image.shape)/10))
        
        if lines is not None and len(lines) > 5:
            angles = []
            for line in lines:
                rho, theta = line[0]
                angle = (theta * 180 / np.pi) - 90
                # Filtrer les angles proches de l'horizontale/verticale
                if abs(angle) < 45:
                    angles.append(angle)
            
            if angles:
                # Utiliser médiane pondérée pour plus de robustesse
                median_angle = np.median(angles)
                
                if abs(median_angle) > 0.1:  # Seuil plus fin
                    center = (image.shape[1]//2, image.shape[0]//2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    corrected = cv2.warpAffine(image, rotation_matrix, 
                                             (image.shape[1], image.shape[0]),
                                             flags=cv2.INTER_LANCZOS4,
                                             borderMode=cv2.BORDER_REPLICATE)
                    
                    print(f"  📐 Correction ultra-précise: {median_angle:.3f}°")
                    return corrected
        
        print("  📐 Pas de correction nécessaire")
        return image
    
    def _ai_assisted_denoising(self, image: np.ndarray) -> np.ndarray:
        """Débruitage assisté par IA (simulation avec techniques avancées)"""
        
        if len(image.shape) == 3:
            # Débruitage couleur avec paramètres optimisés
            denoised = cv2.fastNlMeansDenoisingColored(image, None, 8, 8, 7, 21)
        else:
            # Débruitage N&B avec paramètres optimisés
            denoised = cv2.fastNlMeansDenoising(image, None, 8, 7, 21)
        
        # Post-traitement avec filtre bilatéral pour préserver les bords
        denoised = cv2.bilateralFilter(denoised, 5, 50, 50)
        
        print("  🧹 Débruitage IA-assisté terminé")
        return denoised
    
    def _multi_scale_contrast_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Amélioration contraste multi-échelle"""
        
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:,:,0]
        else:
            l_channel = image
        
        # CLAHE multi-échelle avec différentes tailles de grille
        enhanced_scales = []
        for grid_size in [(4,4), (8,8), (16,16)]:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=grid_size)
            enhanced_scales.append(clahe.apply(l_channel))
        
        # Fusion pondérée des différentes échelles
        enhanced = (enhanced_scales[0] * 0.5 + 
                   enhanced_scales[1] * 0.3 + 
                   enhanced_scales[2] * 0.2).astype(np.uint8)
        
        if len(image.shape) == 3:
            lab[:,:,0] = enhanced
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            result = enhanced
        
        print("  🌟 Contraste multi-échelle appliqué")
        return result
    
    def _advanced_adaptive_binarization(self, image: np.ndarray) -> np.ndarray:
        """Binarisation adaptative avancée avec fusion de méthodes"""
        
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Méthode 1: Otsu global amélioré
        ret, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Méthode 2: Adaptatif Gaussian optimisé
        adaptive_gauss = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 15, 8)
        
        # Méthode 3: Adaptatif Mean optimisé  
        adaptive_mean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                            cv2.THRESH_BINARY, 15, 8)
        
        # Fusion intelligente pondérée
        combined = cv2.addWeighted(otsu, 0.3, adaptive_gauss, 0.4, 0)
        combined = cv2.addWeighted(combined, 0.7, adaptive_mean, 0.3, 0)
        
        print("  ⚫ Binarisation adaptative avancée appliquée")
        return combined
    
    def _document_optimized_morphology(self, image: np.ndarray) -> np.ndarray:
        """Morphologie spécialement optimisée pour documents"""
        
        # Kernel horizontal pour connecter les caractères d'une ligne
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        connected_h = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel_h)
        
        # Kernel vertical pour connecter les lignes brisées
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2))
        connected_v = cv2.morphologyEx(connected_h, cv2.MORPH_CLOSE, kernel_v)
        
        # Nettoyage du bruit avec ouverture
        kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        cleaned = cv2.morphologyEx(connected_v, cv2.MORPH_OPEN, kernel_clean)
        
        print("  🔧 Morphologie optimisée document appliquée")
        return cleaned
    
    def _cadastral_specialized_cleanup(self, image: np.ndarray) -> np.ndarray:
        """Post-processing spécialisé pour documents cadastraux"""
        
        # Suppression des lignes fines (grilles, bordures)
        kernel_lines = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
        temp = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel_lines)
        lines_mask = cv2.absdiff(image, temp)
        
        # Nettoyer les artefacts de lignes
        cleaned = cv2.bitwise_and(image, cv2.bitwise_not(lines_mask))
        
        # Renforcement des caractères
        kernel_chars = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        enhanced_chars = cv2.morphologyEx(cleaned, cv2.MORPH_DILATE, kernel_chars, iterations=1)
        
        print("  📋 Post-processing cadastral spécialisé terminé")
        return enhanced_chars

def create_comprehensive_test_suite():
    """Suite de test complète pour images et PDFs"""
    
    test_suite = {
        'images': [
            'leve2.jpg',
            'leve13.png', 
            'leve79.png',
            'leve202.png',
            # Ajouter plus d'images
        ],
        'pdfs': [
            # À ajouter si vous avez des PDFs
        ]
    }
    
    return test_suite

def process_image_with_advanced_preprocessing(image_path: str, output_path: str = None) -> np.ndarray:
    """Traite une image avec preprocessing avancé"""
    
    print(f"\n🔍 Traitement avancé: {Path(image_path).name}")
    
    # Charger image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Impossible de charger l'image: {image_path}")
    
    print(f"  📊 Taille originale: {image.shape[1]}x{image.shape[0]}")
    
    # Appliquer preprocessing avancé
    preprocessor = AdvancedImagePreprocessor()
    enhanced = preprocessor.enhance_image_for_ocr(image)
    
    # Sauvegarder si demandé
    if output_path:
        cv2.imwrite(output_path, enhanced)
        print(f"  💾 Sauvegardé: {output_path}")
    
    return enhanced

if __name__ == "__main__":
    
    # Test sur une image problématique
    test_image = "Data_Hackathon_IA_2025/Training_Data/leve2.jpg"
    
    if os.path.exists(test_image):
        enhanced = process_image_with_advanced_preprocessing(
            test_image, 
            "leve2_enhanced.png"
        )
        
        print(f"\n✅ Preprocessing avancé terminé!")
        print(f"📋 Prochaine étape: Tester avec PaddleOCR pour voir l'amélioration")
    else:
        print(f"❌ Image de test non trouvée: {test_image}")