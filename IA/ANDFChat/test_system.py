"""
Script de test du système ANDF Chatbot
======================================
Tests complets du système RAG et de l'API FastAPI
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
import httpx
import time

# Configuration du logging pour les tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ANDFTestSuite:
    """Suite de tests complète pour le système ANDF"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    async def run_all_tests(self):
        """Exécute tous les tests"""
        logger.info("🧪 Démarrage de la suite de tests ANDF")
        
        try:
            # Tests de validation des données
            await self.test_data_validation()
            
            # Tests du système RAG (sans API)
            await self.test_rag_system()
            
            # Tests de l'API (nécessite que le serveur soit lancé)
            await self.test_api_endpoints()
            
            # Tests d'intégration complète
            await self.test_integration()
            
            # Rapport final
            self.print_test_report()
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans les tests: {e}")
            self.test_results["errors"].append(str(e))
    
    async def test_data_validation(self):
        """Valide la structure et le contenu des données"""
        logger.info("📊 Test de validation des données...")
        
        try:
            # Test 1: Vérification des fichiers
            data_dir = Path("./data")
            required_files = [
                "andf_knowledge_base.json",
                "training_qa_dataset.json", 
                "sources_metadata.txt"
            ]
            
            for file_name in required_files:
                file_path = data_dir / file_name
                if not file_path.exists():
                    raise FileNotFoundError(f"Fichier manquant: {file_name}")
                
                if file_name.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            logger.info(f"✅ {file_name} - Structure JSON valide")
                        except json.JSONDecodeError as e:
                            raise ValueError(f"JSON invalide dans {file_name}: {e}")
            
            # Test 2: Validation du contenu de la knowledge base
            with open(data_dir / "andf_knowledge_base.json", 'r', encoding='utf-8') as f:
                kb = json.load(f)
                
                required_sections = [
                    "procedures_principales",
                    "tarifs_detailles", 
                    "base_juridique",
                    "definitions_cles"
                ]
                
                for section in required_sections:
                    if section not in kb:
                        raise KeyError(f"Section manquante: {section}")
                
                logger.info("✅ Structure de la knowledge base validée")
            
            # Test 3: Validation du dataset Q&A
            with open(data_dir / "training_qa_dataset.json", 'r', encoding='utf-8') as f:
                qa_data = json.load(f)
                
                if "training_dataset" not in qa_data:
                    raise KeyError("Section 'training_dataset' manquante")
                
                qa_pairs = qa_data["training_dataset"].get("qa_pairs", [])
                if len(qa_pairs) < 10:
                    raise ValueError(f"Pas assez de Q&A: {len(qa_pairs)} trouvées, minimum 10")
                
                # Vérification de la structure des Q&A
                for qa in qa_pairs[:5]:  # Teste les 5 premières
                    required_fields = ["question", "answer", "category", "intent"]
                    for field in required_fields:
                        if field not in qa:
                            raise KeyError(f"Champ manquant dans Q&A: {field}")
                
                logger.info(f"✅ Dataset Q&A validé ({len(qa_pairs)} paires)")
            
            self.test_results["passed"] += 3
            logger.info("✅ Tests de validation des données réussis")
            
        except Exception as e:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Validation données: {e}")
            logger.error(f"❌ Test validation données échoué: {e}")
    
    async def test_rag_system(self):
        """Teste le système RAG directement"""
        logger.info("🤖 Test du système RAG...")
        
        try:
            from rag_system import ANDFRAGSystem
            
            # Test 1: Initialisation
            rag = ANDFRAGSystem()
            await rag.initialize()
            logger.info("✅ Système RAG initialisé")
            
            # Test 2: Requêtes de base
            test_queries = [
                "Comment obtenir un titre foncier ?",
                "Combien coûte un certificat d'appartenance ?",
                "Où se trouve le BCDF de Cotonou ?",
                "Quels documents pour une mutation ?"
            ]
            
            for query in test_queries:
                result = await rag.process_query(query)
                
                # Vérifications
                if not result.get("response"):
                    raise ValueError(f"Pas de réponse pour: {query}")
                
                if result.get("confidence", 0) < 0.1:
                    logger.warning(f"⚠️ Confiance faible pour: {query}")
                
                logger.info(f"✅ Requête traitée: {query[:30]}... (confiance: {result.get('confidence', 0):.2f})")
            
            # Test 3: Recherche dans les collections
            search_results = await rag.search_knowledge("titre foncier", limit=3)
            if len(search_results) == 0:
                raise ValueError("Aucun résultat de recherche")
            
            logger.info(f"✅ Recherche testée ({len(search_results)} résultats)")
            
            # Test 4: Récupération des données
            procedures = await rag.get_procedures()
            if len(procedures) == 0:
                raise ValueError("Aucune procédure trouvée")
            
            tarifs = await rag.get_tarifs()
            if not tarifs:
                raise ValueError("Aucun tarif trouvé")
            
            stats = await rag.get_stats()
            if stats.get("queries_processed", 0) < len(test_queries):
                raise ValueError("Stats incorrectes")
            
            logger.info("✅ Données accessibles via l'API")
            
            # Nettoyage
            await rag.cleanup()
            
            self.test_results["passed"] += 4
            logger.info("✅ Tests du système RAG réussis")
            
        except ImportError as e:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Import RAG: {e}")
            logger.error(f"❌ Impossible d'importer le système RAG: {e}")
        except Exception as e:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Test RAG: {e}")
            logger.error(f"❌ Test système RAG échoué: {e}")
    
    async def test_api_endpoints(self):
        """Teste les endpoints de l'API"""
        logger.info("🌐 Test des endpoints API...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # Test 1: Health check
                try:
                    response = await client.get(f"{self.base_url}/health")
                    if response.status_code == 200:
                        logger.info("✅ Endpoint /health accessible")
                        self.test_results["passed"] += 1
                    else:
                        raise httpx.HTTPError(f"Health check failed: {response.status_code}")
                except httpx.ConnectError:
                    logger.warning("⚠️ API non accessible - serveur probablement arrêté")
                    logger.info("💡 Pour tester l'API, lancez: python main.py")
                    return
                
                # Test 2: Root endpoint
                response = await client.get(f"{self.base_url}/")
                if response.status_code == 200:
                    logger.info("✅ Endpoint / accessible")
                    self.test_results["passed"] += 1
                
                # Test 3: Chat endpoint
                chat_payload = {
                    "message": "Comment obtenir un titre foncier ?",
                    "session_id": "test_session"
                }
                
                response = await client.post(f"{self.base_url}/chat", json=chat_payload)
                if response.status_code == 200:
                    chat_data = response.json()
                    if "response" in chat_data and "confidence" in chat_data:
                        logger.info("✅ Endpoint /chat fonctionnel")
                        self.test_results["passed"] += 1
                    else:
                        raise ValueError("Réponse chat incomplète")
                
                # Test 4: Procedures endpoint
                response = await client.get(f"{self.base_url}/procedures")
                if response.status_code == 200:
                    procedures = response.json()
                    if isinstance(procedures, list) and len(procedures) > 0:
                        logger.info("✅ Endpoint /procedures fonctionnel")
                        self.test_results["passed"] += 1
                
                # Test 5: Search endpoint
                response = await client.get(f"{self.base_url}/search?q=titre foncier&limit=3")
                if response.status_code == 200:
                    search_data = response.json()
                    if "results" in search_data:
                        logger.info("✅ Endpoint /search fonctionnel")
                        self.test_results["passed"] += 1
                
                logger.info("✅ Tests des endpoints API réussis")
                
        except Exception as e:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Test API: {e}")
            logger.error(f"❌ Test endpoints API échoué: {e}")
    
    async def test_integration(self):
        """Tests d'intégration complète"""
        logger.info("🔗 Tests d'intégration...")
        
        try:
            # Simulation d'une conversation complète
            test_conversation = [
                "Bonjour",
                "Je veux obtenir un titre foncier",
                "Combien ça coûte ?", 
                "Quels documents dois-je fournir ?",
                "Où se trouve le BCDF de Cotonou ?"
            ]
            
            session_id = "integration_test"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for i, message in enumerate(test_conversation):
                    try:
                        payload = {
                            "message": message,
                            "session_id": session_id
                        }
                        
                        response = await client.post(f"{self.base_url}/chat", json=payload)
                        if response.status_code == 200:
                            data = response.json()
                            logger.info(f"✅ Message {i+1}/5 traité (confiance: {data.get('confidence', 0):.2f})")
                        else:
                            raise httpx.HTTPError(f"Erreur message {i+1}: {response.status_code}")
                        
                        # Pause entre les messages
                        await asyncio.sleep(0.5)
                        
                    except httpx.ConnectError:
                        logger.warning("⚠️ API non accessible pour les tests d'intégration")
                        return
            
            self.test_results["passed"] += 1
            logger.info("✅ Test d'intégration réussi")
            
        except Exception as e:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Intégration: {e}")
            logger.error(f"❌ Test d'intégration échoué: {e}")
    
    def print_test_report(self):
        """Affiche le rapport de test final"""
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*50)
        print("📊 RAPPORT DE TEST ANDF CHATBOT")
        print("="*50)
        print(f"✅ Tests réussis: {self.test_results['passed']}")
        print(f"❌ Tests échoués: {self.test_results['failed']}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.test_results["errors"]:
            print("\n🔍 ERREURS DÉTAILLÉES:")
            for i, error in enumerate(self.test_results["errors"], 1):
                print(f"{i}. {error}")
        
        if success_rate >= 80:
            print("\n🎉 SYSTÈME PRÊT POUR LA PRODUCTION!")
        elif success_rate >= 60:
            print("\n⚠️ Système fonctionnel avec quelques améliorations nécessaires")
        else:
            print("\n❌ Système nécessite des corrections importantes")
        
        print("="*50)

# Scripts utilitaires

async def test_quick():
    """Test rapide des fonctionnalités de base"""
    print("⚡ Test rapide du système ANDF...")
    
    try:
        from rag_system import ANDFRAGSystem
        
        rag = ANDFRAGSystem()
        await rag.initialize()
        
        result = await rag.process_query("Combien coûte un titre foncier ?")
        print(f"✅ Réponse: {result['response'][:100]}...")
        print(f"✅ Confiance: {result['confidence']:.2f}")
        
        await rag.cleanup()
        print("✅ Test rapide réussi!")
        
    except Exception as e:
        print(f"❌ Test rapide échoué: {e}")

def install_dependencies():
    """Installe les dépendances nécessaires"""
    import subprocess
    
    print("📦 Installation des dépendances...")
    
    try:
        # Installation via pip
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dépendances installées")
        
        # Installation du modèle spaCy français (optionnel)
        try:
            subprocess.run([sys.executable, "-m", "spacy", "download", "fr_core_news_sm"], check=False)
            print("✅ Modèle français spaCy installé")
        except:
            print("⚠️ Modèle spaCy français non installé (optionnel)")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation: {e}")

def check_system():
    """Vérification rapide du système"""
    print("🔍 Vérification du système...")
    
    # Vérification Python
    print(f"🐍 Python: {sys.version}")
    
    # Vérification des fichiers
    required_files = [
        "main.py",
        "rag_system.py", 
        "config.py",
        "requirements.txt",
        "data/andf_knowledge_base.json",
        "data/training_qa_dataset.json"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} MANQUANT")
    
    print("🔍 Vérification terminée")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tests du système ANDF Chatbot")
    parser.add_argument("--action", choices=["full", "quick", "install", "check"], 
                       default="full", help="Action à exécuter")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="URL de base de l'API")
    
    args = parser.parse_args()
    
    if args.action == "install":
        install_dependencies()
    elif args.action == "check":
        check_system()
    elif args.action == "quick":
        asyncio.run(test_quick())
    else:
        # Test complet
        suite = ANDFTestSuite()
        suite.base_url = args.url
        asyncio.run(suite.run_all_tests())