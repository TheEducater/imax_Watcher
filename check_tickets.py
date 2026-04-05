import os
import requests
from bs4 import BeautifulSoup

# Zugangsdaten
token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

def send_msg(text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.get(url, params={"chat_id": chat_id, "text": text})

# 1. Altes Gedächtnis laden
DATEI = "aktuelle_shows.txt"
alte_shows = set()
if os.path.exists(DATEI):
    with open(DATEI, "r", encoding="utf-8") as f:
        alte_shows = set(f.read().splitlines())

# 2. Aktuelle Seite laden
URL = "https://leonberg.traumpalast.de/index.php/PID/11321.html"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

try:
    response = requests.get(URL, headers=headers, timeout=20)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        gefundene_shows = []

        # Suche nach Filmen und Terminen
        movies = soup.select('.movie-list .movie')
        for movie in movies:
            titel_tag = movie.select_one('h3[itemprop="name"]')
            if not titel_tag: continue
            titel = titel_tag.get_text(strip=True)
            
            day_blocks = movie.select('.day-block')
            for block in day_blocks:
                datum_tag = block.select_one('.day-date')
                if not datum_tag: continue
                datum = datum_tag.get_text(strip=True)
                
                zeiten = block.select('time[itemprop="startDate"]')
                for zeit_tag in zeiten:
                    uhrzeit = zeit_tag.get_text(strip=True)
                    gefundene_shows.append(f"{titel} | {datum} | {uhrzeit}")

        # 3. Vergleich: Was ist neu?
        neue_eintraege = [s for s in gefundene_shows
