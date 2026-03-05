import csv
import sys

# Vous pouvez si nécessaire ajouter d'autres fonctions

def charger_csv(fichier_csv):
    """
    Charge un fichier CSV et retourne une liste de dictionnaires.
    Pour chaque valeur lue, on tente une conversion en int ou float si possible.
    """
    s_retour = []
    try:
        with open(fichier_csv, mode='r', newline='', encoding='utf-8') as csvfile:
            lecteur = csv.DictReader(csvfile, delimiter=';')
            for ligne in lecteur:
                new_ligne = {}
                for key, value in ligne.items():
                    if value is not None:
                        v = value.strip()
                        # Tente la conversion en entier (prise en charge des signes)
                        if v.isdigit() or (v and v[0] in "+-" and v[1:].isdigit()):
                            new_ligne[key] = int(v)
                        else:
                            try:
                                f_val = float(v)
                                new_ligne[key] = int(f_val) if f_val.is_integer() else f_val
                            except ValueError:
                                new_ligne[key] = v
                    else:
                        new_ligne[key] = value
                s_retour.append(new_ligne)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {fichier_csv} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue lors du chargement du fichier {fichier_csv} : {e}")
    return s_retour


def projection_simple(s, nom_de_colonne):
    """
    Extrait la colonne spécifiée de la structure s.

    Chaque élément de s est un dictionnaire et s_retour sera constitué
    d'une liste de dictionnaires ne contenant que la clé nom_de_colonne
    et sa valeur associée issue de s.

    Paramètres:
        s (list): Liste de dictionnaires représentant les données.
        nom_de_colonne (str): Le nom de la colonne à extraire.

    Retour:
        list: Une liste de dictionnaires avec uniquement la colonne spécifiée.
    """
    s_retour = []
    for ligne in s:
        if nom_de_colonne in ligne:
            s_retour.append({nom_de_colonne: ligne[nom_de_colonne]})
        else:
            print(f"Avertissement : la colonne '{nom_de_colonne}' n'existe pas dans la ligne {ligne}")
    return s_retour

def projection_multiple(s, liste_colonnes):
    s_retour = []
    for row in s:
        projected_row = {}
        for col in liste_colonnes:
            if col in row:
                projected_row[col] = row[col]
        s_retour.append(projected_row)
    return s_retour

def projection_simple_distinct(s, nom_de_colonne):
    unique_values = []
    for ligne in s:
        if nom_de_colonne in ligne:
            valeur = ligne[nom_de_colonne]
            try:
                valeur = int(valeur)
            except (ValueError, TypeError):
                pass  # Conserve la valeur sous forme de chaîne si la conversion échoue
            if valeur not in unique_values:
                unique_values.append(valeur)
        else:
            print(f"Avertissement : la colonne '{nom_de_colonne}' n'existe pas dans la ligne {ligne}")
    
    # On conserve l'ordre d'apparition (pas de tri)
    s_retour = [{nom_de_colonne: v} for v in unique_values]
    return s_retour

def projection_multiple_distinct(s, liste_colonnes):
    """
    Renvoie une structure de données s_retour qui contient, pour chaque ligne de s,
    uniquement les colonnes présentes dans liste_colonnes, en éliminant les doublons.
    
    Pour chaque valeur dans les colonnes, la fonction tente de la convertir en entier,
    puis en float si la conversion échoue, sinon on conserve la chaîne (après strip).
    
    L'ordre d'apparition est conservé : seule la première occurrence d'une combinaison 
    unique des valeurs (dans l'ordre de liste_colonnes) est conservée.
    
    Paramètres:
        s (list): Liste de dictionnaires représentant les données.
        liste_colonnes (list): Liste des noms de colonnes à extraire.
        
    Retour:
        list: s_retour, liste de dictionnaires contenant les colonnes spécifiées, sans doublons.
    """
    seen = set()
    s_retour = []
    for row in s:
        new_row = {}
        for col in liste_colonnes:
            if col in row:
                val = row[col]
                try:
                    new_val = int(val)
                except (ValueError, TypeError):
                    try:
                        new_val = float(val)
                    except (ValueError, TypeError):
                        new_val = val.strip() if isinstance(val, str) else val
                new_row[col] = new_val
        if len(new_row) == len(liste_colonnes):
            key = tuple(new_row[col] for col in liste_colonnes)
            if key not in seen:
                seen.add(key)
                s_retour.append(new_row)
    return s_retour

