import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

# 1. LANCEMENT DU NAVIGATEUR
print("Lancement du navigateur furtif...")
options = uc.ChromeOptions()
driver = uc.Chrome(options=options, version_main=147)

try:
    # 2. NAVIGATION
    print("Navigation vers l'accueil Arc'teryx...")
    url = "https://www.arcteryx.com/fr/fr"
    driver.get(url)

    # --- GESTION DES COOKIES ---
    print("Recherche de la bannière de cookies...")
    try:
        bouton_cookie = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), \"J'accepte\")]"))
        )
        bouton_cookie.click()
        print("🍪 Cookies acceptés !")
        time.sleep(2) 
    except Exception:
        print("Pas de bannière de cookies.")

    # --- RECHERCHE ---
    print("🔍 Clic sur la loupe de recherche...")
    bouton_loupe = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'earch') or contains(@aria-label, 'echerch') or contains(@class, 'search')]"))
    )
    bouton_loupe.click()
    time.sleep(1)

    print("⌨️ Frappe du texte 'sac a dos'...")
    champ_texte = driver.find_element(By.XPATH, "//input[@type='search' or contains(@placeholder, 'echerch') or contains(@name, 'search')]")
    champ_texte.send_keys("sac a dos")
    champ_texte.send_keys(Keys.ENTER)

    # --- ATTENTE DES RÉSULTATS ---
    print("Attente des produits...")
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ais-Hits-item")))
    print("✅ Les produits sont chargés à l'écran !")

    # --- NOUVEAU : SCROLL POUR LE LAZY LOADING ---
    print("📜 Défilement de la page pour charger tous les sacs...")
    # On scroll en 3 fois pour être sûr que le site détecte le mouvement
    for i in range(1, 4):
        driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * ({i}/3));")
        time.sleep(1.5)

    # 3. EXTRACTION AVEC BEAUTIFULSOUP
    soup = BeautifulSoup(driver.page_source, "html.parser")
    sacs = soup.find_all("li", class_="ais-Hits-item")
    
    print(f"\n--- DÉBUT DE L'EXTRACTION ({len(sacs)} sacs trouvés) ---\n")

    for sac in sacs:
        # TITRE : On utilise la classe que tu as trouvée dans l'inspecteur !
        balise_titre = sac.find(class_="product-tile-name")
        if balise_titre:
            titre = balise_titre.text.strip()
        else:
            titre = "Titre introuvable"

        # PRIX
        tout_le_texte = sac.get_text(separator="|").strip()
        prix = "Prix non affiché"
        for ligne in tout_le_texte.split("|"):
            if "€" in ligne:
                prix = ligne.strip()
                break 

        # NOTE ET DISPO
        note = "N/A"
        dispo = "Voir fiche produit"

        print(f"Titre : {titre}")
        print(f"Prix  : {prix}")
        print(f"Note  : {note}")
        print("-" * 40)

except Exception as e:
    print(f"\n❌ Erreur : Le script a rencontré un problème.")
    print(f"Détail : {e}")

finally:
    # 4. FERMETURE
    print("\n--- FIN DU SCRIPT ---")
    driver.quit()