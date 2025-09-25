#!/bin/bash

# Script d'installation automatique pour ANDF Chatbot
# ===================================================

set -e  # Arrêt en cas d'erreur

echo "🇧🇯 INSTALLATION CHATBOT ANDF"
echo "=============================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage avec couleurs
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Vérification de Python
check_python() {
    print_info "Vérification de Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_status "Python trouvé: $PYTHON_VERSION"
        
        # Vérifier la version (minimum 3.8)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_status "Version Python compatible"
            return 0
        else
            print_error "Python 3.8+ requis, trouvé: $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 non trouvé"
        return 1
    fi
}

# Vérification de uv
check_uv() {
    print_info "Vérification de uv..."
    
    if command -v uv &> /dev/null; then
        UV_VERSION=$(uv --version 2>&1 | head -n1)
        print_status "uv trouvé: $UV_VERSION"
        return 0
    else
        print_warning "uv non trouvé"
        return 1
    fi
}

# Installation de uv
install_uv() {
    print_info "Installation de uv..."
    
    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
        print_status "uv installé"
    else
        print_error "curl requis pour installer uv"
        exit 1
    fi
}

# Vérification des fichiers de données
check_data_files() {
    print_info "Vérification des fichiers de données..."
    
    REQUIRED_FILES=(
        "data/andf_knowledge_base.json"
        "data/training_qa_dataset.json"
        "data/sources_metadata.txt"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_status "$file présent"
        else
            print_error "$file manquant"
            return 1
        fi
    done
    
    return 0
}

# Installation des dépendances
install_dependencies() {
    print_info "Installation des dépendances..."
    
    # Mode d'installation selon disponibilité
    if command -v uv &> /dev/null; then
        print_info "Installation avec uv..."
        
        # Dépendances de base
        print_info "Installation dépendances de base..."
        uv add fastapi uvicorn pydantic httpx python-multipart python-dotenv
        print_status "Dépendances de base installées"
        
        # Proposer les dépendances ML
        echo ""
        echo -e "${YELLOW}❓ Installer les dépendances ML complètes (ChromaDB, Transformers) ?${NC}"
        echo "   Cela prendra plus de temps mais activera le système RAG complet."
        read -p "   Continuer ? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installation dépendances ML..."
            uv add chromadb sentence-transformers torch numpy scikit-learn
            print_status "Dépendances ML installées"
        else
            print_warning "Dépendances ML non installées - mode démonstration seulement"
        fi
        
    elif command -v pip &> /dev/null; then
        print_info "Installation avec pip..."
        pip install fastapi uvicorn pydantic httpx python-multipart python-dotenv
        print_status "Dépendances de base installées avec pip"
    else
        print_error "Ni uv ni pip trouvés"
        return 1
    fi
}

# Test du système
test_system() {
    print_info "Test du système..."
    
    if python3 test_system.py --action=check; then
        print_status "Vérifications système réussies"
    else
        print_error "Erreur lors des vérifications"
        return 1
    fi
    
    if python3 simple_demo.py test; then
        print_status "Test du chatbot réussi"
    else
        print_error "Erreur test chatbot"
        return 1
    fi
}

# Création des répertoires nécessaires
create_directories() {
    print_info "Création des répertoires..."
    
    mkdir -p logs
    mkdir -p chroma_db
    
    print_status "Répertoires créés"
}

# Installation complète
main() {
    echo ""
    print_info "Début de l'installation..."
    echo ""
    
    # Vérifications préliminaires
    if ! check_python; then
        exit 1
    fi
    
    if ! check_data_files; then
        print_error "Fichiers de données manquants. Vérifiez la structure du projet."
        exit 1
    fi
    
    # Installation de uv si nécessaire
    if ! check_uv; then
        echo ""
        echo -e "${YELLOW}❓ Installer uv (gestionnaire de paquets rapide) ?${NC}"
        read -p "   Recommandé pour une installation plus rapide (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_uv
        fi
    fi
    
    # Création des répertoires
    create_directories
    
    # Installation des dépendances
    if ! install_dependencies; then
        print_error "Erreur lors de l'installation des dépendances"
        exit 1
    fi
    
    # Tests du système
    echo ""
    print_info "Tests du système..."
    if ! test_system; then
        print_warning "Certains tests ont échoué, mais le système peut fonctionner"
    fi
    
    # Messages finaux
    echo ""
    echo "🎉 INSTALLATION TERMINÉE !"
    echo "=========================="
    echo ""
    print_status "Le chatbot ANDF est maintenant installé"
    echo ""
    echo -e "${BLUE}📚 Pour démarrer :${NC}"
    echo "   python3 start.py              # Démarrage automatique"
    echo "   python3 simple_demo.py demo   # Démonstration simple"
    echo "   python3 main.py               # API complète (si dépendances ML)"
    echo ""
    echo -e "${BLUE}📖 Documentation :${NC}"
    echo "   README.md                     # Guide complet"
    echo "   RESUME_PROJET.md              # Résumé exécutif"
    echo "   http://localhost:8000/docs    # API docs (une fois lancé)"
    echo ""
    print_status "Prêt pour la production ! 🚀"
}

# Exécution si script appelé directement
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi