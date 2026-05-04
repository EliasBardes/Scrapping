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

# description
        description = ""

#description au json
        try:
            for s in soup_produit.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(s.string)
                except Exception:
                    continue
                # data can be a list or dict
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") and "Product" in item.get("@type"):
                        desc = item.get("description")
                        if desc:
                            description = desc.strip()
                            break
                if description:
                    break
        except Exception:
            pass

#meta description
        if not description:
            meta_desc = soup_produit.find("meta", {"name": "description"})
            if meta_desc:
                description = meta_desc.get("content", "").strip()

#  classes courantes
        if not description:
            for classe in ["description", "product-description", "short-description", "product-short-description", "product-details"]:
                el = soup_produit.find(class_=classe)
                if el:
                    description = el.get_text(" ", strip=True)
                    break

# premier <p> important
        if not description:
            for p in soup_produit.find_all("p"):
                texte = p.get_text(" ", strip=True)
                if len(texte) > 60:
                    description = texte
                    break

# idproduit = sku si trouvé, sinon sera basé sur l'url
        idproduit = ""
        for i in range(len(lignes_propres)):
            if lignes_propres[i] == "SKU":
                if i + 1 < len(lignes_propres):
                    idproduit = lignes_propres[i + 1]
                    break

        if idproduit == "":
            morceau = lien_produit.split("/")[-1]
            idproduit = morceau.replace(".html", "")

        # ne pas ajouter les faux résultats
        if nom != "" and prix != "":
            produit = {
                "idcategorie": idcategorie,
                "nomcategorie": nom_categorie,
                "urlcategorie": urlcategorie,
                "idproduit": idproduit,
                "nom": nom,
                "prix": prix,
                "urlproduit": lien_produit,
                "description": description,
                "imageurl": imageurl,
                "datescraping": datescraping
            }

            donnees.append(produit)
            print("Ajouté :", nom)

        time.sleep(1)

    except Exception as e:
        print("Erreur avec", lien_produit)
        print(e)

df = pd.DataFrame(donnees)

df = df.drop_duplicates(subset=["urlproduit"])

df.to_csv("gregory_client.csv", index=False, encoding="utf-8-sig")

print("Fichier CSV créé : gregory_client.csv")
print(df.head())
print("Nombre total de produits :", len(df))