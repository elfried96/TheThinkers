"""
Backend FastAPI Complet pour ANDF Chatbot
==========================================
Système intelligent avec traitement de réponses et gestion d'erreurs robuste
"""

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any, Union
import json
import logging
import asyncio
import re
import difflib
from datetime import datetime, timedelta
import uuid
import hashlib
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# MODÈLES DE DONNÉES
# =============================================================================

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    language: Optional[str] = Field(default="fr", pattern="^(fr|fon|yoruba)$")
    
    @validator('message')
    def validate_message(cls, v):
        # Nettoyage basique du message
        v = v.strip()
        if not v:
            raise ValueError('Message ne peut pas être vide')
        return v

class EnhancedChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    intent: str
    entities: Dict[str, List[str]]
    suggested_questions: List[str]
    sources: List[Dict[str, Any]]
    corrections_applied: Optional[List[str]] = None
    warning_messages: Optional[List[str]] = None
    follow_up_needed: bool = False
    estimated_processing_time: Optional[str] = None

class SystemStatus(BaseModel):
    status: str
    version: str
    uptime_seconds: int
    total_queries: int
    avg_response_time: float
    knowledge_base_size: int
    last_update: str
    available_services: List[str]

# =============================================================================
# SYSTÈME DE TRAITEMENT INTELLIGENT
# =============================================================================

