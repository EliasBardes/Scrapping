import requests
from bs4 import BeautifulSoup
import json

def scrape_osprey_categories_and_products(base_url="https://www.osprey.com/fr/sacs-a-dos-sacs"):
    """
    Scrape product categories and initial product listings from the Osprey website.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    print(f"Scraping categories and products from: {base_url}")
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return {}, []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract Categories (from the filter section)
    categories = {}
    # Look for 'Activité' or similar filter that acts as a category
    activity_filter = soup.find('div', string='Activité')
    if not activity_filter:
        activity_filter = soup.find('div', string=lambda x: x and 'Activité' in x)
        
    if activity_filter:
        activity_list = activity_filter.find_next('ul')
        if activity_list:
            for li in activity_list.find_all('li'):
                label = li.find('label')
                if label:
                    cat_name = label.text.strip().split('(')[0].strip()
                    cat_id = cat_name.lower().replace(' ', '_')
                    categories[cat_id] = {'id': cat_id, 'name': cat_name, 'url': None}

    # Extract Products from the listing page
    products = []
    product_items = soup.find_all('li', class_='item product product-item')
    for item in product_items:
        product_data = {}
        product_data['id_produit'] = item.get('data-product-id')
        link_tag = item.find('a', class_='product-item-link')
        product_data['nom'] = link_tag.text.strip() if link_tag else None
        
        price_span = item.find('span', class_='price')
        if price_span:
            price_text = price_span.text.strip().replace('€', '').replace(',', '.').replace('\xa0', '').replace(' ', '')
            try:
                product_data['prix'] = float(price_text)
            except ValueError:
                product_data['prix'] = None
        else:
            product_data['prix'] = None

        product_data['url_produit'] = link_tag['href'] if link_tag else None
        img_tag = item.find('img', class_='product-image-photo')
        product_data['image_url'] = img_tag['src'] if img_tag else None
        
        product_data['description'] = None
        product_data['note'] = None
        product_data['disponibilite'] = 'In Stock'
        product_data['volume_litres'] = None
        product_data['poids_kg'] = None
        product_data['date_scraping'] = '2026-05-05'
        product_data['id_categorie'] = None
        product_data['id_serie'] = None

        products.append(product_data)

    return categories, products

def scrape_product_detail(product_url):
    """
    Scrape detailed information from a single product page.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    print(f"Scraping product detail from: {product_url}")
    response = requests.get(product_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve product page: {response.status_code}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    details = {}

    description_div = soup.find('div', id='description')
    if description_div:
        details['description'] = description_div.get_text(strip=True)
    
    spec_table = soup.find('div', id='product.attributes')
    if spec_table:
        specs = {}
        for row in spec_table.find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) == 2:
                key = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                specs[key] = value
        details['specifications'] = specs

    return details

if __name__ == "__main__":
    categories, products = scrape_osprey_categories_and_products()
    
    # If products list is empty, try a different approach or log it
    if not products:
        print("No products found. The site might be using dynamic loading or different classes.")
    
    print("\n--- Categories ---")
    for cat_id, cat_info in categories.items():
        print(f"ID: {cat_id}, Name: {cat_info['name']}")

    print("\n--- Sample Products ---")
    for i, product in enumerate(products[:5]):
        print(f"Product {i+1}: {product['nom']} - {product['prix']}€")
        if i == 0 and product['url_produit']:
            product_details = scrape_product_detail(product['url_produit'])
            product.update(product_details)

    with open('osprey_categories.json', 'w', encoding='utf-8') as f:
        json.dump(list(categories.values()), f, ensure_ascii=False, indent=4)
    with open('osprey_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    print("\nData saved to osprey_categories.json and osprey_products.json")
