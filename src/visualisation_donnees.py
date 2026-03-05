import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import csv

try:
    import folium
    from folium.plugins import HeatMap
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# === FONCTIONS DE TRAITEMENT DES DONNÉES ===

def charger_csv(fichier_csv):
    try:
        df = pd.read_csv(fichier_csv, sep=';')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement du fichier '{fichier_csv}': {e}")

def afficher_colonnes(df):
    print("\nColonnes disponibles :")
    for colonne in df.columns:
        print(f"- {colonne}")

# === FONCTIONS DE VISUALISATION ===

def afficher_histogramme(df, colonne):
    plt.figure(figsize=(10, 6))
    sns.histplot(df[colonne], bins=30, kde=True)
    plt.title(f"Histogramme de {colonne}")
    plt.xlabel(colonne)
    plt.ylabel("Fréquence")
    plt.show()

def afficher_scatter_plot(df, colonne_x, colonne_y):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x=colonne_x, y=colonne_y)
    plt.title(f"Nuage de points : {colonne_x} vs {colonne_y}")
    plt.xlabel(colonne_x)
    plt.ylabel(colonne_y)
    plt.show()

def afficher_box_plot(df, colonne):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=df[colonne])
    plt.title(f"Box plot de {colonne}")
    plt.xlabel(colonne)
    plt.show()

def afficher_bar_plot(df, colonne):
    plt.figure(figsize=(10, 6))
    sns.countplot(x=df[colonne])
    plt.title(f"Graphique en barres de {colonne}")
    plt.xlabel(colonne)
    plt.ylabel("Nombre")
    plt.xticks(rotation=45)
    plt.show()

def creer_carte_toulouse(df):
    if not FOLIUM_AVAILABLE:
        print("Erreur : le module 'folium' n'est pas installé.")
        return
    if 'geo point' not in df.columns:
        print("Erreur : La colonne 'geo point' est absente.")
        return
    df = df.copy()
    df[['latitude', 'longitude']] = df['geo point'].str.split(',', expand=True)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    toulouse_map = folium.Map(location=[43.6045, 1.4442], zoom_start=12)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=row.get('nom', 'Point')
        ).add_to(toulouse_map)
    toulouse_map.save("toulouse_map.html")
    print("Carte enregistrée sous 'toulouse_map.html'")

def creer_heatmap_geographique(df):
    if not FOLIUM_AVAILABLE:
        print("Erreur : le module 'folium' n'est pas installé.")
        return
    if 'geo point' not in df.columns:
        print("Erreur : colonne 'geo point' absente.")
        return
    df = df.copy()
    df[['latitude', 'longitude']] = df['geo point'].str.split(',', expand=True)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    m = folium.Map(location=[43.6045, 1.4442], zoom_start=12)
    HeatMap(data=df[['latitude', 'longitude']].values).add_to(m)
    m.save("heatmap_toulouse.html")
    print("Carte heatmap enregistrée sous 'heatmap_toulouse.html'")

def afficher_pie_chart(df, colonne):
    data = df[colonne].value_counts()
    plt.figure(figsize=(8, 8))
    data.plot.pie(autopct='%1.1f%%', startangle=90)
    plt.ylabel('')
    plt.title(f"Répartition des valeurs de '{colonne}'")
    plt.show()

