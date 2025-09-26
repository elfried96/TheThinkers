#!/usr/bin/env python3
"""
Script de test pour valider toutes les corrections apportées
"""

import sys
import os
import subprocess
import json
import requests
import time
from pathlib import Path

class CorrectionsValidator:
    def __init__(self):
        self.results = {
            "api_ia": {"status": "unknown", "details": []},
            "andfchat": {"status": "unknown", "details": []},
            "overall": {"status": "unknown", "score": 0}
        }
        
    def test_api_ia_imports(self):
        """Test des imports de l'API IA"""
        print("🔍 Test API IA - Imports...")
        try:
            # Test dans le dossier IA
            result = subprocess.run([
                "python", "-c", 
                "import main_final; from main_final import SpatialOverlay; print('✅ Imports OK')"
            ], capture_output=True, text=True, cwd="IA")
            
            if result.returncode == 0:
                self.results["api_ia"]["details"].append("✅ Imports réussis")
                return True
            else:
                self.results["api_ia"]["details"].append(f"❌ Import échoué: {result.stderr}")
                return False
        except Exception as e:
            self.results["api_ia"]["details"].append(f"❌ Erreur test imports: {e}")
            return False
    
    def test_spatial_overlay(self):
        """Test de la détection des couches géospatiales"""
        print("🗺️ Test détection couches géospatiales...")
        try:
            # Test depuis le dossier IA
            result = subprocess.run([
                "python", "-c", 
                """
import logging
logging.basicConfig(level=logging.INFO)
from main_final import SpatialOverlay
overlay = SpatialOverlay()
print(f'Répertoire: {overlay.geojson_dir}')
print(f'Existe: {overlay.geojson_dir.exists()}')
if overlay.geojson_dir.exists():
    files = list(overlay.geojson_dir.glob('*.geojson'))
    print(f'Fichiers GeoJSON: {len(files)}')
"""
            ], capture_output=True, text=True, cwd="IA")
            
            output = result.stdout + result.stderr
            if "Fichiers GeoJSON:" in output and result.returncode == 0:
                self.results["api_ia"]["details"].append("✅ Détection couches OK")
                return True
            else:
                self.results["api_ia"]["details"].append(f"❌ Détection couches échouée: {output}")
                return False
        except Exception as e:
            self.results["api_ia"]["details"].append(f"❌ Erreur test couches: {e}")
            return False
    
    def test_andfchat_imports(self):
        """Test des imports ANDFChat"""
        print("🤖 Test ANDFChat - Imports...")
        try:
            result = subprocess.run([
                "python", "-c", 
                "import chromadb; import enhanced_backend; print('✅ Imports ANDFChat OK')"
            ], capture_output=True, text=True, cwd="IA/ANDFChat")
            
            if result.returncode == 0:
                self.results["andfchat"]["details"].append("✅ Imports réussis (chromadb inclus)")
                return True
            else:
                self.results["andfchat"]["details"].append(f"❌ Import échoué: {result.stderr}")
                return False
        except Exception as e:
            self.results["andfchat"]["details"].append(f"❌ Erreur test imports: {e}")
            return False
    
    def test_andfchat_endpoints(self):
        """Test de la présence des endpoints ANDFChat"""
        print("🌐 Test ANDFChat - Endpoints...")
        try:
            # Chercher les endpoints dans le fichier
            backend_file = Path("IA/ANDFChat/enhanced_backend.py")
            if not backend_file.exists():
                self.results["andfchat"]["details"].append("❌ Fichier enhanced_backend.py introuvable")
                return False
            
            content = backend_file.read_text()
            
            endpoints = ["/procedures", "/search", "/chat"]
            found_endpoints = []
            
            for endpoint in endpoints:
                if f'"{endpoint}"' in content or f"'{endpoint}'" in content:
                    found_endpoints.append(endpoint)
            
            if len(found_endpoints) == len(endpoints):
                self.results["andfchat"]["details"].append(f"✅ Endpoints trouvés: {found_endpoints}")
                return True
            else:
                missing = set(endpoints) - set(found_endpoints)
                self.results["andfchat"]["details"].append(f"❌ Endpoints manquants: {missing}")
                return False
                
        except Exception as e:
            self.results["andfchat"]["details"].append(f"❌ Erreur test endpoints: {e}")
            return False
    
    def test_docker_files(self):
        """Test de la présence des Dockerfiles"""
        print("🐳 Test Dockerfiles...")
        
        docker_files = [
            "IA/Dockerfile",
            "IA/ANDFChat/Dockerfile", 
            "docker-compose.yml"
        ]
        
        all_present = True
        for docker_file in docker_files:
            if Path(docker_file).exists():
                print(f"   ✅ {docker_file}")
            else:
                print(f"   ❌ {docker_file} manquant")
                all_present = False
        
        return all_present
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🚀 Validation des Corrections HackIA2025")
        print("=" * 50)
        
        # Tests API IA
        print("\n📍 API EXTRACTION COORDONNÉES")
        print("-" * 30)
        
        tests_ia = [
            self.test_api_ia_imports(),
            self.test_spatial_overlay()
        ]
        
        if all(tests_ia):
            self.results["api_ia"]["status"] = "success"
            print("✅ API IA - Tous les tests passent")
        else:
            self.results["api_ia"]["status"] = "failed"
            print("❌ API IA - Certains tests échouent")
        
        # Tests ANDFChat
        print("\n🤖 ANDFCHAT")
        print("-" * 30)
        
        tests_andf = [
            self.test_andfchat_imports(),
            self.test_andfchat_endpoints()
        ]
        
        if all(tests_andf):
            self.results["andfchat"]["status"] = "success"
            print("✅ ANDFChat - Tous les tests passent")
        else:
            self.results["andfchat"]["status"] = "failed"
            print("❌ ANDFChat - Certains tests échouent")
        
        # Tests Docker
        print("\n🐳 DOCKER")
        print("-" * 30)
        docker_ok = self.test_docker_files()
        
        # Calcul du score global
        total_tests = len(tests_ia) + len(tests_andf) + (1 if docker_ok else 0)
        passed_tests = sum(tests_ia) + sum(tests_andf) + (1 if docker_ok else 0)
        score = (passed_tests / max(total_tests, 1)) * 100
        
        self.results["overall"]["score"] = score
        
        if score >= 80:
            self.results["overall"]["status"] = "success"
        elif score >= 60:
            self.results["overall"]["status"] = "warning"
        else:
            self.results["overall"]["status"] = "failed"
        
        # Rapport final
        print(f"\n{'='*50}")
        print("📊 RAPPORT DE VALIDATION")
        print(f"{'='*50}")
        print(f"Score global: {score:.1f}%")
        
        if score >= 80:
            print("🎉 Corrections validées avec succès !")
            print("✅ Prêt pour le déploiement")
        elif score >= 60:
            print("⚠️ Corrections partielles - Quelques ajustements nécessaires")
        else:
            print("❌ Corrections insuffisantes - Révision nécessaire")
        
        # Détails par service
        print(f"\n📍 API IA: {self.results['api_ia']['status'].upper()}")
        for detail in self.results["api_ia"]["details"]:
            print(f"   {detail}")
        
        print(f"\n🤖 ANDFChat: {self.results['andfchat']['status'].upper()}")
        for detail in self.results["andfchat"]["details"]:
            print(f"   {detail}")
        
        return score >= 80
    
    def save_report(self):
        """Sauvegarde le rapport de validation"""
        report_file = "validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Rapport sauvegardé: {report_file}")

def main():
    """Fonction principale"""
    validator = CorrectionsValidator()
    
    try:
        success = validator.run_all_tests()
        validator.save_report()
        
        if success:
            print("\n🎯 Toutes les corrections sont opérationnelles !")
            print("🚀 Vous pouvez procéder au déploiement")
            return 0
        else:
            print("\n⚠️ Certaines corrections nécessitent une attention")
            print("🔧 Consultez le rapport pour les détails")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Test interrompu par l'utilisateur")
        return 130
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())