def selection_multiple(s, conditions, operateur_booleen):
    """
    Sélectionne les lignes de s qui vérifient les conditions données.

    Paramètres:
        s (list): Liste de dictionnaires représentant les données.
        conditions (list): Liste de tuples (colonne, opérateur, valeur).
                           L'opérateur peut être '=', '==', '!=', '<', '<=', '>' ou '>='.
        operateur_booleen (str): "AND" ou "OR" pour combiner les conditions.

    Retour:
        list: Liste de dictionnaires vérifiant la condition.
    """
    s_retour = []
    
    for row in s:
        evaluations = []
        for col, op, val in conditions:
            if col in row:
                cell = row[col]
                # Si la valeur de comparaison est numérique, on tente de convertir la valeur de la ligne en float
                if isinstance(val, (int, float)):
                    try:
                        cell = float(cell)
                    except (ValueError, TypeError):
                        evaluations.append(False)
                        continue
                else:
                    if isinstance(cell, str):
                        cell = cell.strip()
                if op in ["==", "="]:
                    evaluations.append(cell == val)
                elif op == "!=":
                    evaluations.append(cell != val)
                elif op == "<":
                    evaluations.append(cell < val)
                elif op == "<=":
                    evaluations.append(cell <= val)
                elif op == ">":
                    evaluations.append(cell > val)
                elif op == ">=":
                    evaluations.append(cell >= val)
                else:
                    raise ValueError(f"Opérateur non supporté : {op}")
            else:
                evaluations.append(False)
        
        if operateur_booleen == "AND" and all(evaluations):
            s_retour.append(row)
        elif operateur_booleen == "OR" and any(evaluations):
            s_retour.append(row)
    
    return s_retour

def selection_simple(s, nom_de_colonne, operateur, valeur):
    """
    Sélectionne les lignes de s où la colonne nom_de_colonne satisfait la condition
    (opérateur, valeur).

    Paramètres:
        s (list): Liste de dictionnaires représentant les données.
        nom_de_colonne (str): La colonne sur laquelle appliquer la condition.
        operateur (str): Opérateur de comparaison ('=', '==', '!=', '<', '<=', '>' ou '>=').
        valeur : La valeur de comparaison (int, float ou str).

    Retour:
        list: Liste de dictionnaires vérifiant la condition.
    """
    return selection_multiple(s, [(nom_de_colonne, operateur, valeur)], "AND")

def minimum(s, nom_de_colonne):
    """
    Renvoie la valeur minimum de la colonne 'nom_de_colonne' dans s.
    
    Si la colonne contient des valeurs non vides, la fonction tente de déterminer
    si la colonne est numérique (en testant la première valeur valide). Si c'est le cas,
    seules les valeurs convertibles en float sont considérées pour le calcul.
    Sinon, la comparaison se fait sur les chaînes.
    
    Si aucune valeur valide n'est trouvée, retourne None.
    """
    valid_values = []
    for row in s:
        if nom_de_colonne in row:
            value = row[nom_de_colonne]
            if value is None:
                continue
            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    continue
            valid_values.append(value)
    
    if not valid_values:
        return None

    # Détection du type : si la première valeur peut être convertie en float, on traite la colonne comme numérique
    try:
        _ = float(valid_values[0])
        numeric_values = []
        for v in valid_values:
            try:
                numeric_values.append(float(v))
            except (ValueError, TypeError):
                continue
        if not numeric_values:
            return None
        min_val = min(numeric_values)
        return int(min_val) if min_val.is_integer() else min_val
    except (ValueError, TypeError):
        # Traitement en tant que chaîne
        min_val = min(valid_values, key=lambda x: x)
        return min_val


def maximum(s, nom_de_colonne):
    """
    Renvoie la valeur maximum de la colonne 'nom_de_colonne' dans s.
    
    Si la colonne contient des valeurs non vides, la fonction tente de déterminer
    si la colonne est numérique (en testant la première valeur valide). Si c'est le cas,
    seules les valeurs convertibles en float sont considérées pour le calcul.
    Sinon, la comparaison se fait sur les chaînes.
    
    Si aucune valeur valide n'est trouvée, retourne None.
    """
    valid_values = []
    for row in s:
        if nom_de_colonne in row:
            value = row[nom_de_colonne]
            if value is None:
                continue
            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    continue
            valid_values.append(value)
    
    if not valid_values:
        return None

    try:
        _ = float(valid_values[0])
        numeric_values = []
        for v in valid_values:
            try:
                numeric_values.append(float(v))
            except (ValueError, TypeError):
                continue
        if not numeric_values:
            return None
        max_val = max(numeric_values)
        return int(max_val) if max_val.is_integer() else max_val
    except (ValueError, TypeError):
        max_val = max(valid_values, key=lambda x: x)
        return max_val


