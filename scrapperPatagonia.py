
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import csv

categories = {
    "Bags": "https://www.patagonia.com/shop/gear/bags"
}


session = HTMLSession()


with open("inventaire_patagonia.csv", "w", newline="", encoding="utf-8") as fichier:
    writer = csv.writer(fichier)
    writer.writerow(["Catégorie", "Titre", "Prix", "Disponibilité"])

    for nom_cat, url in categories.items():
        print(f"Scraping : {nom_cat}")
        
        try:
            response = session.get(url)
            
        
            response.html.render(sleep=5)

            soup = BeautifulSoup(response.html.html, "html.parser")
            produits = soup.find_all("div", class_="product-tile")

            for produit in produits:
                try:
                    # titre
                    titre = produit.find("a").get_text(strip=True)

                   
                    prix_el = produit.find("span", class_="price")
                    prix = prix_el.get_text(strip=True) if prix_el else "N/A"

                    dispo = "En stock"

                    writer.writerow([nom_cat, titre, prix, dispo])

                except:
                    pass

            print(f"{len(produits)} produits trouvés")

        except Exception as e:
            print(f"Erreur : {e}")

print("\n" + "="*30)
print("Le fichier CSV Patagonia est prêt ")