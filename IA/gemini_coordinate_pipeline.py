#!/usr/bin/env python3
"""
PIPELINE FINAL GEMINI - SOLUTION ULTIME POUR EXTRACTION COORDONNÉES
Combine le meilleur des technologies: Preprocessing avancé + Gemini OCR
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse

# Import des modules optimisés
from gemini_simple_extractor import GeminiSimpleExtractor

class GeminiCoordinatePipeline:
    """Pipeline final optimisé avec Gemini OCR"""
    
    def __init__(self, api_key: str = None):
        """Initialise le pipeline Gemini"""
        
        self.extractor = GeminiSimpleExtractor(api_key)
        
        print("🎯 PIPELINE GEMINI INITIALISÉ")
        print("=" * 50)
        print("✅ Preprocessing ultra-avancé 2025")
        print("✅ Gemini OCR avec intelligence artificielle")  
        print("✅ Parsing JSON + patterns multiples")
        print("✅ Validation géographique UTM 31N")
        print("=" * 50)
    
    def extract_single(self, image_path: str, save_result: bool = True) -> Dict[str, Any]:
        """Extraction sur une seule image"""
        
        print(f"\n🎯 EXTRACTION GEMINI PIPELINE")
        print(f"📄 Image: {Path(image_path).name}")
        
        # Extraction avec Gemini
        result = self.extractor.extract_coordinates(image_path, use_preprocessing=True)
        
        # Ajouter métadonnées du pipeline
        result['pipeline_version'] = '1.0.0_gemini'
        result['features'] = [
            'gemini_ocr',
            'advanced_preprocessing',
            'utm_validation',
            'json_parsing',
            'multiple_patterns'
        ]
        
        # Sauvegarder si demandé
        if save_result:
            output_file = self._save_result(result)
            result['output_file'] = output_file
            print(f"💾 Résultat sauvé: {output_file}")
        
        # Afficher résumé
        self._print_summary(result)
        
        return result
    
    def extract_batch(self, image_paths: List[str], save_results: bool = True) -> Dict[str, Any]:
        """Extraction en lot avec statistiques complètes"""
        
        print(f"\n🚀 GEMINI PIPELINE - EXTRACTION LOT")
        print(f"📊 {len(image_paths)} images à traiter")
        
        results = []
        stats = {
            'total_images': len(image_paths),
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_coordinates': 0,
            'processing_times': [],
            'coordinate_counts': []
        }
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\n[{i}/{len(image_paths)}] {'-'*40}")
            
            if not Path(image_path).exists():
                print(f"❌ Image non trouvée: {image_path}")
                stats['failed_extractions'] += 1
                continue
            
            try:
                result = self.extract_single(image_path, save_result=False)
                results.append(result)
                
                if result['success']:
                    stats['successful_extractions'] += 1
                    stats['total_coordinates'] += result['coordinate_count']
                    stats['processing_times'].append(result['processing_time'])
                    stats['coordinate_counts'].append(result['coordinate_count'])
                else:
                    stats['failed_extractions'] += 1
                    
            except Exception as e:
                print(f"❌ Erreur traitement {Path(image_path).name}: {e}")
                stats['failed_extractions'] += 1
        
        # Calculer statistiques finales
        batch_result = self._compile_batch_stats(results, stats)
        
        # Sauvegarder résultats lot
        if save_results:
            output_file = self._save_batch_result(batch_result)
            print(f"\n💾 Résultats lot sauvés: {output_file}")
        
        # Afficher résumé final
        self._print_batch_summary(batch_result)
        
        return batch_result
    
    def _compile_batch_stats(self, results: List[Dict], stats: Dict) -> Dict[str, Any]:
        """Compile les statistiques du lot"""
        
        success_rate = stats['successful_extractions'] / stats['total_images'] if stats['total_images'] > 0 else 0
        avg_processing_time = sum(stats['processing_times']) / len(stats['processing_times']) if stats['processing_times'] else 0
        avg_coordinates = sum(stats['coordinate_counts']) / len(stats['coordinate_counts']) if stats['coordinate_counts'] else 0
        
        return {
            'pipeline_version': '1.0.0_gemini',
            'batch_timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_images': stats['total_images'],
                'successful_extractions': stats['successful_extractions'],
                'failed_extractions': stats['failed_extractions'],
                'success_rate': success_rate,
                'total_coordinates': stats['total_coordinates'],
                'average_coordinates_per_image': avg_coordinates,
                'average_processing_time': avg_processing_time,
                'total_processing_time': sum(stats['processing_times'])
            },
            'results': results,
            'method': 'gemini_pipeline_batch'
        }
    
    def _save_result(self, result: Dict[str, Any]) -> str:
        """Sauvegarde résultat individuel"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"gemini_extraction_{Path(result['image_path']).stem}_{timestamp}.json"
        
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def _save_batch_result(self, batch_result: Dict[str, Any]) -> str:
        """Sauvegarde résultats lot"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"gemini_batch_extraction_{timestamp}.json"
        
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(batch_result, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def _print_summary(self, result: Dict[str, Any]) -> None:
        """Affiche résumé d'extraction"""
        
        print(f"\n📊 RÉSUMÉ EXTRACTION:")
        print(f"=" * 40)
        
        if result['success']:
            print(f"🏆 SUCCÈS: {result['coordinate_count']} coordonnées extraites")
            print(f"⏱️ Temps: {result['processing_time']:.1f}s")
            print(f"🔧 Méthode: {result['method']}")
            
            # Top 5 coordonnées
            for i, coord in enumerate(result['coordinates'][:5], 1):
                print(f"  {i}. {coord['point_id']}: X={coord['x']:.2f}, Y={coord['y']:.2f}")
            
            if len(result['coordinates']) > 5:
                print(f"  ... et {len(result['coordinates'])-5} autres")
        else:
            print(f"❌ ÉCHEC: {result.get('error', 'Erreur inconnue')}")
        
        print(f"=" * 40)
    
    def _print_batch_summary(self, batch_result: Dict[str, Any]) -> None:
        """Affiche résumé lot"""
        
        stats = batch_result['statistics']
        
        print(f"\n🏆 RÉSUMÉ LOT GEMINI PIPELINE")
        print(f"=" * 50)
        print(f"📊 Images traitées: {stats['total_images']}")
        print(f"✅ Succès: {stats['successful_extractions']}")
        print(f"❌ Échecs: {stats['failed_extractions']}")
        print(f"📈 Taux de succès: {stats['success_rate']*100:.1f}%")
        print(f"🎯 Total coordonnées: {stats['total_coordinates']}")
        print(f"📊 Moyenne/image: {stats['average_coordinates_per_image']:.1f}")
        print(f"⏱️ Temps moyen: {stats['average_processing_time']:.1f}s")
        print(f"⏱️ Temps total: {stats['total_processing_time']:.1f}s")
        print(f"=" * 50)