def barres_groupées(df, cat1, cat2):
    ct = pd.crosstab(df[cat1], df[cat2])
    ct.plot(kind='bar', stacked=False, figsize=(12, 6))
    plt.title(f"Répartition de {cat2} selon {cat1}")
    plt.xlabel(cat1)
    plt.ylabel("Nombre")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def afficher_violin_plot(df, colonne_num, colonne_cat):
    plt.figure(figsize=(10, 6))
    sns.violinplot(x=colonne_cat, y=colonne_num, data=df)
    plt.title(f"Distribution de {colonne_num} par {colonne_cat}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def jointure_et_visualisation(df1, df2, df3):
    df3 = df3.copy()
    df3['code_commune'] = df3['code_commune'].astype('Int64')
    df3['code_type'] = df3['code_type'].astype('Int64')
    df_joint = df3.merge(df1, left_on='code_commune', right_on='Code commune', how='left') \
                 .merge(df2, left_on='code_type', right_on='Code type', how='left')
    if 'commune' in df_joint.columns and 'type' in df_joint.columns:
        ct = pd.crosstab(df_joint['commune'], df_joint['type'])
        ct.plot(kind='bar', stacked=True, figsize=(12, 6))
        plt.title("Nombre de stations par commune et par type")
        plt.xlabel("Commune")
        plt.ylabel("Nombre de stations")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("Colonnes 'commune' ou 'type' manquantes après jointure.")

# === MENU PRINCIPAL ===

def afficher_menu():
    print("\nMenu :")
    print("1. Afficher les colonnes disponibles")
    print("2. Afficher un histogramme")
    print("3. Afficher un nuage de points (scatter plot)")
    print("4. Afficher un box plot")
    print("5. Afficher un graphique en barres")
    print("6. Créer une carte de Toulouse")
    print("7. Camembert des valeurs d'une colonne")
    print("8. Barres groupées entre deux colonnes")
    print("9. Diagramme de violon (violin plot)")
    print("10. Carte heatmap des points géographiques")
    print("11. Fusion des 3 fichiers et visualisation croisée")
    print("12. Quitter")

def main():
    if len(sys.argv) != 4:
        print("Usage: python visualisation_donnees.py fichier1.csv fichier2.csv fichier3.csv")
        return

    fichier_csv1 = sys.argv[1]
    fichier_csv2 = sys.argv[2]
    fichier_csv3 = sys.argv[3]

    try:
        df1 = charger_csv(fichier_csv1)
        df2 = charger_csv(fichier_csv2)
        df3 = charger_csv(fichier_csv3)
    except ValueError as e:
        print(e)
        return

    print("Les fichiers ont été chargés avec succès.")

    while True:
        afficher_menu()
        choix = input("Votre choix : ")

        try:
            if choix == "1":
                print("Fichier 1 :")
                afficher_colonnes(df1)
                print("Fichier 2 :")
                afficher_colonnes(df2)
                print("Fichier 3 :")
                afficher_colonnes(df3)

            elif choix == "2":
                colonne = input("Colonne pour histogramme : ")
                fichier = input("Sur quel fichier (1, 2 ou 3) ? ")
                afficher_histogramme([df1, df2, df3][int(fichier)-1], colonne)

            elif choix == "3":
                x = input("Colonne X : ")
                y = input("Colonne Y : ")
                fichier = input("Fichier (1, 2 ou 3) ? ")
                afficher_scatter_plot([df1, df2, df3][int(fichier)-1], x, y)

            elif choix == "4":
                colonne = input("Colonne pour box plot : ")
                fichier = input("Fichier (1, 2 ou 3) ? ")
                afficher_box_plot([df1, df2, df3][int(fichier)-1], colonne)

            elif choix == "5":
                colonne = input("Colonne pour bar plot : ")
                fichier = input("Fichier (1, 2 ou 3) ? ")
                afficher_bar_plot([df1, df2, df3][int(fichier)-1], colonne)

            elif choix == "6":
                fichier = input("Fichier (1, 2 ou 3) ? ")
                creer_carte_toulouse([df1, df2, df3][int(fichier)-1])

            elif choix == "7":
                colonne = input("Colonne pour camembert : ")
                fichier = input("Fichier (1, 2 ou 3) ? ")
                afficher_pie_chart([df1, df2, df3][int(fichier)-1], colonne)

            elif choix == "8":
                cat1 = input("Colonne catégorielle (X) : ")
                cat2 = input("Colonne de regroupement (couleurs) : ")
                fichier = input("Fichier (1, 2 ou 3) ? ")
                barres_groupées([df1, df2, df3][int(fichier)-1], cat1, cat2)

            elif choix == "9":
                num = input("Colonne numérique : ")
                cat = input("Colonne catégorielle : ")
                fichier = input("Fichier (1, 2 ou 3) ? ")
                afficher_violin_plot([df1, df2, df3][int(fichier)-1], num, cat)

            elif choix == "10":
                fichier = input("Fichier (1, 2 ou 3) ? ")
                creer_heatmap_geographique([df1, df2, df3][int(fichier)-1])

            elif choix == "11":
                jointure_et_visualisation(df1, df2, df3)

            elif choix == "12":
                print("Fin du programme.")
                break

            else:
                print("Choix invalide.")

        except Exception as e:
            print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
