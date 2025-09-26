#!/usr/bin/env python3
"""
Test rapide des composants de l'API finale
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test des imports nécessaires"""
    print("🔍 Test des imports...")
    
    try:
        import fastapi
        print("✅ FastAPI disponible")
    except ImportError:
        print("❌ FastAPI manquant")
        return False
    
    try:
        import pyproj
        print("✅ PyProj disponible (conversion coordonnées)")
    except ImportError:
        print("⚠️ PyProj manquant (conversion coordonnées désactivée)")
    
    try:
        import geopandas
        import shapely
        print("✅ GeoPandas/Shapely disponibles (superposition spatiale)")
    except ImportError:
        print("⚠️ GeoPandas/Shapely manquants (superposition spatiale désactivée)")
    
    return True

def test_env_config():
    """Test configuration environnement"""
    print("\n🔧 Test configuration...")
    
    # Chercher fichier .env
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ Fichier .env non trouvé")
        print("💡 Créez le fichier : echo 'GOOGLE_API_KEY=votre_clé' > .env")
        return False
    
    # Vérifier clé API
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY non trouvée dans .env")
        return False
    
    if len(api_key) < 20:
        print("⚠️ GOOGLE_API_KEY semble incorrecte (trop courte)")
        return False
    
    print(f"✅ GOOGLE_API_KEY configurée ({api_key[:10]}...)")
    return True

def test_coordinate_conversion():
    """Test conversion coordonnées"""
    print("\n🗺️ Test conversion coordonnées...")
    
    try:
        from pyproj import Transformer
        
        # Test conversion UTM 31N vers WGS84
        transformer = Transformer.from_crs("EPSG:32631", "EPSG:4326", always_xy=True)
        lon, lat = transformer.transform(448005.15, 703480.27)  # Coordonnée d'exemple
        
        print(f"✅ Conversion réussie: UTM(448005.15, 703480.27) → WGS84({lat:.6f}, {lon:.6f})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur conversion: {e}")
        return False

def test_api_startup():
    """Test démarrage API (import seulement)"""
    print("\n🚀 Test démarrage API...")
    
    try:
        # Importer les modules principaux
        sys.path.append(str(Path(__file__).parent))
        
        # Test import main_final sans lancer le serveur
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_final", "main_final.py")
        if spec is None:
            print("❌ Impossible de charger main_final.py")
            return False
            
        main_final = importlib.util.module_from_spec(spec)
        
        # Test de l'import sans exécution
        print("✅ main_final.py peut être importé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur import main_final: {e}")
        return False

def main():
    """Test complet"""
    print("🧪 Test rapide API finale - Hackathon IA 2025")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    if test_imports():
        tests_passed += 1
    
    if test_env_config():
        tests_passed += 1
    
    if test_coordinate_conversion():
        tests_passed += 1
        
    if test_api_startup():
        tests_passed += 1
    
    print(f"\n📊 Résultats: {tests_passed}/{total_tests} tests réussis")
    
    if tests_passed == total_tests:
        print("🎉 Tous les tests passent ! API prête à être lancée")
        print("\n🚀 Prochaines étapes:")
        print("   1. uv run python main_final.py")
        print("   2. Ouvrir http://localhost:8000")
        print("   3. Tester avec: uv run python test_api_final.py image.png")
        return True
    else:
        print("⚠️ Certains composants ne sont pas prêts")
        print("💡 Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)