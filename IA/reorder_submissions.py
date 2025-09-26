#!/usr/bin/env python3
"""
Script pour réordonner submissions.csv selon l'ordre de référence
"""

import pandas as pd
import csv
from pathlib import Path

def reorder_submissions():
    """Réordonne submissions.csv selon l'ordre de référence"""
    
    print("🔄 RÉORDONNEMENT SUBMISSIONS.CSV")
    print("="*50)
    
    # Lire l'ordre de référence
    ref_order = []
    with open('Data_Hackathon_IA_2025/submission.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Skip header
        for row in reader:
            if row and row[0]:  # Vérifier que la ligne n'est pas vide
                ref_order.append(row[0])
    
    print(f"📋 Ordre de référence: {len(ref_order)} fichiers")
    
    # Lire notre fichier submissions
    df = pd.read_csv('submissions.csv')
    print(f"📊 Notre fichier: {len(df)} lignes")
    
    # Créer un dictionnaire pour l'accès rapide
    submissions_dict = {}
    for _, row in df.iterrows():
        filename = row['Nom_du_levé']
        submissions_dict[filename] = row
    
    # Créer le nouveau DataFrame dans l'ordre de référence
    reordered_rows = []
    
    # En-tête
    header = df.columns.tolist()
    
    for filename in ref_order:
        if filename in submissions_dict:
            reordered_rows.append(submissions_dict[filename])
            print(f"✅ Trouvé: {filename}")
        else:
            # Créer une ligne vide pour les fichiers manquants
            empty_row = pd.Series(index=header, dtype=str)
            empty_row['Nom_du_levé'] = filename
            empty_row = empty_row.fillna('')
            reordered_rows.append(empty_row)
            print(f"⚠️ Manquant: {filename}")
    
    # Créer le nouveau DataFrame
    reordered_df = pd.DataFrame(reordered_rows, columns=header)
    
    # Sauvegarder
    reordered_df.to_csv('submissions_TheThinkers.csv', index=False)
    
    print(f"✅ Fichier réordonné sauvé: submissions_TheThinkers.csv")
    print(f"📊 {len(reordered_df)} lignes au total")
    
    return reordered_df

if __name__ == "__main__":
    reorder_submissions()