def main():
    """Interface CLI du pipeline Gemini"""
    
    parser = argparse.ArgumentParser(description="Pipeline Gemini pour extraction coordonnées")
    parser.add_argument('input', help='Image ou dossier à traiter')
    parser.add_argument('--batch', action='store_true', help='Mode lot (dossier)')
    parser.add_argument('--no-save', action='store_true', help='Ne pas sauvegarder les résultats')
    parser.add_argument('--api-key', help='Clé API Google (optionnel si dans .env)')
    
    args = parser.parse_args()
    
    try:
        # Initialiser pipeline
        pipeline = GeminiCoordinatePipeline(args.api_key)
        
        if args.batch:
            # Mode lot
            input_dir = Path(args.input)
            if not input_dir.is_dir():
                print(f"❌ Dossier non trouvé: {args.input}")
                return 1
            
            # Trouver toutes les images
            image_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
            image_paths = [
                str(p) for p in input_dir.rglob('*') 
                if p.suffix.lower() in image_extensions
            ]
            
            if not image_paths:
                print(f"❌ Aucune image trouvée dans: {args.input}")
                return 1
            
            # Extraction lot
            result = pipeline.extract_batch(image_paths, save_results=not args.no_save)
            
        else:
            # Mode fichier unique
            if not Path(args.input).exists():
                print(f"❌ Fichier non trouvé: {args.input}")
                return 1
            
            result = pipeline.extract_single(args.input, save_result=not args.no_save)
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur pipeline: {e}")
        return 1


def demo_pipeline():
    """Démonstration du pipeline sur images test"""
    
    print("🚀 DÉMONSTRATION PIPELINE GEMINI")
    
    try:
        pipeline = GeminiCoordinatePipeline()
        
        # Images test (de facile à difficile)
        demo_images = [
            "Data_Hackathon_IA_2025/Training_Data/leve124.png",  # Référence (parfait)
            "Data_Hackathon_IA_2025/Training_Data/leve101.png",  # Bon
            "Data_Hackathon_IA_2025/Training_Data/leve13.png",   # Moyen
        ]
        
        # Filtrer images existantes
        existing_images = [img for img in demo_images if Path(img).exists()]
        
        if existing_images:
            batch_result = pipeline.extract_batch(existing_images)
            
            print(f"\n✅ DÉMONSTRATION TERMINÉE")
            print(f"🏆 Performance globale: {batch_result['statistics']['success_rate']*100:.1f}%")
        else:
            print("❌ Aucune image de démonstration trouvée")
    
    except Exception as e:
        print(f"❌ Erreur démonstration: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Mode démonstration si pas d'arguments
        demo_pipeline()
    else:
        # Mode CLI normal
        sys.exit(main())