class IntelligentResponseProcessor:
    """Processeur intelligent pour les réponses ANDF"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.qa_dataset = {}
        self.query_patterns = {}
        self.correction_rules = {}
        self.load_data()
        self.setup_processing_rules()
        
    def load_data(self):
        """Charge toutes les données nécessaires"""
        try:
            # Base de connaissances principale
            with open("./data/andf_knowledge_base.json", "r", encoding="utf-8") as f:
                self.knowledge_base = json.load(f)
            
            # Dataset Q&A
            with open("./data/training_qa_dataset.json", "r", encoding="utf-8") as f:
                self.qa_dataset = json.load(f)
            
            logger.info("✅ Données chargées avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement données: {e}")
            raise e
    
    def setup_processing_rules(self):
        """Configure les règles de traitement intelligent"""
        
        # Patterns de requêtes communes
        self.query_patterns = {
            'cost_inquiry': {
                'patterns': [
                    r'\b(combien|coût|prix|tarif|frais|paye[rz]?)\b',
                    r'\b(ça coûte|coute)\b',
                    r'\b\d+.*f\s*cfa\b'
                ],
                'entities': ['procedures', 'services'],
                'response_template': 'cost_response'
            },
            'procedure_info': {
                'patterns': [
                    r'\b(comment|procédure|étapes|démarche|faire)\b',
                    r'\b(obtenir|avoir|demander)\b',
                    r'\b(processus|méthode)\b'
                ],
                'entities': ['procedures', 'documents'],
                'response_template': 'procedure_response'
            },
            'document_requirements': {
                'patterns': [
                    r'\b(documents?|pièces?|papiers?)\b',
                    r'\b(requis|nécessaires?|fournir|apporter)\b',
                    r'\b(dossier|constitution)\b'
                ],
                'entities': ['procedures', 'document_types'],
                'response_template': 'document_response'
            },
            'location_info': {
                'patterns': [
                    r'\b(où|adresse|localisation|situe)\b',
                    r'\b(bcdf|bureau|office)\b',
                    r'\b(contact|téléphone|appeler)\b'
                ],
                'entities': ['communes', 'departments'],
                'response_template': 'location_response'
            },
            'problem_solving': {
                'patterns': [
                    r'\b(problème|souci|difficultés?)\b',
                    r'\b(conflit|litige|dispute)\b',
                    r'\b(erreur|échec|refus)\b',
                    r'\b(aide|solution|résoudre)\b'
                ],
                'entities': ['problem_types', 'procedures'],
                'response_template': 'problem_response'
            }
        }
        
        # Règles de correction des erreurs utilisateur
        self.correction_rules = {
            'common_misspellings': {
                'titre foncier': ['titre foncer', 'titr foncier', 'titre foncié'],
                'certificat appartenance': ['certificat d\'apartenance', 'certifica appartenance'],
                'bcdf': ['bcfd', 'bcdg', 'dcf'],
                'cotonou': ['cotonou', 'cotonu', 'cotonnu'],
                'mutation': ['mutaton', 'mutatoin', 'mutatino']
            },
            'abbreviations': {
                'tf': 'titre foncier',
                'ca': 'certificat appartenance',
                'mut': 'mutation',
                'hyp': 'hypothèque'
            },
            'synonyms': {
                'titre foncier': ['titre de propriété', 'acte de propriété', 'certificat de propriété'],
                'bcdf': ['bureau foncier', 'service foncier', 'office foncier'],
                'procédure': ['démarche', 'processus', 'méthode']
            }
        }

class ANDFChatbotEngine:
    """Moteur principal du chatbot ANDF avec traitement intelligent"""
    
    def __init__(self):
        self.processor = IntelligentResponseProcessor()
        self.session_store = {}
        self.stats = {
            'total_queries': 0,
            'successful_responses': 0,
            'error_corrections': 0,
            'average_confidence': 0.0,
            'startup_time': datetime.now(),
            'response_times': []
        }
        self.gemini_enhancer = None
        self.setup_gemini()

    def setup_gemini(self):
        """Initialise l'enhancer Gemini"""
        try:
            import sys
            import os
            # Ajout du dossier courant au path Python
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from enhanced_gemini_enhancer import EnhancedGeminiAssistant
            self.gemini_enhancer = EnhancedGeminiAssistant()
            logger.info("✅ Gemini enhancer initialisé avec succès")
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'initialiser Gemini: {e}")
            self.gemini_enhancer = None

    def correct_user_input(self, query: str) -> tuple[str, List[str]]:
        """Corrige les erreurs communes dans la requête utilisateur"""
        corrections_applied = []
        corrected_query = query.lower()
        
        # Correction des fautes de frappe
        for correct_term, misspellings in self.processor.correction_rules['common_misspellings'].items():
            for misspelling in misspellings:
                if misspelling in corrected_query:
                    corrected_query = corrected_query.replace(misspelling, correct_term)
                    corrections_applied.append(f"Corrigé '{misspelling}' → '{correct_term}'")
        
        # Expansion des abréviations
        for abbr, full_term in self.processor.correction_rules['abbreviations'].items():
            pattern = r'\b' + re.escape(abbr) + r'\b'
            if re.search(pattern, corrected_query, re.IGNORECASE):
                corrected_query = re.sub(pattern, full_term, corrected_query, flags=re.IGNORECASE)
                corrections_applied.append(f"Étendu '{abbr}' → '{full_term}'")
        
        # Gestion des synonymes
        for main_term, synonyms in self.processor.correction_rules['synonyms'].items():
            for synonym in synonyms:
                if synonym in corrected_query:
                    corrected_query = corrected_query.replace(synonym, main_term)
                    corrections_applied.append(f"Normalisé '{synonym}' → '{main_term}'")
        
        return corrected_query, corrections_applied
    
    def analyze_intent_and_entities(self, query: str) -> tuple[str, Dict[str, List[str]], float]:
        """Analyse avancée de l'intention et extraction d'entités"""
        
        intent_scores = {}
        all_entities = {
            'procedures': [],
            'communes': [],
            'documents': [],
            'services': [],
            'amounts': []
        }
        
        # Analyse des intentions
        for intent_name, intent_config in self.processor.query_patterns.items():
            score = 0
            for pattern in intent_config['patterns']:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            intent_scores[intent_name] = score
        
        # Intention dominante
        best_intent = max(intent_scores, key=intent_scores.get) if max(intent_scores.values()) > 0 else 'general'
        confidence = min(max(intent_scores.values()) / 3, 1.0)  # Normalisation
        
        # Extraction d'entités
        # Procédures
        procedures = ['titre foncier', 'certificat d\'appartenance', 'mutation', 'morcellement', 'hypothèque']
        all_entities['procedures'] = [proc for proc in procedures if proc in query.lower()]
        
        # Communes
        communes = ['cotonou', 'porto-novo', 'parakou', 'abomey-calavi', 'allada', 'ouidah', 'lokossa', 'natitingou']
        all_entities['communes'] = [commune for commune in communes if commune in query.lower()]
        
        # Documents
        documents = ['cni', 'carte identité', 'plan topographique', 'attestation', 'certificat']
        all_entities['documents'] = [doc for doc in documents if doc in query.lower()]
        
        # Montants (extraction de nombres)
        amounts = re.findall(r'\b\d+(?:\s*\d+)*(?:\s*f\s*cfa|fcfa|francs?)?\b', query, re.IGNORECASE)
        all_entities['amounts'] = amounts
        
        return best_intent, all_entities, confidence
    
    def search_knowledge_base(self, query: str, intent: str) -> List[Dict[str, Any]]:
        """Recherche intelligente dans la base de connaissances"""
        results = []
        
        # Recherche dans le dataset Q&A
        qa_pairs = self.processor.qa_dataset.get('training_dataset', {}).get('qa_pairs', [])
        
        for qa in qa_pairs:
            # Correspondance basique par mots-clés
            query_words = set(query.lower().split())
            question_words = set(qa['question'].lower().split())
            answer_words = set(qa['answer'].lower().split())
            
            # Score de similarité
            question_similarity = len(query_words & question_words) / max(len(query_words), len(question_words))
            
            if question_similarity > 0.3:  # Seuil de pertinence
                results.append({
                    'source': 'qa_dataset',
                    'content': qa['answer'],
                    'question': qa['question'],
                    'category': qa.get('category', 'general'),
                    'similarity': question_similarity,
                    'metadata': {
                        'intent': qa.get('intent', 'general'),
                        'id': qa.get('id', '')
                    }
                })
        
        # Recherche dans la knowledge base principale
        kb_sections = ['procedures_principales', 'tarifs_detailles', 'base_juridique']
        
        for section_name in kb_sections:
            section_data = self.processor.knowledge_base.get(section_name, {})
            
            for key, value in section_data.items():
                if isinstance(value, dict):
                    # Création d'un texte de recherche
                    search_text = f"{key} {json.dumps(value, ensure_ascii=False)}"
                    
                    # Score de pertinence simple
                    query_words = set(query.lower().split())
                    content_words = set(search_text.lower().split())
                    similarity = len(query_words & content_words) / max(len(query_words), len(content_words))
                    
                    if similarity > 0.2:
                        results.append({
                            'source': 'knowledge_base',
                            'section': section_name,
                            'key': key,
                            'content': value,
                            'similarity': similarity,
                            'metadata': {
                                'type': section_name,
                                'key': key
                            }
                        })
        
        # Tri par pertinence
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:5]  # Top 5 résultats
    
    def generate_enhanced_response(self, query: str, intent: str, entities: Dict, search_results: List[Dict], corrections: List[str]) -> Dict[str, Any]:
        """Génère une réponse enrichie et structurée"""
        
        response_data = {
            'response': '',
            'confidence_score': 0.5,
            'suggested_questions': [],
            'sources': search_results[:3],
            'corrections_applied': corrections,
            'warning_messages': [],
            'follow_up_needed': False,
            'estimated_processing_time': None
        }
        
        if not search_results:
            response_data.update(self._generate_fallback_response(intent, entities))
            return response_data
        
        best_result = search_results[0]
        
        # Génération selon le type d'intention
        if intent == 'cost_inquiry':
            response_data.update(self._generate_cost_response(query, entities, search_results))
        elif intent == 'procedure_info':
            response_data.update(self._generate_procedure_response(query, entities, search_results))
        elif intent == 'document_requirements':
            response_data.update(self._generate_document_response(query, entities, search_results))
        elif intent == 'location_info':
            response_data.update(self._generate_location_response(query, entities, search_results))
        elif intent == 'problem_solving':
            response_data.update(self._generate_problem_response(query, entities, search_results))
        else:
            response_data.update(self._generate_general_response(query, search_results))
        
        # Ajout d'informations contextuelles
        self._add_contextual_information(response_data, entities, intent)
        
        return response_data
    
    def _generate_cost_response(self, query: str, entities: Dict, results: List[Dict]) -> Dict[str, Any]:
        """Génère une réponse spécialisée pour les coûts"""
        
        tarifs_base = {
            'titre foncier': 100000,
            'certificat appartenance': 50000,
            'mutation': '0.3% de la valeur',
            'morcellement': '0.3% + 102,500 F CFA',
            'hypothèque': 0,
            'duplicata': 25000
        };

        response = "💰 **Informations Tarifaires ANDF**\n\n";

        # Recherche de tarifs spécifiques
        found_procedures = entities.get('procedures', []);
        if found_procedures:
            for procedure in found_procedures:
                if procedure in tarifs_base:
                    cost = tarifs_base[procedure];
                    response += f"**{procedure.title()} :** {cost:,} F CFA\n" if isinstance(cost, int) else f"**{procedure.title()} :** {cost}\n";

                    # Ajout d'informations complémentaires
                    if procedure == 'titre foncier':
                        response += "  - Durée : 120 jours maximum\n";
                        response += "  - Frais de bornage en sus (variable)\n";
                    elif procedure == 'certificat appartenance':
                        response += "  - Validité : 1 an non renouvelable\n";
                        response += "  - Obligatoire avant toute vente\n";

                response += "\n";
        else:
            # Affichage des tarifs généraux
            response += "**Tarifs principaux :**\n";
            for service, prix in tarifs_base.items():
                if isinstance(prix, int) and prix > 0:
                    response += f"- {service.title()} : {prix:,} F CFA\n";
                elif isinstance(prix, str):
                    response += f"- {service.title()} : {prix}\n";

        response += "\n📞 **Contact :** +229 21 30 10 20";
        response += "\n🌐 **Site :** https://andf.bj";

        # Suggestions de questions
        suggestions = [
            "Quels sont les frais de bornage ?",
            "Comment payer les frais ANDF ?",
            "Y a-t-il des réductions de tarifs ?"
        ]
        
        return {
            'response': response,
            'confidence_score': 0.85,
            'suggested_questions': suggestions,
            'estimated_processing_time': "Immédiat"
        }
    
    def _generate_procedure_response(self, query: str, entities: Dict, results: List[Dict]) -> Dict[str, Any]:
        """Génère une réponse pour les procédures"""
        
        response = "📋 **Procédure ANDF**\n\n";

        # Recherche dans les résultats pour des procédures spécifiques
        procedure_found = False;
        for result in results:
            if result.get('source') == 'qa_dataset' and 'procédure' in result.get('question', '').lower():
                response += result['content'];
                procedure_found = True;
                break;

        if not procedure_found:
            # Réponse générique basée sur les entités
            procedures = entities.get('procedures', []);
            if 'titre foncier' in procedures:
                response += """**Obtention d'un Titre Foncier :**

**Étapes principales :**
1. **Préparation du dossier** (documents requis)
2. **Dépôt au BCDF** de votre commune
3. **Enquête publique** (45 jours)
4. **Bornage contradictoire** avec géomètre
5. **Confirmation et délivrance** du titre

**Durée :** 120 jours maximum
**Coût :** 100,000 F CFA + frais de bornage""";

            else:
                response += """**Services ANDF principaux :**
- Confirmation de droits fonciers (Titre foncier)
- Certificats d'appartenance
- Mutations de titre foncier
- Morcelements et lotissements""";

        response += "\n\n**🏢 Service compétent :** BCDF de votre commune";

        suggestions = [
            "Quels documents pour un titre foncier ?",
            "Combien de temps prend la procédure ?",
            "Où déposer mon dossier ?"
        ]
        
        return {
            'response': response,
            'confidence_score': 0.80,
            'suggested_questions': suggestions,
            'follow_up_needed': True,
            'estimated_processing_time': "Variable selon la procédure"
        }
    
    def _generate_document_response(self, query: str, entities: Dict, results: List[Dict]) -> Dict[str, Any]:
        """Génère une réponse pour les documents requis"""
        
        response = "📄 **Documents Requis ANDF**\n\n";

        # Documents selon la procédure
        procedures = entities.get('procedures', []);

        if 'titre foncier' in procedures:
            response += """**Pour un Titre Foncier :**

**Documents obligatoires :**
1. **Identité :** CNI ou CIP + Extrait de naissance
2. **Présomption de propriété :** 
   - Attestation de détention coutumière, OU
   - Attestation de recasement, OU
   - Avis d'imposition (3 dernières années), OU
   - Certificat administratif
3. **Technique :** Plan topographique géoréférencé
4. **Administratif :** Fiche de demande signée
5. **Paiement :** Reçu des frais (100,000 F CFA)

**⚠️ Important :** Tous les documents doivent être légalisés""";

        elif 'certificat appartenance' in procedures:
            response += """**Pour un Certificat d'Appartenance :**

**Documents requis :**
1. Pièce d'identité (CNI/CIP)
2. Document de présomption de propriété
3. Plan topographique sommaire
4. Fiche de demande
5. Reçu de paiement (50,000 F CFA)""";

        else:
            response += """**Documents généralement requis :**

**Pour toute procédure ANDF :**
✓ Pièce d'identité valide
✓ Documents justificatifs de propriété
✓ Plan topographique (selon procédure)
✓ Fiche de demande complétée
✓ Justificatif de paiement des frais

**💡 Conseil :** Contactez votre BCDF pour la liste exacte""";

        # Informations complémentaires
        response += "\n\n**📋 Recommandations :**";
        response += "\n- Préparez des copies légalisées";
        response += "\n- Vérifiez la validité de vos documents";
        response += "\n- Constituez votre dossier avant le dépôt";

        suggestions = [
            "Où légaliser mes documents ?",
            "Combien coûte la légalisation ?",
            "Validité des documents requis ?"
        ]
        
        return {
            'response': response,
            'confidence_score': 0.90,
            'suggested_questions': suggestions,
            'warning_messages': ["Vérifiez toujours les exigences avec votre BCDF local"],
            'estimated_processing_time': "Information immédiate"
        }
    
    def _generate_location_response(self, query: str, entities: Dict, results: List[Dict]) -> Dict[str, Any]:
        """Génère une réponse pour les informations de localisation"""
        
        response = "📍 **Localisation BCDF**\n\n";

        # BCDF principaux avec informations complètes
        bcdf_info = {
            'cotonou': {
                'adresse': 'Quartier Gbégamey, Cotonou',
                'telephone': '+229 21 30 10 20',
                'email': 'bcdf.cotonou@andf.bj',
                'departement': 'Littoral',
                'horaires': 'Lundi-Vendredi : 7h30-17h30'
            },
            'porto-novo': {
                'adresse': 'Centre-ville, Porto-Novo',
                'telephone': '+229 20 21 22 23',
                'email': 'bcdf.portonovo@andf.bj',
                'departement': 'Ouémé',
                'horaires': 'Lundi-Vendredi : 8h00-17h00'
            },
            'parakou': {
                'adresse': 'Centre administratif, Parakou',
                'telephone': '+229 23 61 03 04',
                'email': 'bcdf.parakou@andf.bj',
                'departement': 'Borgou',
                'horaires': 'Lundi-Vendredi : 7h30-17h30'
            }
        };

        communes = entities.get('communes', []);
        found_commune = False;

        for commune in communes:
            if commune in bcdf_info:
                info = bcdf_info[commune];
                response += f"**BCDF de {commune.title()}**\n";
                response += f"📍 **Adresse :** {info['adresse']}\n";
                response += f"📞 **Téléphone :** {info['telephone']}\n";
                response += f"📧 **Email :** {info['email']}\n";
                response += f"🗺️ **Département :** {info['departement']}\n";
                response += f"⏰ **Horaires :** {info['horaires']}\n\n";
                found_commune = True;
                break;

        if not found_commune:
            response += "**BCDF Principaux :**\n\n";
            for commune, info in bcdf_info.items():
                response += f"**{commune.title()} :** {info['telephone']}\n";

            response += "\n**🌐 Autres BCDF :**\n";
            response += "Pour les autres communes, contactez :\n";
            response += "📞 Standard ANDF : +229 21 30 10 20";

        response += "\n\n**🚗 Conseils pratiques :**";
        response += "\n- Appelez avant votre déplacement";
        response += "\n- Préparez votre dossier complet";
        response += "\n- Évitez les heures de pointe (12h-14h)";

        suggestions = [
            "Horaires d'ouverture des BCDF ?",
            "Services disponibles dans mon BCDF ?",
            "Comment prendre rendez-vous ?"
        ]
        
        warning_messages = [];
        if not found_commune:
            warning_messages.append("Informations partielles - contactez le standard pour votre commune");

        return {
            'response': response,
            'confidence_score': 0.85 if found_commune else 0.60,
            'suggested_questions': suggestions,
            'warning_messages': warning_messages,
            'estimated_processing_time': "Information immédiate"
        }
    
    def _generate_problem_response(self, query: str, entities: Dict, results: List[Dict]) -> Dict[str, Any]:
        """Génère une réponse pour la résolution de problèmes"""
        
        response = "🛠️ **Résolution de Problèmes ANDF**\n\n";

        # Analyse du type de problème
        if any(word in query.lower() for word in ['perdu', 'perte', 'perdue']):
            response += """**Perte de Titre Foncier :**

**Procédure de duplicata :**
1. **Déclaration de perte** au commissariat
2. **Publication** dans un journal d'annonces légales
3. **Demande de duplicata** au BCDF compétent
4. **Paiement des frais** (25,000 F CFA)
5. **Délivrance** du nouveau titre (30 jours)

**Documents requis :**
- Déclaration de perte
- Preuve de publication
- CNI du propriétaire
- Tout document disponible (photocopies)""";

        elif any(word in query.lower() for word in ['conflit', 'litige', 'voisin', 'dispute']):
            response += """**Conflit de Limites/Voisinage :**

**Étapes de résolution :**
1. **Dialogue amiable** avec le voisin
2. **Médiation** par le chef de quartier/village
3. **Bornage contradictoire** par géomètre agréé
4. **Recours judiciaire** si nécessaire

**Coûts :**
- Médiation : Gratuite
- Bornage contradictoire : Variable (partagé)
- Procédure judiciaire : Frais de justice

**💡 Conseil :** Privilégiez toujours la solution amiable""";

        elif any(word in query.lower() for word in ['refus', 'rejet', 'échec']):
            response += """**Dossier Refusé/Rejeté :**

**Actions à entreprendre :**
1. **Demander** les motifs détaillés du refus
2. **Corriger** les éléments défaillants
3. **Compléter** les documents manquants
4. **Redéposer** le dossier corrigé
5. **Recours** si refus injustifié

**Voies de recours :**
- Recours gracieux (2 mois)
- Recours hiérarchique
- Recours contentieux (tribunal)""";

        else:
            response += """**Assistance Générale :**

**Pour tout problème foncier :**
📞 **Hotline ANDF :** +229 21 30 10 20
📧 **Email :** assistance@andf.bj
🏢 **BCDF local :** Votre premier interlocuteur

**Services d'aide disponibles :**
- Orientation et conseil
- Vérification de dossier
- Suivi de procédure
- Médiation en cas de conflit

**⏰ Disponibilité :** Lundi-Vendredi, 8h-17h""";

        response += "\n\n**🚨 Urgences :**";
        response += "\nEn cas d'urgence foncière (expulsion, etc.) :";
        response += "\n📞 Contactez immédiatement votre BCDF";

        suggestions = [
            "Comment faire un recours ?",
            "Procédure de médiation foncière ?",
            "Coût d'un bornage contradictoire ?"
        ]
        
        return {
            'response': response,
            'confidence_score': 0.75,
            'suggested_questions': suggestions,
            'follow_up_needed': True,
            'warning_messages': ["Pour les urgences, contactez immédiatement votre BCDF"],
            'estimated_processing_time': "Variable selon le problème"
        }
    
    def _generate_general_response(self, query: str, results: List[Dict]) -> Dict[str, Any]:
        """Génère une réponse générale"""
        
        if results and results[0].get('source') == 'qa_dataset':
            # Utilise la meilleure réponse du dataset
            best_result = results[0]
            response = best_result['content']
            confidence = best_result['similarity']
        else:
            response = """Bonjour ! Je suis l'assistant virtuel de l'ANDF.

**Je peux vous aider avec :**
- 📋 Les procédures foncières
- 💰 Les tarifs et coûts
- 📍 La localisation des BCDF
- 📄 Les documents requis
- 🛠️ La résolution de problèmes

**Questions populaires :**
- Comment obtenir un titre foncier ?
- Combien coûte un certificat d'appartenance ?
- Où se trouve mon BCDF ?

📞 **Contact direct :** +229 21 30 10 20"""
            confidence = 0.5
        
        suggestions = [
            "Comment obtenir un titre foncier ?",
            "Combien coûte un certificat d'appartenance ?",
            "Où se trouve le BCDF de ma commune ?",
            "Quels documents pour une mutation ?"
        ]
        
        return {
            'response': response,
            'confidence_score': confidence,
            'suggested_questions': suggestions,
            'estimated_processing_time': "Information immédiate"
        }
    
    def _generate_fallback_response(self, intent: str, entities: Dict) -> Dict[str, Any]:
        """Génère une réponse de fallback adaptée à l'intention"""
        
        fallback_responses = {
            'cost_inquiry': """💰 **Tarifs ANDF principaux :**
- Titre foncier : 100,000 F CFA
- Certificat d'appartenance : 50,000 F CFA
- Mutations : 0,3% de la valeur

📞 **Pour plus de détails :** +229 21 30 10 20""",
            
            'procedure_info': """📋 **Procédures ANDF :**
- Confirmation de droits fonciers
- Certificats d'appartenance
- Mutations de titre foncier

🏢 **Contactez votre BCDF** pour les détails.""",
            
            'general': """Je n'ai pas trouvé d'information spécifique sur votre question.

📞 **Contactez l'ANDF :**
- Standard : +229 21 30 10 20
- Site web : https://andf.bj
- BCDF local : Selon votre commune

Je peux vous aider avec les procédures, tarifs et contacts ANDF."""
        };

        response = fallback_responses.get(intent, fallback_responses['general']);

        return {
            'response': response,
            'confidence_score': 0.3,
            'suggested_questions': [
                "Comment obtenir un titre foncier ?",
                "Combien coûte un certificat d'appartenance ?",
                "Où se trouve mon BCDF ?"
            ],
            'warning_messages': ["Information limitée - contactez l'ANDF pour plus de détails"],
            'estimated_processing_time': "Information immédiate"
        }
    
    def _add_contextual_information(self, response_data: Dict, entities: Dict, intent: str):
        """Ajoute des informations contextuelles à la réponse"""
        
        # Ajout d'alertes selon le contexte
        if intent == 'cost_inquiry' and any(proc in entities.get('procedures', []) for proc in ['titre foncier']):
            if not response_data.get('warning_messages'):
                response_data['warning_messages'] = []
            response_data['warning_messages'].append("Les frais de bornage contradictoire sont en sus et varient selon le géomètre")
        
        # Suggestion de suivi
        if intent in ['procedure_info', 'document_requirements']:
            response_data['follow_up_needed'] = True
        
        # Estimation du temps de traitement
        if not response_data.get('estimated_processing_time'):
            time_estimates = {
                'cost_inquiry': "Immédiat",
                'location_info': "Immédiat", 
                'procedure_info': "Variable selon la procédure",
                'document_requirements': "Information immédiate",
                'problem_solving': "Variable selon le problème"
            }
            response_data['estimated_processing_time'] = time_estimates.get(intent, "Variable")
    
    async def process_chat_message(self, message: str, session_id: Optional[str] = None, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Traite un message de chat avec toute l'intelligence du système"""
        
        start_time = datetime.now()
        
        # Génération de l'ID de session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Correction des erreurs utilisateur
        corrected_query, corrections = self.correct_user_input(message)
        
        # Analyse de l'intention et des entités
        intent, entities, base_confidence = self.analyze_intent_and_entities(corrected_query)
        
        # Recherche dans la base de connaissances
        search_results = self.search_knowledge_base(corrected_query, intent)
        
        # Génération de la réponse enrichie
        response_data = self.generate_enhanced_response(
            corrected_query, intent, entities, search_results, corrections
        )
        
        # Amélioration avec Gemini si disponible
        if self.gemini_enhancer:
            try:
                context = {
                    'intent': intent,
                    'question': message,
                    'user_context': user_context or {}
                }
                
                # Utilisation du nouvel enhancer conversationnel
                enhanced_response = await self.gemini_enhancer.enhance_response_conversational(
                    response_data['response'],
                    context,
                    session_id
                )
                
                # Génération de questions de suivi
                follow_up_questions = await self.gemini_enhancer.generate_follow_up_questions(
                    {'intent': intent, 'entities': entities},
                    session_id
                )
                
                # Mise à jour de la réponse avec les améliorations Gemini
                response_data['response'] = enhanced_response
                response_data['suggested_questions'] = follow_up_questions or response_data.get('suggested_questions', [])
                response_data['confidence_score'] = min(response_data['confidence_score'] + 0.1, 1.0)  # Bonus confiance
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur amélioration Gemini: {e}")
        
        # Calcul du temps de traitement
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Mise à jour des statistiques
        self.stats['total_queries'] += 1
        self.stats['response_times'].append(processing_time)
        if len(self.stats['response_times']) > 100:
            self.stats['response_times'] = self.stats['response_times'][-100:]  # Garde les 100 derniers
        self.stats['average_response_time'] = sum(self.stats['response_times']) / len(self.stats['response_times'])
        
        if response_data['confidence_score'] > 0.5:
            self.stats['successful_responses'] += 1
        
        if corrections:
            self.stats['error_corrections'] += 1
        
        # Construction de la réponse finale
        final_response = EnhancedChatResponse(
            response=response_data['response'],
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            confidence_score=response_data['confidence_score'],
            intent=intent,
            entities=entities,
            suggested_questions=response_data.get('suggested_questions', []),
            sources=response_data.get('sources', []),
            corrections_applied=response_data.get('corrections_applied', []),
            warning_messages=response_data.get('warning_messages', []),
            follow_up_needed=response_data.get('follow_up_needed', False),
            estimated_processing_time=response_data.get('estimated_processing_time')
        )
        
        # Sauvegarde de la session
        if session_id not in self.session_store:
            self.session_store[session_id] = []
        
        self.session_store[session_id].append({
            'timestamp': datetime.now().isoformat(),
            'original_query': message,
            'corrected_query': corrected_query,
            'intent': intent,
            'confidence': response_data['confidence_score'],
            'processing_time': processing_time
        })
        
        # Garde seulement les 20 dernières interactions par session
        if len(self.session_store[session_id]) > 20:
            self.session_store[session_id] = self.session_store[session_id][-20:]
        
        return final_response.dict()

# =============================================================================
# APPLICATION FASTAPI
# =============================================================================

# Initialisation de l'application
app = FastAPI(
    title="ANDF Chatbot Backend Intelligent",
    description="Backend FastAPI complet avec traitement intelligent des requêtes et gestion d'erreurs robuste",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer selon l'environnement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instance globale du chatbot
chatbot_engine: Optional[ANDFChatbotEngine] = None

# =============================================================================
# ÉVÉNEMENTS DE CYCLE DE VIE
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    global chatbot_engine
    try:
        logger.info("🚀 Initialisation du backend ANDF intelligent...")
        chatbot_engine = ANDFChatbotEngine()
        logger.info("✅ Backend ANDF prêt")
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        raise e

@app.on_event("shutdown") 
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    global chatbot_engine
    if chatbot_engine:
        # Sauvegarde des stats si nécessaire
        logger.info(f"📊 Stats finales: {chatbot_engine.stats['total_queries']} requêtes traitées")
    logger.info("👋 Arrêt du backend ANDF")

# =============================================================================
# DÉPENDANCES
# =============================================================================

async def get_chatbot_engine():
    """Dépendance pour récupérer le moteur du chatbot"""
    if chatbot_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Service temporairement indisponible - moteur du chatbot non initialisé"
        )
    return chatbot_engine

# =============================================================================
# GESTIONNAIRES D'ERREURS
# =============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"Erreur de validation: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "error": "Erreur de validation",
            "message": str(exc),
            "suggestion": "Vérifiez le format de votre requête",
            "contact": "+229 21 30 10 20"
        }
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint non trouvé",
            "message": f"L'URL {request.url.path} n'existe pas",
            "documentation": "/docs",
            "endpoints_disponibles": ["/chat", "/chat/stream", "/health", "/chat/feedback"]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Erreur interne: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "message": "Une erreur s'est produite lors du traitement",
            "action": "Veuillez réessayer ou contacter l'ANDF",
            "contact": "+229 21 30 10 20",
            "timestamp": datetime.now().isoformat()
        }
    )

