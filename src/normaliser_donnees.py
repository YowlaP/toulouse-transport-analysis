import csv
import sys 
input_file = sys.argv[1]  # Remplace par le chemin exact de ton fichier d'entrée

###############################################
# 1. Génération du fichier communes.csv
###############################################

communes_output = "fichier1.csv"
unique_communes = []  # Liste pour stocker les communes uniques (dictionnaires)
communes_seen = set() # Pour éviter les doublons

with open(input_file, mode='r', encoding='utf-8', newline='') as infile:
    reader = csv.DictReader(infile, delimiter=';')
    if "Code commune" not in reader.fieldnames or "commune" not in reader.fieldnames:
        raise KeyError("Le fichier d'entrée doit contenir les colonnes 'Code commune' et 'commune'.")
    for row in reader:
        code_commune = row["Code commune"].strip()
        commune = row["commune"].strip()
        # On ajoute uniquement si aucune des deux données n'est vide
        if code_commune and commune and code_commune not in communes_seen:
            communes_seen.add(code_commune)
            unique_communes.append({"Code commune": code_commune, "commune": commune})
        if len(unique_communes) == 6:
            break

with open(communes_output, mode='w', encoding='utf-8', newline='') as outfile:
    fieldnames = ["Code commune", "commune"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    writer.writerows(unique_communes)

print(f"✅ Fichier '{communes_output}' généré avec succès avec {len(unique_communes)} communes.")

###############################################
# 2. Génération du fichier types_transport.csv
###############################################

types_output = "fichier2.csv"
unique_types = []  # Liste pour stocker les types de transport uniques
types_seen = set()

with open(input_file, mode='r', encoding='utf-8', newline='') as infile:
    reader = csv.reader(infile, delimiter=';')
    header = next(reader)  # Ignorer l'en-tête
    # On suppose que la 6ᵉ colonne (index 5) est le code type et la 7ᵉ (index 6) est le type
    for row in reader:
        if len(row) < 7:
            continue
        code_type = row[5].strip()
        type_value = row[6].strip()
        # Exclure les lignes où l'une des deux données est vide
        if not code_type or not type_value:
            continue
        if code_type not in types_seen:
            types_seen.add(code_type)
            unique_types.append([code_type, type_value])
        if len(unique_types) == 18:
            break

with open(types_output, mode='w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile, delimiter=';')
    writer.writerow(["Code type", "type"])
    writer.writerows(unique_types)

print(f"✅ Fichier '{types_output}' généré avec succès avec {len(unique_types)} types de transport.")

###############################################
# 3. Génération du fichier arrets.csv
###############################################

arrets_output = "fichier3.csv"
# Indices des colonnes à extraire pour le fichier arrets
selected_indices = [5, 10, 0, 1, 2, 3, 4, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18]
output_header = [
    "code_type", "code_commune", "geo point", "geo shape", "infobulle", "nom", "ligne",
    "en_service", "couvert", "etiquette", "num_sation", "nb_bornettes", "rue",
    "mot_directeur", "No", "locations_2016", "nb_places"
]

with open(input_file, mode='r', encoding='utf-8', newline='') as infile, \
     open(arrets_output, mode='w', encoding='utf-8', newline='') as outfile:
    
    reader = csv.reader(infile, delimiter=';')
    writer = csv.writer(outfile, delimiter=';')
    
    # Lire et ignorer l'en-tête du fichier d'entrée
    header = next(reader)
    writer.writerow(output_header)
    
    for row in reader:
        if len(row) < max(selected_indices) + 1:
            continue
        new_row = [row[i].strip() for i in selected_indices]
        writer.writerow(new_row)

print(f"✅ Fichier '{arrets_output}' généré avec succès avec toutes les lignes d'arrêts.")