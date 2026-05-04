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