def somme(s, nom_de_colonne):
    """
    Renvoie la somme des valeurs de la colonne 'nom_de_colonne' dans s.
    
    Seules les valeurs convertibles en float (après suppression des espaces si chaîne)
    sont considérées dans le calcul. Si aucune valeur valide n'est trouvée, retourne None.
    """
    total = 0.0
    valid = False
    for row in s:
        if nom_de_colonne in row:
            val = row[nom_de_colonne]
            if val is None:
                continue
            if isinstance(val, str):
                val = val.strip()
                if val == "":
                    continue
            try:
                num = float(val)
            except (ValueError, TypeError):
                continue
            total += num
            valid = True
    return None if not valid else (int(total) if total.is_integer() else total)


def compte(s, nom_de_colonne):
    """
    Renvoie le nombre de valeurs non vides dans la colonne 'nom_de_colonne' de s.
    
    Si aucune valeur valide n'est trouvée, retourne None.
    """
    count = 0
    for row in s:
        if nom_de_colonne in row:
            val = row[nom_de_colonne]
            if val is None:
                continue
            if isinstance(val, str):
                if val.strip() == "":
                    continue
            count += 1
    return None if count == 0 else count


def moyenne(s, nom_de_colonne):
    """
    Renvoie la moyenne des valeurs de la colonne 'nom_de_colonne' dans s.
    
    Seules les valeurs convertibles en float (après suppression des espaces) sont prises en compte.
    Si aucune valeur valide n'est trouvée, retourne None.
    """
    total = 0.0
    count = 0
    for row in s:
        if nom_de_colonne in row:
            val = row[nom_de_colonne]
            if val is None:
                continue
            if isinstance(val, str):
                val = val.strip()
                if val == "":
                    continue
            try:
                num = float(val)
            except (ValueError, TypeError):
                continue
            total += num
            count += 1
    if count == 0:
        return None
    avg = total / count
    return int(avg) if avg.is_integer() else avg


def ordonne(s, nom_de_colonne, sens):
    """
    Trie la structure s (liste de dictionnaires) selon la valeur de la colonne
    nom_de_colonne, en convertissant les valeurs en int ou float si possible.
    
    Pour chaque dictionnaire de s, toutes les valeurs sont converties :
      - Si la valeur est une chaîne, elle est d'abord "strip" puis convertie en int ou float si possible.
    
    L'algorithme de tri fusion est appliqué pour trier la liste en ordre
    croissant (si sens == 'croissant') ou décroissant (si sens == 'decroissant').
    
    Paramètres:
        s (list): Liste de dictionnaires représentant les données.
        nom_de_colonne (str): Nom de la colonne utilisée pour le tri.
        sens (str): 'croissant' pour un tri ascendant, 'decroissant' pour un tri descendant.
    
    Retour:
        list: La structure s_retour (liste de dictionnaires) triée.
    """
    def convert_value(val):
        if isinstance(val, str):
            v = val.strip()
            try:
                return int(v)
            except ValueError:
                try:
                    return float(v)
                except ValueError:
                    return v
        return val

    s_converted = []
    for d in s:
        new_d = {key: convert_value(val) for key, val in d.items()}
        s_converted.append(new_d)

    reverse = sens.lower() == 'decroissant'

    def merge_sort(lst):
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        left = merge_sort(lst[:mid])
        right = merge_sort(lst[mid:])
        return merge(left, right)

    def merge(left, right):
        merged = []
        i, j = 0, 0
        while i < len(left) and j < len(right):
            a = left[i][nom_de_colonne]
            b = right[j][nom_de_colonne]
            if not reverse:
                if a <= b:
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    j += 1
            else:
                if a >= b:
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    j += 1
        while i < len(left):
            merged.append(left[i])
            i += 1
        while j < len(right):
            merged.append(right[j])
            j += 1
        return merged

    s_retour = merge_sort(s_converted)
    return s_retour

