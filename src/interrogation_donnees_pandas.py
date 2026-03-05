import sys
import pandas as pd
import csv
import numpy as np

def charger_csv(nom_fichier):
    """
    Charge un fichier CSV délimité par des points-virgules dans un DataFrame.

    :param nom_fichier: chemin vers le fichier CSV
    :return: pandas.DataFrame
    """
    return pd.read_csv(nom_fichier, sep=';')


def projection_simple(s, nom_de_colonne):
    """
    Retourne la colonne spécifiée du DataFrame s.
    """
    return s[nom_de_colonne]


def projection_multiple(s, noms_de_colonnes):
    """
    Retourne un sous-DataFrame composé des colonnes spécifiées.
    """
    return s[noms_de_colonnes]


def projection_simple_distinct(s, nom_de_colonne):
    """
    Retourne la colonne spécifiée sans doublons.
    """
    return s[nom_de_colonne].drop_duplicates()


def projection_multiple_distinct(s, noms_de_colonnes):
    """
    Retourne un sous-DataFrame composé des colonnes spécifiées,
    en éliminant les doublons.
    """
    return s[noms_de_colonnes].drop_duplicates()


def selection_simple(s, nom_de_colonne, operateur, valeur):
    """
    Filtre le DataFrame s selon une condition simple.
    """
    if operateur in ["=", "=="]:
        return s[s[nom_de_colonne] == valeur]
    elif operateur == "!=":
        return s[s[nom_de_colonne] != valeur]
    elif operateur == ">":
        return s[s[nom_de_colonne] > valeur]
    elif operateur == ">=":
        return s[s[nom_de_colonne] >= valeur]
    elif operateur == "<":
        return s[s[nom_de_colonne] < valeur]
    elif operateur == "<=":
        return s[s[nom_de_colonne] <= valeur]
    else:
        raise ValueError(f"Opérateur non supporté: {operateur}")


def selection_multiple(s, conditions, operateur_booleen):
    """
    Filtre le DataFrame s en combinant plusieurs conditions.
    """
    masks = []
    for colonne, op, valeur in conditions:
        if op in ["=", "=="]:
            mask = s[colonne] == valeur
        elif op == "!=":
            mask = s[colonne] != valeur
        elif op == ">":
            mask = s[colonne] > valeur
        elif op == ">=":
            mask = s[colonne] >= valeur
        elif op == "<":
            mask = s[colonne] < valeur
        elif op == "<=":
            mask = s[colonne] <= valeur
        else:
            raise ValueError(f"Opérateur non supporté: {op}")
        masks.append(mask)

    if operateur_booleen.lower() == "and":
        combined = masks[0]
        for m in masks[1:]:
            combined &= m
    elif operateur_booleen.lower() == "or":
        combined = masks[0]
        for m in masks[1:]:
            combined |= m
    else:
        raise ValueError(f"Opérateur booléen non supporté: {operateur_booleen}")

    return s[combined]


def minimum(s, nom_de_colonne):
    """Renvoie la valeur minimale de la colonne."""
    return s[nom_de_colonne].min()


def maximum(s, nom_de_colonne):
    """Renvoie la valeur maximale de la colonne."""
    return s[nom_de_colonne].max()


def compte(s, nom_de_colonne):
    """Compte le nombre de valeurs non nulles."""
    return int(s[nom_de_colonne].count())


def somme(s, nom_de_colonne):
    """Calcule la somme des valeurs et renvoie un scalaire Python."""
    result = s[nom_de_colonne].sum()
    return result.item() if hasattr(result, 'item') else result


def moyenne(s, nom_de_colonne):
    """Calcule la moyenne des valeurs."""
    return s[nom_de_colonne].mean()


def ordonne(s, nom_de_colonne, sens):
    """Trie le DataFrame selon une colonne."""
    asc = sens.lower() == 'asc'
    return s.sort_values(by=nom_de_colonne, ascending=asc)


def ordonne_multiple(s, noms_de_colonnes, sens):
    """Trie le DataFrame selon plusieurs colonnes."""
    asc = sens.lower() == 'asc'
    return s.sort_values(by=noms_de_colonnes, ascending=asc)


