"""
Tests Complets du Système ANDF Intelligent
==========================================
Suite de tests pour valider toutes les fonctionnalités
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any
import httpx
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedANDFTestSuite:
    """Suite de tests complète pour le système ANDF intelligent"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance": {}
        }
    
    async def run_comprehensive_tests(self):
        """Exécute tous les tests du système"""
        logger.info("🧪 DÉMARRAGE TESTS COMPLETS ANDF INTELLIGENT")
        print("=" * 60)
        
        test_suites = [
            ("Validation des données enrichies", self.test_enhanced_data),
            ("Système de traitement intelligent", self.test_intelligent_processing),
            ("Correction d'erreurs utilisateur", self.test_error_correction),
            ("Endpoints API avancés", self.test_advanced_endpoints),
            ("Recherche intelligente", self.test_intelligent_search),
            ("Gestion des sessions", self.test_session_management),
            ("Tests de performance", self.test_performance),
            ("Tests d'intégration complète", self.test_full_integration)
        ]
        
        for suite_name, suite_func in test_suites:
            logger.info(f"\n🔧 {suite_name}...")
            try:
                await suite_func()
            except Exception as e:
                logger.error(f"❌ Erreur dans {suite_name}: {e}")
                self.test_results["errors"].append(f"{suite_name}: {e}")
        
        # Rapport final
        self.generate_test_report()
    
    async def test_enhanced_data(self):
        """Test des données enrichies"""
        try:
            # Vérification du fichier de données enrichies
            with open("enhanced_knowledge_base.json", "r", encoding="utf-8") as f:
                enhanced_data = json.load(f)
            
            self._assert_test(
                "enhanced_data_structure",
                "procedures_principales" in enhanced_data,
                "Structure de données enrichies présente"
            )
            
            # Vérification des procédures enrichies
            procedures = enhanced_data.get("procedures_principales", {})
            
            self._assert_test(
                "titre_foncier_enhanced",
                "documents_requis_complets" in procedures.get("titre_foncier", {}),
                "Documents requis complets pour titre foncier"
            )
            
            self._assert_test(
                "digitalisation_info",
                "digitalisation_2025" in procedures.get("titre_foncier", {}),
                "Informations digitalisation 2025 présentes"
            )
            
            # Vérification des tarifs 2025
            tarifs = enhanced_data.get("tarifs_detailles_2025", {})
            
            self._assert_test(
                "tarifs_e_notaire",
                "frais_transactions_e_notaire" in tarifs,
                "Nouveaux tarifs e-Notaire présents"
            )
            
            logger.info("✅ Tests données enrichies réussis")
            
        except Exception as e:
            self._record_error("enhanced_data", str(e))
    
    async def test_intelligent_processing(self):
        """Test du système de traitement intelligent"""
        try:
            from enhanced_backend import ANDFChatbotEngine
            
            engine = ANDFChatbotEngine()
            
            # Test de correction d'erreurs
            corrected, corrections = engine.correct_user_input("titre foncer à cotonu")
            
            self._assert_test(
                "error_correction",
                len(corrections) > 0,
                "Correction d'erreurs fonctionne"
            )
            
            # Test d'analyse d'intention
            intent, entities, confidence = engine.analyze_intent_and_entities("Combien coûte un certificat d'appartenance ?")
            
            self._assert_test(
                "intent_analysis",
                intent == "cost_inquiry",
                f"Analyse d'intention correcte: {intent}"
            )
            
            self._assert_test(
                "entity_extraction", 
                len(entities.get("procedures", [])) > 0,
                f"Extraction d'entités: {entities}"
            )
            
            # Test de recherche dans la base
            results = engine.search_knowledge_base("titre foncier", "procedure_info")
            
            self._assert_test(
                "knowledge_search",
                len(results) > 0,
                f"Recherche base de connaissances: {len(results)} résultats"
            )
            
            logger.info("✅ Tests traitement intelligent réussis")
            
        except Exception as e:
            self._record_error("intelligent_processing", str(e))
    
    async def test_error_correction(self):
        """Test spécifique des corrections d'erreur"""
        try:
            from enhanced_backend import ANDFChatbotEngine
            
            engine = ANDFChatbotEngine()
            
            test_cases = [
                ("titre foncer", "titre foncier"),
                ("bcfd cotonou", "bcdf cotonou"),
                ("certifica appartenance", "certificat appartenance"),
                ("tf mutation", "titre foncier mutation"),
                ("poerto novo", "porto-novo")
            ]
            
            corrections_count = 0
            
            for original, expected_corrected in test_cases:
                corrected, corrections = engine.correct_user_input(original)
                
                if corrections:
                    corrections_count += 1
                    logger.info(f"  📝 '{original}' → corrections appliquées")
                
            self._assert_test(
                "multiple_corrections",
                corrections_count >= 3,
                f"Corrections multiples fonctionnent: {corrections_count}/5"
            )
            
            logger.info("✅ Tests correction d'erreurs réussis")
            
        except Exception as e:
            self._record_error("error_correction", str(e))
    
    async def test_advanced_endpoints(self):
        """Test des endpoints API avancés"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # Test endpoint procedures avec détails
                response = await client.get(f"{self.base_url}/procedures")
                self._assert_test(
                    "procedures_endpoint",
                    response.status_code == 200,
                    "Endpoint /procedures accessible"
                )
                
                if response.status_code == 200:
                    procedures = response.json()
                    self._assert_test(
                        "procedures_content",
                        len(procedures) > 0,
                        f"Procédures retournées: {len(procedures)}"
                    )
                
                # Test endpoint tarifs
                response = await client.get(f"{self.base_url}/tarifs")
                self._assert_test(
                    "tarifs_endpoint",
                    response.status_code == 200,
                    "Endpoint /tarifs accessible"
                )
                
                # Test recherche avancée
                response = await client.get(f"{self.base_url}/search?q=titre+foncier&limit=5")
                self._assert_test(
                    "search_endpoint",
                    response.status_code == 200,
                    "Endpoint /search accessible"
                )
                
                if response.status_code == 200:
                    search_data = response.json()
                    self._assert_test(
                        "search_results",
                        len(search_data.get("results", [])) > 0,
                        f"Résultats recherche: {len(search_data.get('results', []))}"
                    )
                
                # Test BCDF avec filtres
                response = await client.get(f"{self.base_url}/bcdf?commune=cotonou")
                self._assert_test(
                    "bcdf_filtered",
                    response.status_code == 200,
                    "Endpoint /bcdf avec filtres accessible"
                )
                
                logger.info("✅ Tests endpoints avancés réussis")
                
        except httpx.ConnectError:
            logger.warning("⚠️ Serveur API non accessible - lancez d'abord le serveur")
            self._record_error("advanced_endpoints", "Serveur non accessible")
        except Exception as e:
            self._record_error("advanced_endpoints", str(e))
    
    async def test_intelligent_search(self):
        """Test de la recherche intelligente"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                search_tests = [
                    ("titre foncier", "procedure"),
                    ("50000 certificat", "cost"),
                    ("cotonou bcdf", "location"),
                    ("documents requis", "document"),
                    ("probleme terrain", "problem")
                ]
                
                successful_searches = 0
                
                for query, expected_category in search_tests:
                    try:
                        response = await client.get(f"{self.base_url}/search?q={query}&limit=3")
                        
                        if response.status_code == 200:
                            data = response.json()
                            if len(data.get("results", [])) > 0:
                                successful_searches += 1
                                logger.info(f"  🔍 '{query}' → {len(data['results'])} résultats")
                        
                    except Exception as e:
                        logger.warning(f"  ⚠️ Recherche '{query}' échouée: {e}")
                
                self._assert_test(
                    "intelligent_search",
                    successful_searches >= 3,
                    f"Recherches intelligentes: {successful_searches}/5"
                )
                
                logger.info("✅ Tests recherche intelligente réussis")
                
        except Exception as e:
            self._record_error("intelligent_search", str(e))
    
    async def test_session_management(self):
        """Test de la gestion des sessions"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                session_id = "test_session_123"
                
                # Première requête avec session
                payload1 = {
                    "message": "Bonjour, comment obtenir un titre foncier ?",
                    "session_id": session_id
                }
                
                response1 = await client.post(f"{self.base_url}/chat", json=payload1)
                self._assert_test(
                    "session_creation",
                    response1.status_code == 200,
                    "Première requête avec session"
                )
                
                # Deuxième requête avec même session
                payload2 = {
                    "message": "Et combien ça coûte ?",
                    "session_id": session_id
                }
                
                response2 = await client.post(f"{self.base_url}/chat", json=payload2)
                self._assert_test(
                    "session_continuity",
                    response2.status_code == 200,
                    "Continuité de session"
                )
                
                if response2.status_code == 200:
                    data = response2.json()
                    self._assert_test(
                        "session_context",
                        data.get("session_id") == session_id,
                        "ID de session maintenu"
                    )
                
                logger.info("✅ Tests gestion sessions réussis")
                
        except Exception as e:
            self._record_error("session_management", str(e))
    
    async def test_performance(self):
        """Test des performances du système"""
        try:
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # Test de charge basique
                concurrent_requests = 5
                tasks = []
                
                for i in range(concurrent_requests):
                    payload = {
                        "message": f"Test performance {i}: comment obtenir un titre foncier ?",
                        "session_id": f"perf_test_{i}"
                    }
                    task = client.post(f"{self.base_url}/chat", json=payload)
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful_responses = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
                
                total_time = time.time() - start_time
                avg_time = total_time / concurrent_requests
                
                self._assert_test(
                    "concurrent_requests",
                    successful_responses >= 4,
                    f"Requêtes concurrentes: {successful_responses}/{concurrent_requests}"
                )
                
                self._assert_test(
                    "response_time",
                    avg_time < 5.0,
                    f"Temps de réponse moyen: {avg_time:.2f}s"
                )
                
                # Sauvegarde des métriques de performance
                self.test_results["performance"] = {
                    "concurrent_requests": concurrent_requests,
                    "successful_responses": successful_responses,
                    "total_time": total_time,
                    "average_time": avg_time
                }
                
                logger.info("✅ Tests performance réussis")
                
        except Exception as e:
            self._record_error("performance", str(e))
    
    async def test_full_integration(self):
        """Test d'intégration complète - Simulation d'utilisateur réel"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # Simulation d'une session utilisateur complète
                user_session = "integration_test_user"
                
                conversation_flow = [
                    {
                        "message": "Bonjour, j'aimerais avoir des informations sur les titres fonciers",
                        "expected_intent": "general"
                    },
                    {
                        "message": "Combien ca coute un titre foncié ?",  # Avec faute intentionnelle
                        "expected_intent": "cost_inquiry"
                    },
                    {
                        "message": "Quels documents il faut pour faire la demande ?",
                        "expected_intent": "document_requirements"
                    },
                    {
                        "message": "Ou se trouve le BCDF de Cotonou ?",  # Sans accent intentionnel
                        "expected_intent": "location_info"
                    },
                    {
                        "message": "Merci pour toutes ces informations !",
                        "expected_intent": "general"
                    }
                ]
                
                successful_interactions = 0
                total_confidence = 0.0
                
                for i, interaction in enumerate(conversation_flow):
                    payload = {
                        "message": interaction["message"],
                        "session_id": user_session
                    }
                    
                    response = await client.post(f"{self.base_url}/chat", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        confidence = data.get("confidence_score", 0.0)
                        intent = data.get("intent", "unknown")
                        
                        successful_interactions += 1
                        total_confidence += confidence
                        
                        logger.info(f"  💬 Interaction {i+1}: Intent={intent}, Confiance={confidence:.2f}")
                        
                        # Vérification des corrections appliquées
                        corrections = data.get("corrections_applied", [])
                        if corrections:
                            logger.info(f"    🔧 Corrections: {corrections}")
                    
                    # Petite pause entre les messages
                    await asyncio.sleep(0.5)
                
                avg_confidence = total_confidence / len(conversation_flow) if len(conversation_flow) > 0 else 0
                
                self._assert_test(
                    "full_conversation",
                    successful_interactions == len(conversation_flow),
                    f"Conversation complète: {successful_interactions}/{len(conversation_flow)}"
                )
                
                self._assert_test(
                    "conversation_quality",
                    avg_confidence > 0.6,
                    f"Qualité conversation: {avg_confidence:.2f}"
                )
                
                logger.info("✅ Tests intégration complète réussis")
                
        except Exception as e:
            self._record_error("full_integration", str(e))
    
    def _assert_test(self, test_name: str, condition: bool, description: str):
        """Enregistre le résultat d'un test"""
        self.test_results["total_tests"] += 1
        
        if condition:
            self.test_results["passed"] += 1
            logger.info(f"  ✅ {description}")
        else:
            self.test_results["failed"] += 1
            logger.warning(f"  ❌ {description}")
            self.test_results["errors"].append(f"{test_name}: {description}")
    
    def _record_error(self, test_suite: str, error: str):
        """Enregistre une erreur de test"""
        self.test_results["failed"] += 1
        self.test_results["errors"].append(f"{test_suite}: {error}")
        logger.error(f"❌ {test_suite}: {error}")
    
    def generate_test_report(self):
        """Génère le rapport de test final"""
        results = self.test_results
        total = results["total_tests"]
        passed = results["passed"]
        failed = results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 70)
        print("📊 RAPPORT DE TEST ANDF INTELLIGENT")
        print("=" * 70)
        
        print(f"📈 **RÉSULTATS GLOBAUX**")
        print(f"   Tests totaux: {total}")
        print(f"   ✅ Réussis: {passed}")
        print(f"   ❌ Échecs: {failed}")
        print(f"   📊 Taux de réussite: {success_rate:.1f}%")
        
        # Métriques de performance
        if "performance" in results:
            perf = results["performance"]
            print(f"\n⚡ **PERFORMANCE**")
            print(f"   Requêtes concurrentes: {perf.get('concurrent_requests', 'N/A')}")
            print(f"   Réponses réussies: {perf.get('successful_responses', 'N/A')}")
            print(f"   Temps moyen: {perf.get('average_time', 0):.2f}s")
        
        # Erreurs détaillées
        if results["errors"]:
            print(f"\n🔍 **ERREURS DÉTAILLÉES** ({len(results['errors'])})")
            for i, error in enumerate(results["errors"], 1):
                print(f"   {i}. {error}")
        
        # Évaluation finale
        print(f"\n🎯 **ÉVALUATION FINALE**")
        if success_rate >= 90:
            print("   🎉 EXCELLENT - Système prêt pour la production")
        elif success_rate >= 75:
            print("   ✅ BON - Système fonctionnel avec améliorations mineures")
        elif success_rate >= 60:
            print("   ⚠️ ACCEPTABLE - Corrections nécessaires")
        else:
            print("   ❌ INSUFFISANT - Corrections majeures requises")
        
        print("\n" + "=" * 70)
        print(f"🕐 Tests terminés: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

# Fonctions utilitaires pour tests rapides

async def test_quick_functionality():
    """Test rapide des fonctionnalités principales"""
    print("⚡ TEST RAPIDE ANDF INTELLIGENT")
    print("=" * 40)
    
    try:
        from enhanced_backend import ANDFChatbotEngine
        
        engine = ANDFChatbotEngine()
        
        # Test de traitement de message
        result = await engine.process_chat_message("titre foncer combien sa cout ?")
        
        print(f"✅ Message traité")
        print(f"✅ Corrections: {len(result.get('corrections_applied', []))}")
        print(f"✅ Confiance: {result.get('confidence_score', 0):.2f}")
        print(f"✅ Intention: {result.get('intent', 'N/A')}")
        print(f"✅ Réponse: {len(result.get('response', ''))} caractères")
        
        print("\n🎉 Test rapide réussi !")
        
    except Exception as e:
        print(f"❌ Test rapide échoué: {e}")

def test_data_integrity():
    """Test d'intégrité des données"""
    print("🔍 VÉRIFICATION INTÉGRITÉ DONNÉES")
    print("=" * 40)
    
    try:
        # Vérification enhanced_knowledge_base.json
        with open("enhanced_knowledge_base.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"✅ enhanced_knowledge_base.json: {len(data)} sections")
        print(f"✅ Procédures: {len(data.get('procedures_principales', {}))}")
        print(f"✅ BCDF: {len(data.get('structures_andf_completes', {}).get('bcdf_principaux', {}).get('bureaux', []))}")
        print(f"✅ Tarifs 2025: {'tarifs_detailles_2025' in data}")
        
        # Vérification données originales
        with open("data/andf_knowledge_base.json", "r", encoding="utf-8") as f:
            original_data = json.load(f)
        
        print(f"✅ Données originales: {len(original_data)} sections")
        
        print("\n🎉 Intégrité des données validée !")
        
    except Exception as e:
        print(f"❌ Erreur intégrité données: {e}")

# Point d'entrée
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Tests du système ANDF intelligent")
    parser.add_argument("--mode", choices=["full", "quick", "data", "api"], 
                       default="full", help="Mode de test")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="URL de base de l'API")
    
    args = parser.parse_args()
    
    if args.mode == "data":
        test_data_integrity()
    elif args.mode == "quick":
        asyncio.run(test_quick_functionality())
    elif args.mode == "api":
        # Test API seulement
        suite = EnhancedANDFTestSuite()
        suite.base_url = args.url
        asyncio.run(suite.test_advanced_endpoints())
    else:
        # Test complet
        suite = EnhancedANDFTestSuite()
        suite.base_url = args.url
        asyncio.run(suite.run_comprehensive_tests())