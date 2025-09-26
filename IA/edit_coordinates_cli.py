#!/usr/bin/env python3
"""
Éditeur interactif de coordonnées - Version ligne de commande
Alternative au notebook Jupyter pour modifier submissions_TheThinkers.csv
"""

import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import shutil
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class CoordinateEditor:
    def __init__(self, csv_file='submissions_TheThinkers.csv'):
        self.csv_file = csv_file
        self.df = None
        self.analysis_df = None
        self.load_data()
    
    def load_data(self):
        """Charge le fichier CSV"""
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"✅ Fichier chargé: {len(self.df)} lignes")
            print(f"📋 Colonnes: {list(self.df.columns)}")
        except FileNotFoundError:
            print(f"❌ Fichier {self.csv_file} introuvable")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            sys.exit(1)
    
    def parse_coordinates(self, coord_string: str) -> List[Dict]:
        """Parse une chaîne de coordonnées JSON"""
        if pd.isna(coord_string) or coord_string == '':
            return []
        
        try:
            cleaned = coord_string.replace('""', '"')
            coords = json.loads(cleaned)
            return coords if isinstance(coords, list) else []
        except:
            return []
    
    def validate_coordinate(self, x: float, y: float) -> Tuple[bool, str]:
        """Valide une coordonnée UTM"""
        issues = []
        
        if not (350000 <= x <= 550000):
            issues.append(f"X={x} hors plage normale (350000-550000)")
        
        if not (650000 <= y <= 850000):
            issues.append(f"Y={y} hors plage normale (650000-850000)")
        
        if x == 0 or y == 0:
            issues.append("Coordonnée nulle détectée")
        
        if len(str(int(x))) < 6 or len(str(int(y))) < 6:
            issues.append("Coordonnée trop courte")
        
        return len(issues) == 0, "; ".join(issues)
    
    def analyze_coordinates(self) -> pd.DataFrame:
        """Analyse toutes les coordonnées du DataFrame"""
        analysis = []
        
        for idx, row in self.df.iterrows():
            coords = self.parse_coordinates(row['Coordonnées'])
            
            if not coords:
                analysis.append({
                    'Index': idx,
                    'Nom_du_levé': row['Nom_du_levé'],
                    'Nb_coordonnées': 0,
                    'Coordonnées_valides': False,
                    'Problèmes': 'Aucune coordonnée trouvée'
                })
                continue
            
            all_valid = True
            all_issues = []
            
            for i, coord in enumerate(coords):
                x = coord.get('x', 0)
                y = coord.get('y', 0)
                valid, issues = self.validate_coordinate(x, y)
                
                if not valid:
                    all_valid = False
                    all_issues.append(f"Coord {i+1}: {issues}")
            
            analysis.append({
                'Index': idx,
                'Nom_du_levé': row['Nom_du_levé'],
                'Nb_coordonnées': len(coords),
                'Coordonnées_valides': all_valid,
                'Problèmes': "; ".join(all_issues) if all_issues else 'OK'
            })
        
        self.analysis_df = pd.DataFrame(analysis)
        return self.analysis_df
    
    def show_analysis(self):
        """Affiche l'analyse des coordonnées"""
        if self.analysis_df is None:
            self.analyze_coordinates()
        
        print(f"\n📊 STATISTIQUES GÉNÉRALES")
        print(f"{'='*50}")
        print(f"Total d'images: {len(self.analysis_df)}")
        print(f"Images avec coordonnées valides: {sum(self.analysis_df['Coordonnées_valides'])}")
        print(f"Images avec problèmes: {sum(~self.analysis_df['Coordonnées_valides'])}")
        
        problemes = self.analysis_df[~self.analysis_df['Coordonnées_valides']]
        
        if len(problemes) > 0:
            print(f"\n❌ {len(problemes)} IMAGES AVEC PROBLÈMES:")
            print(problemes[['Index', 'Nom_du_levé', 'Nb_coordonnées', 'Problèmes']].to_string())
        else:
            print("\n✅ Toutes les coordonnées sont valides !")
    
    def show_row_details(self, index: int):
        """Affiche les détails d'une ligne spécifique"""
        if index >= len(self.df) or index < 0:
            print(f"❌ Index {index} invalide (max: {len(self.df)-1})")
            return None
        
        row = self.df.iloc[index]
        coords = self.parse_coordinates(row['Coordonnées'])
        
        print(f"\n📋 LIGNE {index}")
        print(f"{'='*30}")
        print(f"Nom du levé: {row['Nom_du_levé']}")
        print(f"Nombre de coordonnées: {len(coords)}")
        
        if coords:
            print("Coordonnées actuelles:")
            for i, coord in enumerate(coords):
                x, y = coord.get('x', 0), coord.get('y', 0)
                valid, issues = self.validate_coordinate(x, y)
                status = "✅" if valid else "❌"
                print(f"  {i+1}. X={x}, Y={y} {status}")
                if not valid:
                    print(f"     Problème: {issues}")
        else:
            print("❌ Aucune coordonnée trouvée")
        
        return row
    
    def update_coordinates(self, index: int, new_coordinates: List[Dict]) -> bool:
        """Met à jour les coordonnées d'une ligne"""
        if index >= len(self.df) or index < 0:
            print(f"❌ Index {index} invalide")
            return False
        
        valid_coords = []
        for coord in new_coordinates:
            if 'x' in coord and 'y' in coord:
                x, y = float(coord['x']), float(coord['y'])
                valid, issues = self.validate_coordinate(x, y)
                if valid:
                    valid_coords.append({'x': x, 'y': y})
                else:
                    print(f"⚠️ Coordonnée ignorée X={x}, Y={y}: {issues}")
        
        if valid_coords:
            coord_string = json.dumps(valid_coords).replace('"', '""')
            self.df.loc[index, 'Coordonnées'] = coord_string
            print(f"✅ {len(valid_coords)} coordonnées mises à jour pour la ligne {index}")
            # Réanalyser après modification
            self.analyze_coordinates()
            return True
        else:
            print("❌ Aucune coordonnée valide à mettre à jour")
            return False
    
    def interactive_edit(self):
        """Mode d'édition interactif"""
        while True:
            print(f"\n🔧 ÉDITEUR INTERACTIF DE COORDONNÉES")
            print(f"{'='*50}")
            print("1. Voir l'analyse générale")
            print("2. Voir les détails d'une ligne")
            print("3. Modifier les coordonnées d'une ligne")
            print("4. Correction automatique des problèmes courants")
            print("5. Sauvegarder les modifications")
            print("6. Quitter")
            
            try:
                choice = input("\n👆 Votre choix (1-6): ").strip()
                
                if choice == '1':
                    self.show_analysis()
                
                elif choice == '2':
                    index = int(input("📋 Index de la ligne à voir: "))
                    self.show_row_details(index)
                
                elif choice == '3':
                    index = int(input("✏️ Index de la ligne à modifier: "))
                    self.show_row_details(index)
                    
                    print("\n💡 Entrez les nouvelles coordonnées (format: x1,y1 x2,y2 x3,y3...)")
                    print("Exemple: 427094.7,712773.67 427110.61,712767.66")
                    coord_input = input("Nouvelles coordonnées: ").strip()
                    
                    if coord_input:
                        try:
                            new_coords = []
                            pairs = coord_input.split()
                            for pair in pairs:
                                x, y = pair.split(',')
                                new_coords.append({'x': float(x), 'y': float(y)})
                            
                            self.update_coordinates(index, new_coords)
                        except ValueError:
                            print("❌ Format invalide. Utilisez: x1,y1 x2,y2...")
                
                elif choice == '4':
                    self.fix_common_issues()
                
                elif choice == '5':
                    filename = input("💾 Nom du fichier (défaut: submissions_reordered_corrected.csv): ").strip()
                    if not filename:
                        filename = 'submissions_reordered_corrected.csv'
                    self.save_corrected_csv(filename)
                
                elif choice == '6':
                    print("👋 Au revoir !")
                    break
                
                else:
                    print("❌ Choix invalide")
            
            except KeyboardInterrupt:
                print("\n👋 Au revoir !")
                break
            except ValueError:
                print("❌ Veuillez entrer un nombre valide")
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def fix_common_issues(self):
        """Corrige automatiquement les problèmes courants"""
        fixes_applied = 0
        
        for idx, row in self.df.iterrows():
            coords = self.parse_coordinates(row['Coordonnées'])
            if not coords:
                continue
                
            modified = False
            fixed_coords = []
            
            for coord in coords:
                x, y = coord.get('x', 0), coord.get('y', 0)
                
                # Ignorer les coordonnées nulles
                if x == 0 or y == 0:
                    print(f"⚠️ Ligne {idx}: Coordonnée nulle ignorée X={x}, Y={y}")
                    continue
                
                # Corriger les coordonnées trop courtes
                original_x, original_y = x, y
                if len(str(int(x))) < 6 and x > 0:
                    x = x * 10 ** (6 - len(str(int(x))))
                    modified = True
                
                if len(str(int(y))) < 6 and y > 0:
                    y = y * 10 ** (6 - len(str(int(y))))
                    modified = True
                
                if modified:
                    print(f"🔧 Ligne {idx}: Coordonnée corrigée ({original_x}, {original_y}) → ({x}, {y})")
                
                # Garder les coordonnées valides
                valid, _ = self.validate_coordinate(x, y)
                if valid:
                    fixed_coords.append({'x': x, 'y': y})
            
            # Mettre à jour si des modifications ont été faites
            if modified and fixed_coords:
                coord_string = json.dumps(fixed_coords).replace('"', '""')
                self.df.loc[idx, 'Coordonnées'] = coord_string
                fixes_applied += 1
        
        print(f"✅ {fixes_applied} lignes corrigées automatiquement")
        self.analyze_coordinates()
    
    def save_corrected_csv(self, filename: str = 'submissions_reordered_corrected.csv'):
        """Sauvegarde le DataFrame corrigé"""
        try:
            # Faire une sauvegarde de l'original
            shutil.copy2(self.csv_file, f"{self.csv_file}.backup")
            print(f"✅ Sauvegarde de l'original créée: {self.csv_file}.backup")
            
            # Sauvegarder la version corrigée
            self.df.to_csv(filename, index=False)
            print(f"✅ Version corrigée sauvegardée: {filename}")
            
            # Analyser la version corrigée
            self.analyze_coordinates()
            valid_count = sum(self.analysis_df['Coordonnées_valides'])
            total_count = len(self.analysis_df)
            
            print(f"📊 Résultats: {valid_count}/{total_count} images avec coordonnées valides")
            
            remaining_issues = self.analysis_df[~self.analysis_df['Coordonnées_valides']]
            if len(remaining_issues) > 0:
                print(f"⚠️ {len(remaining_issues)} images nécessitent encore des corrections")
            else:
                print("🎉 Toutes les coordonnées sont maintenant valides !")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return False

def main():
    """Fonction principale"""
    print("🚀 Éditeur de Coordonnées - Version CLI")
    print("=" * 50)
    
    # Chercher le fichier CSV
    csv_file = 'submissions_TheThinkers.csv'
    
    # Créer l'éditeur
    editor = CoordinateEditor(csv_file)
    
    # Analyser les coordonnées
    editor.analyze_coordinates()
    
    # Mode interactif
    editor.interactive_edit()

if __name__ == "__main__":
    main()