def ordonne_multiple(s, liste_colonnes, sens):
    """
    Trie la structure s (liste de dictionnaires) selon les colonnes données dans liste_colonnes.

    Si sens == 'croissant', tous les critères sont triés par ordre croissant.
    Si sens == 'decroissant', tous les critères sont triés par ordre décroissant.
    
    Les valeurs sont converties (int/float si possible) pour uniformiser les comparaisons.
    Retourne la structure s_retour, c'est-à-dire une liste de dictionnaires triée.
    """
    def convert_value(val):
        if isinstance(val, str):
            v = val.strip()
            try:
                return int(v)
            except ValueError:
                try:
                    return float(v)
                except ValueError:
                    return v
        return val

    s_converted = []
    for d in s:
        new_d = {key: convert_value(val) for key, val in d.items()}
        s_converted.append(new_d)

    def compare_rows(row1, row2):
        for key in liste_colonnes:
            v1 = row1.get(key)
            v2 = row2.get(key)
            if v1 == v2:
                continue
            if sens.lower().strip() == 'decroissant':
                return -1 if v1 > v2 else 1
            else:
                return -1 if v1 < v2 else 1
        return 0

    def quick_sort(lst):
        if len(lst) <= 1:
            return lst
        pivot = lst[len(lst) // 2]
        left, equal, right = [], [], []
        for element in lst:
            cmp_val = compare_rows(element, pivot)
            if cmp_val < 0:
                left.append(element)
            elif cmp_val > 0:
                right.append(element)
            else:
                equal.append(element)
        return quick_sort(left) + equal + quick_sort(right)

    s_retour = quick_sort(s_converted)
    return s_retour

def jointure(s_1, s_2, nom_de_colonne):
    """
    Réalise une jointure interne (inner join) entre s_1 et s_2 sur la colonne nom_de_colonne.
    
    Seules les valeurs de la colonne de jointure sont converties (ex. '1' devient 1) ;
    les autres colonnes conservent leur type d'origine.
    Pour chaque ligne de s_1, on recherche dans s_2 les lignes dont la valeur de nom_de_colonne correspond,
    puis on fusionne les dictionnaires (les valeurs de s_2 écrasant celles de s_1 en cas de conflit).
    
    Retourne une liste de dictionnaires (s_retour) représentant le résultat de la jointure.
    """
    def convert_value(val):
        if isinstance(val, str):
            v = val.strip()
            try:
                return int(v)
            except ValueError:
                try:
                    return float(v)
                except ValueError:
                    return v
        return val

    def convert_row(row, join_key):
        new_row = {}
        for k, v in row.items():
            if k == join_key:
                new_row[k] = convert_value(v)
            else:
                new_row[k] = v
        return new_row

    s1_converted = [convert_row(row, nom_de_colonne) for row in s_1]
    s2_converted = [convert_row(row, nom_de_colonne) for row in s_2]

    s_retour = []
    index = {}
    for row in s2_converted:
        key = row.get(nom_de_colonne)
        if key is not None:
            index.setdefault(key, []).append(row)

    for row1 in s1_converted:
        key = row1.get(nom_de_colonne)
        if key is not None and key in index:
            for row2 in index[key]:
                new_row = {}
                new_row.update(row1)
                new_row.update(row2)
                s_retour.append(new_row)

    return s_retour


def main():
    if len(sys.argv) != 4:
        print("Usage: python interrogation_donnees.py data1.csv data2.csv data3.csv")
        return

    fichier_1, fichier_2, fichier_3 = sys.argv[1], sys.argv[2], sys.argv[3]
    S1 = charger_csv(fichier_1)
    S2 = charger_csv(fichier_2)
    S3 = charger_csv(fichier_3)
    print("Données chargées.")

    while True:
        print("\n📋 Menu proposé :")
        print("1. projection_simple(Si, nomDeColonne)")
        print("2. projection_multiple(Si, [liste de nomDeColonnes])")
        print("3. projection_simple_distinct(Si, nomDeColonne)")
        print("4. projection_multiple_distinct(Si, [liste de nomDeColonnes])")
        print("5. sélection_simple(Si, nomDeColonne, opérateur, valeur)")
        print("6. sélection_multiple(Si, [(nomDeColonne, opérateur, valeur)], opérateurbooléen)")
        print("7. min(Si, nomDeColonne)")
        print("8. max(Si, nomDeColonne)")
        print("9. compte(Si, nomDeColonne)")
        print("10. somme(Si, nomDeColonne)")
        print("11. moyenne(Si, nomDeColonne)")
        print("12. ordonne(Si, nomDeColonne, sens)")
        print("13. ordonne_multiple(Si, [liste de nomDeColonnes], sens)")
        print("14. jointure(Si, Sj, nomDeColonne)")
        print("15. Quitter")
        
        choice = input("Entrez votre choix (1-15) : ").strip()
        
        if choice == "1":
            col = input("Entrez le nom de la colonne : ")
            result = projection_simple(S1, col)
            print("Résultat :", result)
        elif choice == "2":
            cols = input("Entrez la liste des colonnes séparées par des virgules : ")
            liste_cols = [c.strip() for c in cols.split(",") if c.strip()]
            result = projection_multiple(S1, liste_cols)
            print("Résultat :", result)
        elif choice == "3":
            col = input("Entrez le nom de la colonne pour projection_simple_distinct : ")
            result = projection_simple_distinct(S1, col)
            print("Résultat :", result)
        elif choice == "4":
            cols = input("Entrez la liste des colonnes (séparées par des virgules) pour projection_multiple_distinct : ")
            liste_cols = [c.strip() for c in cols.split(",") if c.strip()]
            result = projection_multiple_distinct(S1, liste_cols)
            print("Résultat :", result)
        elif choice == "5":
            col = input("Entrez le nom de la colonne pour sélection_simple : ")
            op = input("Entrez l'opérateur (ex. '=', '!=', '<', '<=', '>', '>=') : ")
            val = input("Entrez la valeur de comparaison : ")
            try:
                if '.' in val:
                    val_converted = float(val)
                else:
                    val_converted = int(val)
            except ValueError:
                val_converted = val
            result = selection_simple(S1, col, op, val_converted)
            print("Résultat :", result)
        elif choice == "6":
            cond = input("Entrez une condition sous la forme 'col,op,val' : ")
            parts = [x.strip() for x in cond.split(",")]
            if len(parts) != 3:
                print("Condition invalide.")
            else:
                col, op, val = parts
                try:
                    if '.' in val:
                        val_converted = float(val)
                    else:
                        val_converted = int(val)
                except ValueError:
                    val_converted = val
                op_bool = input("Entrez l'opérateur booléen pour combiner (AND/OR) : ").upper()
                result = selection_multiple(S1, [(col, op, val_converted)], op_bool)
                print("Résultat :", result)
        elif choice == "7":
            col = input("Entrez le nom de la colonne pour min : ")
            try:
                result = minimum(S1, col)
                print("Résultat :", result)
            except Exception as e:
                print("Erreur :", e)
        elif choice == "8":
            col = input("Entrez le nom de la colonne pour max : ")
            try:
                result = maximum(S1, col)
                print("Résultat :", result)
            except Exception as e:
                print("Erreur :", e)
        elif choice == "9":
            col = input("Entrez le nom de la colonne pour compte : ")
            result = compte(S1, col)
            print("Résultat :", result)
        elif choice == "10":
            col = input("Entrez le nom de la colonne pour somme : ")
            try:
                result = somme(S1, col)
                print("Résultat :", result)
            except Exception as e:
                print("Erreur :", e)
        elif choice == "11":
            col = input("Entrez le nom de la colonne pour moyenne : ")
            try:
                result = moyenne(S1, col)
                print("Résultat :", result)
            except Exception as e:
                print("Erreur :", e)
        elif choice == "12":
            col = input("Entrez le nom de la colonne pour ordonne : ")
            sens = input("Entrez le sens (croissant/decroissant) : ")
            result = ordonne(S1, col, sens)
            print("Résultat :", result)
        elif choice == "13":
            cols = input("Entrez la liste des colonnes (séparées par des virgules) pour ordonne_multiple : ")
            liste_cols = [c.strip() for c in cols.split(",") if c.strip()]
            sens = input("Entrez le sens (croissant/decroissant) : ")
            result = ordonne_multiple(S1, liste_cols, sens)
            print("Résultat :", result)
        elif choice == "14":
            col = input("Entrez le nom de la colonne de jointure : ")
            # Utilisation de S1 et S2 pour la jointure
            result = jointure(S1, S2, col)
            print("Résultat :", result)
        elif choice == "15":
            print("Au revoir !")
            break
        else:
            print("Choix invalide, réessayez.")

if __name__ == "__main__":
    main()