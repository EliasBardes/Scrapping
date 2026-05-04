import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import re
import time

headers = {
    "User-Agent": "Mozilla/5.0"
}

url_categorie = "https://eu.gregorypacks.com/fr-fr/shopping-par-activite/sacs-a-dos/"

response = requests.get(url_categorie, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# setup les nom de la catégorie
nom_categorie = "Sacs à dos"
urlcategorie = url_categorie
idcategorie = "cat_sacs_a_dos"

# récupération des liens produits
liens = soup.find_all("a", href=True) 

liste_liens_produits = []

for lien in liens:
    href = lien["href"]

    if href.startswith("/"):
        href = "https://eu.gregorypacks.com" + href

    # on garde seulement les liens qui ressemblent à des pages produit
    if "/fr-fr/" in href and ".html" in href:
        if re.search(r"\d+-[A-Za-z0-9]+\.html", href):
            if href not in liste_liens_produits:
                liste_liens_produits.append(href)




# prépare une liste vide pour produit
donnees = []

for lien_produit in liste_liens_produits:
    try:
        print("Je scrape : ", lien_produit)

        response_produit = requests.get(lien_produit, headers=headers)
        soup_produit = BeautifulSoup(response_produit.text, "html.parser")

        texte_page = soup_produit.get_text("\n")
        lignes = texte_page.split("\n")

        lignes_propres = []
        for ligne in lignes:
            ligne = ligne.strip()
            if ligne != "":
                lignes_propres.append(ligne)

        # nom produit
        nom = ""
        for ligne in lignes_propres:
            if "Sac à dos" in ligne or "Housse" in ligne or "Accessoire" in ligne or "Sac banane" in ligne:
                nom = ligne
                break

        # prix
        prix = ""
        for ligne in lignes_propres:
            if "€" in ligne:
                prix = ligne
                break

        # nettoyage  prix
        resultat_prix = re.search(r"(\d+[,.]\d+|\d+)", prix)
        if resultat_prix:
            prix = resultat_prix.group(1).replace(",", ".")
        else:
            prix = ""

    except