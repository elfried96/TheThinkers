#!/usr/bin/env python3
"""
Script principal amélioré avec preprocessing morphologique
Correction des confusions OCR 0/6, 4/1, 9/0
"""

import sys
import os
import argparse
from pathlib import Path

def main():
    """Point d'entrée principal amélioré"""
    
    parser = argparse.ArgumentParser(description="Pipeline OCR Gemini avec preprocessing morphologique amélioré")
    parser.add_argument("input", help="Fichier image ou dossier d'images")
    parser.add_argument("-o", "--output", required=True, help="Fichier CSV de sortie")
    parser.add_argument("--validate", action="store_true", help="Activer validation géométrique")
    parser.add_argument("--morphological", action="store_true", default=True, help="Activer enhancement morphologique")
    
    args = parser.parse_args()
    
    print("🚀 PIPELINE OCR GEMINI MORPHOLOGIQUE AMÉLIORÉ")
    print("=" * 60)
    
    if args.morphological:
        print("🔧 Enhancement morphologique ACTIVÉ")
        print("  • Correction confusions 0/6, 4/1, 9/0")
        print("  • Débruitage morphologique adaptatif")
        print("  • Sharpening intelligent")
    
    # Importer le module principal existant
    try:
        import main as original_main
        
        # Exécuter avec les mêmes arguments
        sys.argv = [sys.argv[0], args.input, "-o", args.output]
        if args.validate:
            sys.argv.append("--validate")
        
        original_main.main()
        
    except ImportError:
        print("❌ Module main.py original non trouvé")
        print("💡 Exécutez depuis le répertoire contenant main.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