# =============================================================================
# ENDPOINTS PRINCIPAUX
# =============================================================================

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Backend ANDF Chatbot Intelligent",
        "version": "2.0.0",
        "description": "Système avancé avec traitement intelligent et gestion d'erreurs",
        "features": [
            "Traitement intelligent des requêtes",
            "Correction automatique des erreurs",
            "Analyse d'intention avancée",
            "Réponses enrichies et structurées",
            "Gestion robuste des erreurs"
        ],
        "documentation": "/docs",
        "endpoints": {
            "chat": "/chat",
            "chat_stream": "/chat/stream",
            "health": "/health",
            "feedback": "/chat/feedback"
        }
    }

@app.get("/health", response_model=SystemStatus)
async def health_check(engine: ANDFChatbotEngine = Depends(get_chatbot_engine)):
    """Vérification complète de l'état du système"""
    
    uptime = (datetime.now() - engine.stats['startup_time']).total_seconds()
    
    return SystemStatus(
        status="healthy" if engine else "degraded",
        version="2.0.0",
        uptime_seconds=int(uptime),
        total_queries=engine.stats['total_queries'],
        avg_response_time=engine.stats.get('average_response_time', 0.0),
        knowledge_base_size=len(engine.processor.knowledge_base),
        last_update=datetime.now().isoformat(),
        available_services=[
            "Chat intelligent",
            "Correction d'erreurs",
            "Analyse d'intention", 
            "Recherche sémantique",
            "Réponses enrichies"
        ]
    )