def jointure(s1, s2, nom_de_colonne):
    """
    Effectue une jointure interne (inner join) entre deux DataFrames
    sur la colonne spécifiée.

    :param s1: premier pandas.DataFrame
    :param s2: deuxième pandas.DataFrame
    :param nom_de_colonne: colonne commune pour la jointure
    :return: pandas.DataFrame résultant de la jointure
    """
    return pd.merge(s1, s2, on=nom_de_colonne, how='inner')


def main():
    """
    Point d'entrée du script :
    charge trois fichiers CSV délimités par des points-virgules
    et propose un menu interactif.
    Usage: python interrogation_donnees_pandas.py data1.csv data2.csv data3.csv
    """
    if len(sys.argv) != 4:
        print("Usage: python interrogation_donnees_pandas.py data1.csv data2.csv data3.csv")
        return

    # Chargement des données via la fonction dédiée
    s = charger_csv(sys.argv[1])
    s2 = charger_csv(sys.argv[2])
    s3 = charger_csv(sys.argv[3])

    # Jeu de données combiné pour analyses globales
    df = pd.concat([s, s2, s3], ignore_index=True)

    while True:
        print("\nMenu des opérations:")
        print("1. Projection simple")
        print("2. Projection multiple")
        print("3. Projection simple distinct")
        print("4. Projection multiple distinct")
        print("5. Sélection simple")
        print("6. Sélection multiple")
        print("7. Minimum")
        print("8. Maximum")
        print("9. Compte")
        print("10. Somme")
        print("11. Moyenne")
        print("12. Ordonner")
        print("13. Ordonner multiple")
        print("14. Jointure")
        print("15. Quitter")

        choix = input("Entrez votre choix: ")
        if choix == '15':
            break

        # Choix du DataFrame
        print("Sources: 1=data1, 2=data2, 3=data3, 4=combinée")
        ds = input("Sélectionnez la source (1-4): ")
        if ds == '1':
            s_use = s
        elif ds == '2':
            s_use = s2
        elif ds == '3':
            s_use = s3
        elif ds == '4':
            s_use = df
        else:
            print("Source invalide.")
            continue

        if choix == '14':
            col = input("Colonne commune pour jointure: ")
            print("Deuxième source (1-4): ")
            other = input("Source: ")
            if other == ds:
                print("Deux sources doivent être différentes.")
                continue
            s_use2 = {'1': s, '2': s2, '3': s3, '4': df}.get(other)
            print(jointure(s_use, s_use2, col).head())
        else:
            col = input("Colonne: ")
            if choix == '1':
                print(projection_simple(s_use, col).head())
            elif choix == '2':
                cols = input("Colonnes (virgules): ")
                cols_list = [c.strip() for c in cols.split(',')]
                print(projection_multiple(s_use, cols_list).head())
            elif choix == '3':
                print(projection_simple_distinct(s_use, col))
            elif choix == '4':
                cols = input("Colonnes (virgules): ")
                cols_list = [c.strip() for c in cols.split(',')]
                print(projection_multiple_distinct(s_use, cols_list))
            elif choix == '5':
                op = input("Opérateur (==, !=, >, >=, <, <=): ")
                val = input("Valeur: ")
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                print(selection_simple(s_use, col, op, val))
            elif choix == '6':
                print("Format: col,op,val; ...")
                conds = input("Conditions: ")
                conditions = []
                for cond in conds.split(';'):
                    parts = cond.split(',')
                    if len(parts) == 3:
                        c, o, v = [p.strip() for p in parts]
                        try:
                            v = int(v)
                        except ValueError:
                            try:
                                v = float(v)
                            except ValueError:
                                pass
                        conditions.append((c, o, v))
                bool_op = input("and/or: ")
                print(selection_multiple(s_use, conditions, bool_op))
            elif choix == '7':
                print(minimum(s_use, col))
            elif choix == '8':
                print(maximum(s_use, col))
            elif choix == '9':
                print(compte(s_use, col))
            elif choix == '10':
                print(somme(s_use, col))
            elif choix == '11':
                print(moyenne(s_use, col))
            elif choix == '12':
                sens = input("Ordre asc/desc: ")
                print(ordonne(s_use, col, sens).head())
            elif choix == '13':
                cols = input("Colonnes (virgules): ")
                cols_list = [c.strip() for c in cols.split(',')]
                sens = input("asc/desc: ")
                print(ordonne_multiple(s_use, cols_list, sens).head())
            else:
                print("Option non reconnue.")


if __name__ == '__main__':
    main()
