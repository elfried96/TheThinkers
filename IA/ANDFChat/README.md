# ANDF Chatbot - Backend FastAPI

Système de chatbot avec RAG (Retrieval-Augmented Generation) pour l'Agence Nationale du Domaine et du Foncier du Bénin.

## 🎯 Fonctionnalités

- **Chatbot intelligent** avec compréhension du contexte ANDF
- **Système RAG** utilisant ChromaDB pour la recherche sémantique
- **API FastAPI** complète avec documentation automatique
- **Support multilingue** (Français, Fon, Yoruba)
- **Base de connaissances complète** sur les procédures foncières béninoises
- **Interface digitale** compatible avec la plateforme e-Notaire 2025

## 📁 Structure du Projet

```
ANDFChat/
├── main.py                 # Serveur FastAPI principal
├── rag_system.py          # Système RAG avec ChromaDB
├── config.py              # Configuration du système
├── test_system.py         # Suite de tests complète
├── requirements.txt       # Dépendances Python
├── quick_start_guide.py   # Guide de démarrage original
├── README.md              # Documentation
└── data/                  # Données de la knowledge base
    ├── andf_knowledge_base.json
    ├── training_qa_dataset.json
    └── sources_metadata.txt
```

## 🚀 Installation et Démarrage

### 1. Installation des dépendances

```bash
# Installation des dépendances Python
pip install -r requirements.txt

# Installation du modèle français spaCy (optionnel)
python -m spacy download fr_core_news_sm
```

### 2. Vérification du système

```bash
python test_system.py --action=check
```

### 3. Test rapide

```bash
python test_system.py --action=quick
```

### 4. Lancement du serveur

```bash
# Développement
python main.py

# Ou avec uvicorn directement
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test complet

```bash
# Avec le serveur lancé dans un autre terminal
python test_system.py --action=full
```

## 📚 API Endpoints

### Endpoints principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page d'accueil API |
| `/health` | GET | Vérification de l'état |
| `/chat` | POST | Interface chatbot principale |
| `/procedures` | GET | Liste des procédures ANDF |
| `/tarifs` | GET | Tarifs des services |
| `/bcdf` | GET | Informations BCDF |
| `/search` | GET | Recherche dans la knowledge base |
| `/stats` | GET | Statistiques du système |

### Documentation interactive

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🤖 Utilisation du Chatbot

### Requête POST /chat

```json
{
  "message": "Comment obtenir un titre foncier ?",
  "session_id": "optional_session_id",
  "context": {
    "commune": "Cotonou",
    "type_bien": "terrain"
  }
}
```

### Réponse

```json
{
  "response": "Pour obtenir un titre foncier au Bénin...",
  "session_id": "generated_or_provided",
  "timestamp": "2025-01-25T10:30:00",
  "confidence": 0.85,
  "sources": [
    {
      "collection": "procedures",
      "type": "procedure",
      "relevance": 0.92
    }
  ],
  "metadata": {
    "intent": "procedure_info",
    "entities": ["titre foncier"]
  }
}
```

## 💡 Exemples de Questions

Le chatbot peut répondre à des questions comme :

- **Procédures** : "Comment obtenir un titre foncier ?"
- **Coûts** : "Combien coûte un certificat d'appartenance ?"
- **Documents** : "Quels documents pour une mutation ?"
- **Localisation** : "Où se trouve le BCDF de Cotonou ?"
- **Services digitaux** : "Comment utiliser e-Notaire ?"
- **Problèmes** : "Que faire en cas de double vente ?"

## 🔧 Configuration

### Variables d'environnement

```bash
# Environnement (development, production, testing)
ENV=development

# Configuration API
API_HOST=0.0.0.0
API_PORT=8000

# Paths personnalisés
DATA_DIR=./data
CHROMA_DB_DIR=./chroma_db
```

### Configuration avancée

Modifiez `config.py` pour personnaliser :
- Modèles d'embeddings
- Seuils de confiance
- Templates de réponse
- Patterns d'intention

## 📊 Données et Knowledge Base

### Sources de données

1. **Code Foncier 2013** - Loi n°2013-01 du 14 août 2013
2. **Réformes 2025** - Digitalisation et plateforme e-Notaire
3. **Procédures ANDF** - Documents officiels
4. **FAQ communautaire** - Questions fréquentes

### Collections ChromaDB

- `procedures` - Procédures foncières
- `tarifs` - Coûts et tarifs
- `legal_info` - Base juridique
- `faq` - Questions-réponses
- `locations` - Informations BCDF
- `digital_services` - Services numériques

## 🧪 Tests

### Suite de tests complète

```bash
# Tests complets (nécessite serveur lancé)
python test_system.py --action=full

# Test rapide du RAG seulement
python test_system.py --action=quick

# Vérification du système
python test_system.py --action=check

# Installation des dépendances
python test_system.py --action=install
```

### Tests inclus

1. **Validation des données** - Structure et contenu JSON
2. **Système RAG** - Initialisation et requêtes
3. **Endpoints API** - Tous les endpoints
4. **Intégration** - Conversation complète

## 🌍 Support Multilingue

### Langues supportées

- **Français** (principal)
- **Fon** (glossaire de base)
- **Yoruba** (glossaire de base)

### Extension linguistique

Pour ajouter une langue :

1. Étendre `LANGUAGE_CONFIG` dans `config.py`
2. Ajouter les traductions dans la knowledge base
3. Configurer le modèle spaCy correspondant

## 🔐 Sécurité et Production

### Configuration CORS

```python
# Development
CORS_ORIGINS = ["*"]

# Production
CORS_ORIGINS = ["https://andf.bj", "https://www.andf.bj"]
```

### Monitoring et Logs

- Logs automatiques dans `andf_chatbot.log`
- Métriques de performance via `/stats`
- Historique de sessions (limité)

## 🚀 Déploiement

### Développement

```bash
python main.py
```

### Production avec Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (à créer)

```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contribution

### Structure de développement

1. **Fork** le projet
2. **Créer** une branche feature
3. **Tester** avec `python test_system.py`
4. **Documenter** les changements
5. **Soumettre** une pull request

### Standards de code

- **PEP 8** pour Python
- **Type hints** obligatoires
- **Docstrings** pour fonctions publiques
- **Tests** pour nouvelles fonctionnalités

## 📞 Support et Contact

- **ANDF** : +229 21 30 10 20
- **Site web** : https://andf.bj
- **E-mail** : contact@andf.bj

## 📄 License

Projet développé pour l'Agence Nationale du Domaine et du Foncier du Bénin.

---

**Développé avec ❤️ pour la modernisation foncière du Bénin** 🇧🇯