@app.post("/chat", response_model=EnhancedChatResponse)
async def chat_endpoint(
    request: ChatMessage,
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Endpoint principal pour les conversations intelligentes
    
    Fonctionnalités avancées :
    - Correction automatique des fautes de frappe
    - Analyse d'intention et extraction d'entités
    - Recherche sémantique dans la base de connaissances
    - Réponses enrichies et structurées avec Gemini
    - Suggestions de questions de suivi personnalisées
    - Gestion robuste des erreurs
    """
    try:
        logger.info(f"🤖 Nouvelle requête: {request.message[:50]}...")
        
        result = await engine.process_chat_message(
            message=request.message,
            session_id=request.session_id,
            user_context=request.user_context
        )
        
        logger.info(f"✅ Réponse générée (confiance: {result['confidence_score']:.2f})")
        
        return EnhancedChatResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Requête invalide: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Erreur traitement chat: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du traitement de la conversation")

@app.post("/chat/stream")
async def chat_streaming_endpoint(
    request: ChatMessage,
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Endpoint de conversation en streaming pour une expérience plus fluide
    
    Retourne la réponse en temps réel, mot par mot, pour une meilleure UX
    """
    async def generate_response():
        try:
            logger.info(f"🌊 Stream requête: {request.message[:50]}...")
            
            if engine.gemini_enhancer:
                # Utilisation du streaming Gemini
                context = {
                    'intent': 'general',
                    'question': request.message,
                    'user_context': request.user_context or {}
                }
                
                async for chunk in engine.gemini_enhancer.generate_streaming_response(
                    request.message, 
                    context, 
                    request.session_id
                ):
                    yield f"data: {json.dumps({'chunk': chunk, 'type': 'content'})}\n\n"
                
                # Génération des questions de suivi à la fin
                follow_up = await engine.gemini_enhancer.generate_follow_up_questions(
                    context, request.session_id
                )
                
                yield f"data: {json.dumps({'suggestions': follow_up, 'type': 'suggestions'})}\n\n"
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
            else:
                # Fallback si Gemini n'est pas disponible
                result = await engine.process_chat_message(
                    message=request.message,
                    session_id=request.session_id,
                    user_context=request.user_context
                )
                yield f"data: {json.dumps({'chunk': result['response'], 'type': 'content'})}\n\n"
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
        except Exception as e:
            logger.error(f"❌ Erreur streaming: {e}")
            error_msg = "Désolé, je rencontre des difficultés techniques. Contactez l'ANDF au +229 21 30 10 20."
            yield f"data: {json.dumps({'chunk': error_msg, 'type': 'error'})}\n\n"
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.get("/chat/session/{session_id}/stats")
async def get_session_stats(
    session_id: str,
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Récupère les statistiques d'une session de conversation
    """
    try:
        if engine.gemini_enhancer:
            stats = engine.gemini_enhancer.get_conversation_stats(session_id)
        else:
            stats = {"total_exchanges": 0, "session_start": None}
        
        # Ajout des stats du moteur principal
        session_data = engine.session_store.get(session_id, [])
        stats.update({
            "backend_exchanges": len(session_data),
            "last_backend_interaction": session_data[-1]["timestamp"] if session_data else None,
            "average_confidence": sum(item["confidence"] for item in session_data) / len(session_data) if session_data else 0.0,
            "intents_used": list(set(item["intent"] for item in session_data)) if session_data else []
        })
        
        return {
            "session_id": session_id,
            "statistics": stats,
            "status": "active" if session_id in engine.session_store else "inactive"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur stats session: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques")

@app.post("/chat/feedback")
async def submit_feedback(
    feedback_data: Dict[str, Any],
    engine: ANDFChatbotEngine = Depends(get_chatbot_engine)
):
    """
    Endpoint pour recevoir les retours utilisateur et améliorer le service
    """
    try:
        session_id = feedback_data.get("session_id")
        rating = feedback_data.get("rating")  # 1-5
        comment = feedback_data.get("comment", "")
        
        # Log du feedback pour analyse
        logger.info(f"📝 Feedback reçu - Session: {session_id}, Note: {rating}, Commentaire: {comment[:50]}...")
        
        # Ici, vous pourriez sauvegarder en base de données
        feedback_entry = {
            "session_id": session_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "message": "Merci pour votre retour ! Il nous aide à améliorer nos services.",
            "feedback_id": str(uuid.uuid4()),
            "status": "received"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur feedback: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement du feedback")
