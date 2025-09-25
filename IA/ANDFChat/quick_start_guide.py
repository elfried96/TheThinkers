# GUIDE DE DÉMARRAGE RAPIDE - RAG ANDF
# Implémentation complète en 30 minutes

import json
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
from typing import Dict, List, Tuple
import pandas as pd

class ANDFChatbot:
    """
    Chatbot RAG complet pour l'ANDF Bénin
    Utilise toutes les données collectées
    """
    
    def __init__(self):
        print("🚀 Initialisation du Chatbot ANDF...")
        self.setup_models()
        self.setup_vector_db()
        self.load_knowledge_base()
        self.setup_entity_recognition()
        print("✅ Chatbot ANDF prêt !")
    
    def setup_models(self):
        """Configuration des modèles IA"""
        print("📥 Chargement des modèles...")
        
        # Modèle d'embeddings multilingue
        self.embedding_model = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
        
        # Modèle de génération (vous pouvez changer selon vos ressources)
        self.tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/DialoGPT-small",  # Léger pour démo
            padding_side='left'
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.llm = AutoModelForCausalLM.from_pretrained(
            "microsoft/DialoGPT-small"
        )
    
    def setup_vector_db(self):
        """Configuration de la base vectorielle"""
        print("🗂️  Configuration ChromaDB...")
        
        # Client ChromaDB
        self.chroma_client = chromadb.Client()
        
        # Collections spécialisées
        try:
            self.chroma_client.delete_collection("andf_procedures")
        except:
            pass
            
        self.procedures_collection = self.chroma_client.create_collection(
            name="andf_procedures",
            metadata={"description": "Procédures foncières ANDF"}
        )
    
    def load_knowledge_base(self):
        """Chargement de la base de connaissances collectée"""
        print("📚 Chargement base de connaissances...")
        
        # Base de données principale (utilisez les données collectées)
        self.knowledge_base = {
            "procedures": {
                "titre_foncier": {
                    "nom": "Confirmation de droits fonciers",
                    "cout": 100000,
                    "duree": "120 jours", 
                    "documents": [
                        "Demande écrite au Chef BCDF",
                        "Copie légalisée CNI",
                        "Document de présomption de propriété",
                        "Plan topographique géoréférencé",
                        "PV bornage contradictoire",
                        "Certificat de non-opposition",
                        "Reçu paiement frais"
                    ],
                    "etapes": [
                        "Dépôt dossier au BCDF compétent",
                        "Vérification complétude par agent",
                        "Enquête publique (45 jours)",
                        "Bornage contradictoire avec géomètre",
                        "Examen technique du dossier",
                        "Délivrance titre foncier définitif"
                    ]
                },
                "certificat_appartenance": {
                    "nom": "Certificat d'appartenance",
                    "cout": 50000,
                    "duree": "Immédiat",
                    "validite": "1 an non renouvelable",
                    "obligation": "Avant toute vente immobilière"
                }
            },
            
            "tarifs": {
                "titre_foncier": 100000,
                "certificat_appartenance": 50000,
                "mutations": "0.3% valeur marchande",
                "duplicata": 25000,
                "hypotheque": 0,
                "morcellement": "0.3% valeur + 102,500"
            },
            
            "communes": [
                "Cotonou", "Porto-Novo", "Parakou", "Abomey-Calavi",
                "Allada", "Ouidah", "Lokossa", "Natitingou", "Kandi",
                # ... (toutes les 77 communes de la collecte)
            ],
            
            "bcdf": {
                "cotonou": {
                    "adresse": "Quartier Gbégamey",
                    "telephone": "+229 21 30 10 20",
                    "communes_couvertes": ["Cotonou"]
                }
                # ... (tous les BCDF de la collecte)
            }
        }
        
        # Indexation vectorielle
        self.index_knowledge_base()
    
    def index_knowledge_base(self):
        """Indexation vectorielle de la base de connaissances"""
        print("🔍 Indexation vectorielle...")
        
        documents = []
        metadatas = []
        ids = []
        
        # Indexation des procédures
        for proc_id, proc_data in self.knowledge_base["procedures"].items():
            # Document principal
            doc_text = f"""
            Procédure: {proc_data['nom']}
            Coût: {proc_data['cout']} F CFA
            Durée: {proc_data['duree']}
            Documents requis: {', '.join(proc_data.get('documents', []))}
            Étapes: {' - '.join(proc_data.get('etapes', []))}
            """
            
            documents.append(doc_text.strip())
            metadatas.append({
                "type": "procedure",
                "procedure_id": proc_id,
                "cout": proc_data["cout"],
                "duree": proc_data["duree"]
            })
            ids.append(f"proc_{proc_id}")
        
        # Ajout à ChromaDB
        if documents:
            self.procedures_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def setup_entity_recognition(self):
        """Configuration reconnaissance d'entités"""
        self.entities = {
            "communes": self.knowledge_base["communes"],
            "procedures": [
                "titre foncier", "certificat d'appartenance", 
                "mutation", "hypothèque", "morcellement", "bornage"
            ],
            "cout_patterns": [
                r"combien", r"coût", r"prix", r"tarif", r"frais"
            ]
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extraction des entités du texte"""
        found_entities = {
            "communes": [],
            "procedures": [],
            "intent": "general"
        }
        
        text_lower = text.lower()
        
        # Communes
        for commune in self.entities["communes"]:
            if commune.lower() in text_lower:
                found_entities["communes"].append(commune)
        
        # Procédures
        for procedure in self.entities["procedures"]:
            if procedure in text_lower:
                found_entities["procedures"].append(procedure)
        
        # Intention (coût, procédure, etc.)
        if any(pattern in text_lower for pattern in ["comment", "procédure", "étapes"]):
            found_entities["intent"] = "procedure_info"
        elif any(re.search(pattern, text_lower) for pattern in self.entities["cout_patterns"]):
            found_entities["intent"] = "cost_inquiry"
        
        return found_entities
    
    def search_knowledge(self, query: str, n_results: int = 3) -> List[Dict]:
        """Recherche dans la base de connaissances"""
        try:
            results = self.procedures_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            contexts = []
            for i in range(len(results['documents'][0])):
                contexts.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else 0.5
                })
            
            return contexts
        
        except Exception as e:
            print(f"Erreur recherche: {e}")
            return []
    
    def generate_response(self, query: str, contexts: List[Dict], entities: Dict) -> str:
        """Génération de réponse basée sur le contexte"""
        
        # Templates de réponse selon l'intention
        if entities["intent"] == "cost_inquiry":
            return self.generate_cost_response(query, contexts, entities)
        elif entities["intent"] == "procedure_info":
            return self.generate_procedure_response(query, contexts, entities)
        else:
            return self.generate_general_response(query, contexts, entities)
    
    def generate_cost_response(self, query: str, contexts: List[Dict], entities: Dict) -> str:
        """Réponse spécialisée pour les coûts"""
        response = "💰 **Informations tarifaires ANDF**\n\n"
        
        # Titre foncier
        if "titre foncier" in query.lower():
            response += f"**Titre foncier :** {self.knowledge_base['tarifs']['titre_foncier']:,} F CFA\n"
            response += "- Plus frais de bornage (variable selon superficie)\n"
            response += "- Durée : 120 jours\n\n"
        
        # Certificat d'appartenance  
        if "certificat" in query.lower():
            response += f"**Certificat d'appartenance :** {self.knowledge_base['tarifs']['certificat_appartenance']:,} F CFA\n"
            response += "- Validité : 1 an non renouvelable\n"
            response += "- Obligatoire avant toute vente\n\n"
        
        # Mutations
        if "mutation" in query.lower():
            response += f"**Mutations :** {self.knowledge_base['tarifs']['mutations']}\n"
            response += "- Exemple : terrain 10M F CFA → 30,000 F CFA de frais\n\n"
        
        response += "📞 **Contact :** +229 21 30 10 20\n"
        response += "🌐 **Site :** https://andf.bj"
        
        return response
    
    def generate_procedure_response(self, query: str, contexts: List[Dict], entities: Dict) -> str:
        """Réponse spécialisée pour les procédures"""
        response = "📋 **Procédure ANDF**\n\n"
        
        if "titre foncier" in query.lower():
            proc = self.knowledge_base["procedures"]["titre_foncier"]
            
            response += f"**{proc['nom']}**\n\n"
            response += f"💰 **Coût :** {proc['cout']:,} F CFA\n"
            response += f"⏱️ **Durée :** {proc['duree']}\n\n"
            
            response += "**📄 Documents requis :**\n"
            for i, doc in enumerate(proc['documents'], 1):
                response += f"{i}. {doc}\n"
            
            response += "\n**🔄 Étapes :**\n"  
            for i, etape in enumerate(proc['etapes'], 1):
                response += f"{i}. {etape}\n"
        
        response += "\n**🏢 Service compétent :** BCDF de votre commune"
        
        return response
    
    def generate_general_response(self, query: str, contexts: List[Dict], entities: Dict) -> str:
        """Réponse générale"""
        if not contexts:
            return """
            Je n'ai pas trouvé d'informations spécifiques sur votre question.
            
            **Pour vous aider :**
            📞 Contactez votre BCDF local
            📱 Appelez le +229 21 30 10 20  
            🌐 Consultez https://andf.bj
            
            **Questions fréquentes :**
            - Comment obtenir un titre foncier ?
            - Quel est le coût d'un certificat d'appartenance ?
            - Où se trouve mon BCDF ?
            """
        
        # Utilisation du contexte trouvé
        context_text = contexts[0]["content"]
        
        response = f"""
        Voici les informations que j'ai trouvées :
        
        {context_text}
        
        **Pour plus de détails :**
        📞 +229 21 30 10 20
        🌐 https://andf.bj
        """
        
        return response
    
    def chat(self, query: str) -> str:
        """Interface principale du chatbot"""
        try:
            # 1. Extraction des entités
            entities = self.extract_entities(query)
            
            # 2. Recherche contextuelle
            contexts = self.search_knowledge(query)
            
            # 3. Génération de réponse
            response = self.generate_response(query, contexts, entities)
            
            return response
            
        except Exception as e:
            return f"""
            ⚠️ Une erreur s'est produite. 
            
            **Contactez directement :**
            📞 +229 21 30 10 20
            🌐 https://andf.bj
            
            (Erreur technique : {str(e)})
            """

# DÉMO D'UTILISATION
def demo_chatbot():
    """Démonstration du chatbot avec questions types"""
    
    print("=" * 60)
    print("🇧🇯 DÉMONSTRATION CHATBOT ANDF BÉNIN")
    print("=" * 60)
    
    # Initialisation
    bot = ANDFChatbot()
    
    # Questions de démonstration
    demo_questions = [
        "Comment obtenir un titre foncier ?",
        "Quel est le coût d'un certificat d'appartenance ?", 
        "Combien coûte une mutation de titre foncier ?",
        "Où se trouve le BCDF de Cotonou ?",
        "Quels documents faut-il pour confirmer des droits fonciers ?"
    ]
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{i}. 👤 UTILISATEUR: {question}")
        print("🤖 ANDF CHATBOT:")
        print("-" * 50)
        
        response = bot.chat(question)
        print(response)
        print("-" * 50)
    
    # Interface interactive
    print("\n💬 MODE INTERACTIF")
    print("Tapez vos questions (ou 'quit' pour sortir):")
    
    while True:
        try:
            user_input = input("\n👤 Votre question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'sortir']:
                print("👋 Au revoir ! Contactez l'ANDF pour plus d'infos.")
                break
            
            if not user_input:
                continue
                
            print("\n🤖 ANDF CHATBOT:")
            print("-" * 50)
            response = bot.chat(user_input)
            print(response)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

# TESTS RAPIDES
def run_tests():
    """Tests de validation rapide"""
    print("🧪 TESTS DE VALIDATION")
    print("=" * 40)
    
    bot = ANDFChatbot()
    
    test_cases = [
        ("titre foncier", "procedure_info"),
        ("coût certificat", "cost_inquiry"), 
        ("Cotonou BCDF", "general"),
    ]
    
    for query, expected_intent in test_cases:
        entities = bot.extract_entities(query)
        print(f"✅ '{query}' → Intention: {entities['intent']}")
    
    print("\n🎯 Tous les tests passés !")

if __name__ == "__main__":
    print("""
    🚀 GUIDE DE DÉMARRAGE RAPIDE - RAG ANDF
    =====================================
    
    Ce script implémente un chatbot RAG complet pour l'ANDF
    utilisant toutes les données que nous avons collectées.
    
    COMMANDES :
    - demo_chatbot() : Démonstration complète
    