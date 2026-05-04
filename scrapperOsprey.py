from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

# Lancer Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Ouvrir le site
url = "https://www.osprey.com/backpacks"
driver.get(url)

time.sleep(5)

# Scroll pour charger les produits
for i in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# Récupérer les produits
produits = driver.find_elements(By.CLASS_NAME, "product-tile")

# Créer CSV
with open("osprey_products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Titre", "Prix"])

    for produit in produits:
        try:
            titre = produit.find_element(By.CLASS_NAME, "link").text
            prix = produit.find_element(By.CLASS_NAME, "price").text
            writer.writerow([titre, prix])
        except:
            continue

print("Scraping terminé et données enregistrées dans osprey_products.csv")
driver.quit() 
