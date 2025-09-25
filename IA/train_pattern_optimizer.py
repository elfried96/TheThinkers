#!/usr/bin/env python3
"""
Optimiseur de patterns basé sur le groundtruth - Approche ML
"""

import sys
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Any
import re
sys.path.append('.')

from main_extractor import CoordinateExtractionPipeline

class PatternOptimizer:
    """Optimiseur de patterns basé sur données d'entraînement"""
    
    def __init__(self):
        self.groundtruth_file = "Data_Hackathon_IA_2025/groundtruth_training.xlsx"
        self.training_dir = Path("Data_Hackathon_IA_2025/Training_Data")
        self.pipeline = None
        self.results = []
        
    def load_groundtruth(self) -> Dict[str, List[Dict]]:
        """Charge le groundtruth depuis Excel"""
        print("📂 Chargement du groundtruth...")
        
        df = pd.read_excel(self.groundtruth_file)
        groundtruth = {}
        
        for _, row in df.iterrows():
            filename = row['Nom_du_levé']
            coords_str = row['Coordonnées']
            
            try:
                coords = json.loads(coords_str)
                groundtruth[filename] = coords
                print(f"  ✓ {filename}: {len(coords)} coordonnées")
            except Exception as e:
                print(f"  ❌ {filename}: Erreur parsing - {e}")
        
        print(f"📊 Total: {len(groundtruth)} fichiers chargés\n")
        return groundtruth
    
    def initialize_pipeline(self):
        """Initialise le pipeline d'extraction"""
        print("🔧 Initialisation pipeline...")
        
        self.pipeline = CoordinateExtractionPipeline(
            ocr_engine='tesseract',
            language='fr', 
            confidence_threshold=0.5,  # Seuil bas pour plus de détections
            use_gpu=False
        )
        print("✓ Pipeline initialisé\n")
    
    def evaluate_single_image(self, filename: str, expected_coords: List[Dict]) -> Dict:
        """Évalue l'extraction sur une seule image"""
        
        image_path = self.training_dir / filename
        
        if not image_path.exists():
            return {
                'filename': filename,
                'status': 'file_not_found',
                'extracted_count': 0,
                'expected_count': len(expected_coords),
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0,
                'matches': []
            }
        
        print(f"🔍 Test: {filename}")
        
        # Extraction
        try:
            result = self.pipeline.process_file(str(image_path))
            extracted_coords = result['ocr_result']['coordinates_found']
            
            print(f"  📊 Extraites: {len(extracted_coords)} | Attendues: {len(expected_coords)}")
            
            # Calcul des métriques
            matches = self.match_coordinates(extracted_coords, expected_coords)
            
            precision = len(matches) / len(extracted_coords) if extracted_coords else 0
            recall = len(matches) / len(expected_coords) if expected_coords else 0
            f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"  🎯 Matches: {len(matches)} | Précision: {precision:.2f} | Rappel: {recall:.2f} | F1: {f1_score:.2f}")
            
            # Afficher les coordonnées extraites vs attendues
            if extracted_coords:
                print(f"  📍 Extraites:")
                for i, coord in enumerate(extracted_coords[:5]):  # Top 5
                    print(f"    {i+1}. ({coord['x']:8.2f}, {coord['y']:9.2f}) - Conf: {coord['confidence']:.3f}")
            
            if len(matches) > 0:
                print(f"  ✅ Matches trouvés:")
                for match in matches[:3]:  # Top 3
                    ext, exp = match
                    print(f"    ↳ ({ext['x']:8.2f}, {ext['y']:9.2f}) ≈ ({exp['x']:8.2f}, {exp['y']:9.2f})")
            
            print()
            
            return {
                'filename': filename,
                'status': 'success',
                'extracted_count': len(extracted_coords),
                'expected_count': len(expected_coords),
                'precision': precision,
                'recall': recall, 
                'f1_score': f1_score,
                'matches': matches,
                'extracted_coords': extracted_coords,
                'expected_coords': expected_coords,
                'ocr_text': result['ocr_result'].get('raw_text', '')[:200] + '...'
            }
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}\n")
            return {
                'filename': filename,
                'status': 'error',
                'error': str(e),
                'extracted_count': 0,
                'expected_count': len(expected_coords),
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0,
                'matches': []
            }
    
    def match_coordinates(self, extracted: List[Dict], expected: List[Dict], tolerance: float = 2.0) -> List[Tuple]:
        """Match coordonnées extraites vs attendues avec tolérance"""
        
        matches = []
        used_expected = set()
        
        for ext_coord in extracted:
            best_match = None
            best_distance = float('inf')
            
            for i, exp_coord in enumerate(expected):
                if i in used_expected:
                    continue
                
                # Distance euclidienne
                dx = ext_coord['x'] - exp_coord['x']
                dy = ext_coord['y'] - exp_coord['y'] 
                distance = (dx**2 + dy**2)**0.5
                
                if distance < tolerance and distance < best_distance:
                    best_match = (ext_coord, exp_coord)
                    best_distance = distance
                    best_idx = i
            
            if best_match:
                matches.append(best_match)
                used_expected.add(best_idx)
        
        return matches
    
    def run_training_evaluation(self, max_files: int = 10) -> Dict:
        """Lance l'évaluation sur le set d'entraînement"""
        
        print("🚀 ENTRAÎNEMENT/ÉVALUATION DES PATTERNS")
        print("="*60)
        
        # Charger groundtruth  
        groundtruth = self.load_groundtruth()
        
        # Initialiser pipeline
        self.initialize_pipeline()
        
        # Évaluer sur échantillon
        print(f"📋 Évaluation sur {min(max_files, len(groundtruth))} images...")
        print()
        
        results = []
        total_f1 = 0
        successful_tests = 0
        
        for i, (filename, expected_coords) in enumerate(groundtruth.items()):
            if i >= max_files:
                break
                
            result = self.evaluate_single_image(filename, expected_coords)
            results.append(result)
            
            if result['status'] == 'success':
                total_f1 += result['f1_score']
                successful_tests += 1
        
        # Calcul métriques globales
        avg_f1 = total_f1 / successful_tests if successful_tests > 0 else 0
        
        summary = {
            'total_files': len(results),
            'successful_tests': successful_tests,
            'failed_tests': len(results) - successful_tests,
            'average_f1_score': avg_f1,
            'results': results
        }
        
        self.results = results
        
        print("="*60)
        print("📊 RÉSULTATS GLOBAUX:")
        print(f"  Tests réussis: {successful_tests}/{len(results)}")
        print(f"  Score F1 moyen: {avg_f1:.3f}")
        print(f"  Taux de succès: {successful_tests/len(results)*100:.1f}%")
        
        return summary
    
    def analyze_failures(self):
        """Analyse les échecs pour optimiser les patterns"""
        
        print("\n🔍 ANALYSE DES ÉCHECS:")
        print("="*40)
        
        low_performance = [r for r in self.results if r.get('f1_score', 0) < 0.5]
        
        for result in low_performance[:5]:  # Top 5 échecs
            if result['status'] != 'success':
                continue
                
            print(f"\n❌ {result['filename']} (F1: {result['f1_score']:.3f})")
            print(f"  Extraites: {result['extracted_count']} | Attendues: {result['expected_count']}")
            print(f"  OCR extrait: '{result['ocr_text']}'")
            
            # Analyser les coordonnées manquées
            expected = result['expected_coords']
            matches = result['matches']
            matched_expected = [m[1] for m in matches]
            
            missed = [exp for exp in expected if exp not in matched_expected]
            if missed:
                print(f"  Manquées ({len(missed)}):")
                for coord in missed[:3]:
                    print(f"    - ({coord['x']:8.2f}, {coord['y']:9.2f})")
    
    def suggest_pattern_improvements(self):
        """Suggère des améliorations de patterns basées sur l'analyse"""
        
        print("\n💡 SUGGESTIONS D'AMÉLIORATION:")
        print("="*40)
        
        # Analyser les textes OCR pour patterns manqués
        all_ocr_texts = [r.get('ocr_text', '') for r in self.results if r['status'] == 'success']
        
        # Rechercher des patterns numériques non capturés
        all_numbers = []
        for text in all_ocr_texts:
            numbers = re.findall(r'\d{6,8}[\.,]?\d*', text)
            all_numbers.extend(numbers)
        
        print(f"🔢 Nombres détectés dans OCR: {len(set(all_numbers))}")
        print("Exemples:")
        for num in sorted(set(all_numbers))[:10]:
            print(f"  - {num}")
        
        print("\n📋 RECOMMANDATIONS:")
        print("1. Améliorer le préprocessing pour images à faible contraste")
        print("2. Ajouter des patterns pour coordonnées fragmentées")
        print("3. Optimiser la validation UTM (certaines coordonnées valides rejetées)")
        print("4. Tester d'autres configurations Tesseract (PSM modes)")

def main():
    """Fonction principale d'optimisation"""
    
    optimizer = PatternOptimizer()
    
    # Lancer l'évaluation
    summary = optimizer.run_training_evaluation(max_files=15)  # Test sur 15 images
    
    # Analyser les résultats
    optimizer.analyze_failures()
    optimizer.suggest_pattern_improvements()
    
    # Sauvegarder résultats
    with open('pattern_optimization_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📁 Résultats sauvegardés: pattern_optimization_results.json")
    
    return summary['average_f1_score'] >= 0.6  # Succès si F1 >= 0.6

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 OPTIMISATION RÉUSSIE!' if success else '⚠️ OPTIMISATION À POURSUIVRE'}")