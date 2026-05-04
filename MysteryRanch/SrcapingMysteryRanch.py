import requests
from bs4 import BeautifulSoup
import csv

categories = {
    "Everyday": "https://www.mysteryranch.com/Packs/Everyday-Carry",
    "Hunting": "https://www.mysteryranch.com/Packs/Hunting", 
    "Military": "https://www.mysteryranch.com/Packs/Military"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Préparation du fichier CSV
with open("inventaire_final_ranch.csv", "w", newline="", encoding="utf-8") as fichier:
    writer = csv.writer(fichier)
    writer.writerow(["Catégorie", "Titre", "Prix", "Note", "Disponibilité"])

    for nom_cat, url in categories.items():
        print(f" Scraping : {nom_cat}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200: continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            produits = soup.find_all("div", class_="facets-item-cell-grid")
            
            for produit in produits:
                # Titre et Prix
                titre = produit.find("div", class_="facets-item-cell-grid-title").text.strip()
                prix_el = produit.find("span", class_="product-views-price-lead")
                prix = prix_el.text.strip() if prix_el else "N/A"
                
                # Note 
                note_el = produit.find("div", class_="bv-off-screen")
                note = note_el.text.strip() if note_el else "Note masquée (JS)"
                
                dispo = "En stock" 
                
                writer.writerow([nom_cat, titre, prix, note, dispo])
            
            print(f" {len(produits)} produits pour {nom_cat}")

        except Exception as e:
            print(f"Erreur sur {nom_cat} : {e}")

print("\n" + "="*30)
print("Le fichier CSV est readyyyyyyy")