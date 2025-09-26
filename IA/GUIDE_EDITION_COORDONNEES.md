# 📝 Guide d'Édition des Coordonnées

Ce guide vous explique comment corriger les coordonnées non conformes dans le fichier `submissions_reordered.csv`.

## 🎯 Deux options disponibles

### 1. 📓 Notebook Jupyter (Recommandé)
Interface visuelle et interactive avec graphiques.

### 2. 🖥️ Script CLI (Alternative)
Interface en ligne de commande simple.

## 🚀 Installation des dépendances

```bash
# Installer/mettre à jour les dépendances
uv sync
```

## 📓 Option 1: Notebook Jupyter

### Lancement
```bash
# Démarrer Jupyter
uv run jupyter notebook

# Ou Jupyter Lab
uv run jupyter lab
```

### Utilisation
1. Ouvrir le fichier `edit_coordinates.ipynb`
2. Exécuter toutes les cellules (Kernel > Restart & Run All)
3. Suivre les instructions dans le notebook

### Fonctionnalités du notebook
- ✅ **Analyse automatique** des coordonnées non conformes
- ✅ **Visualisation graphique** des coordonnées sur une carte
- ✅ **Interface interactive** pour modifier ligne par ligne
- ✅ **Validation en temps réel** des coordonnées
- ✅ **Correction automatique** des problèmes courants
- ✅ **Sauvegarde sécurisée** avec backup de l'original

## 🖥️ Option 2: Script CLI

### Lancement
```bash
# Lancer l'éditeur en ligne de commande
uv run python edit_coordinates_cli.py
```

### Menu interactif
```
1. Voir l'analyse générale
2. Voir les détails d'une ligne
3. Modifier les coordonnées d'une ligne
4. Correction automatique des problèmes courants
5. Sauvegarder les modifications
6. Quitter
```

### Exemple d'utilisation CLI
```bash
# 1. Voir l'analyse
> 1
📊 STATISTIQUES GÉNÉRALES
Images avec problèmes: 5

# 2. Voir détails ligne problématique
> 2
📋 Index de la ligne à voir: 10

# 3. Modifier les coordonnées
> 3
✏️ Index de la ligne à modifier: 10
💡 Entrez les nouvelles coordonnées: 427094.7,712773.67 427110.61,712767.66
```

## 📋 Format des coordonnées

### Format attendu (UTM Zone 31N - Bénin)
```json
[
  {"x": 427094.7, "y": 712773.67},
  {"x": 427110.61, "y": 712767.66},
  {"x": 427103.58, "y": 712748.94}
]
```

### Plages valides
- **X (Easting)**: 350,000 à 550,000 mètres
- **Y (Northing)**: 650,000 à 850,000 mètres

## 🔍 Types de problèmes détectés

### Problèmes courants
- ❌ **Coordonnées nulles** : X=0 ou Y=0
- ❌ **Coordonnées trop courtes** : Moins de 6 chiffres
- ❌ **Hors plage UTM** : En dehors des limites du Bénin
- ❌ **Format JSON invalide** : Erreur de syntaxe
- ❌ **Coordonnées vides** : Aucune coordonnée dans le champ

### Corrections automatiques
- 🔧 **Ajout de zéros** : 42709 → 427090
- 🔧 **Suppression des nulles** : Ignore les coordonnées (0,0)
- 🔧 **Nettoyage JSON** : Corrige les guillemets doubles

## 💾 Sauvegarde et sécurité

### Fichiers créés
- `submissions_reordered_backup.csv` - Sauvegarde de l'original
- `submissions_reordered_corrected.csv` - Version corrigée
- `analyse_coordonnees.csv` - Rapport d'analyse détaillé

### Workflow recommandé
1. **Analyser** les problèmes détectés
2. **Corriger** les coordonnées problématiques
3. **Valider** que toutes les coordonnées sont maintenant conformes
4. **Sauvegarder** la version corrigée
5. **Remplacer** le fichier original si nécessaire

## 🛠️ Exemples de corrections

### Correction manuelle (Notebook)
```python
# Modifier la ligne 5
nouvelles_coordonnees = [
    {"x": 427094.7, "y": 712773.67},
    {"x": 427110.61, "y": 712767.66}
]
df = update_coordinates(df, 5, nouvelles_coordonnees)
```

### Correction manuelle (CLI)
```bash
# Format: x1,y1 x2,y2 x3,y3...
Nouvelles coordonnées: 427094.7,712773.67 427110.61,712767.66
```

### Correction automatique
Les deux outils incluent une fonction de correction automatique qui :
- Corrige les coordonnées trop courtes
- Supprime les coordonnées nulles
- Valide les plages UTM

## ⚠️ Points d'attention

### Avant de modifier
- ✅ Vérifiez que vous avez la **bonne image** ouverte
- ✅ Comptez le **nombre de coordonnées** visible sur l'image
- ✅ Vérifiez que les coordonnées sont en **UTM** (pas en latitude/longitude)

### Coordonnées suspectes
- 🚨 Coordonnées rondes (ex: 427000, 712000)
- 🚨 Coordonnées répétées à l'identique
- 🚨 Coordonnées avec trop de décimales (>3)

### Validation finale
```bash
# Tester l'API après corrections
uv run python test_single_image.py "chemin/vers/image.jpg"
```

## 🎯 Résultats attendus

### Avant correction
```
📊 Images avec coordonnées valides: 45/88 (51%)
❌ 43 images avec problèmes
```

### Après correction
```
📊 Images avec coordonnées valides: 88/88 (100%)
🎉 Toutes les coordonnées sont maintenant valides !
```

## 🆘 Dépannage

### Erreurs communes
```bash
# Erreur: Fichier CSV non trouvé
cd IA/  # Assurez-vous d'être dans le bon dossier

# Erreur: Jupyter non installé
uv add jupyter matplotlib seaborn

# Erreur: Coordonnées invalides
# Vérifiez les plages UTM (350k-550k, 650k-850k)
```

### Récupération en cas d'erreur
```bash
# Restaurer l'original depuis le backup
cp submissions_reordered.csv.backup submissions_reordered.csv
```

---

**🎯 Une fois les coordonnées corrigées, votre API d'extraction sera parfaitement alignée avec les données de référence !**