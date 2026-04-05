import os
import requests
from datetime import datetime, timedelta

# 1. Datum berechnen
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
ziel_datum = (heute + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
scraper_key = os.getenv('SCRAPER_API_KEY')

def send_msg(text):
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage", params={"chat_id": chat_id, "text": text})

# 2. Das Gedächtnis des Bots laden
DATEI = "alte_filme.txt"
alte_filme = []
if os.path.exists(DATEI):
    with open(DATEI, "r", encoding="utf-8") as f:
        alte_filme = f.read().splitlines()

# 3. Der Tunnel (ScraperAPI)
# Wir sagen dem Tunnel, er soll unsere Ziel-URL für uns abrufen
TARGET_URL = "https://www.kinoheld.de/api/v1/cinemas/2631/shows?format=json"
tunnel_url = f"http://api.scraperapi.com/?api_key={scraper_key}&url={TARGET_URL}"

try:
    print("Rufe Daten über den Tunnel ab...")
    # Timeout etwas höher, da der Weg durch den Tunnel minimal länger dauert
    response = requests.get(tunnel_url, timeout=30) 
    
    if response.status_code == 200:
        data = response.json()
        shows = data.get('shows', [])
        
        aktuelle_filme = []
        for show in shows:
            if show.get('beginning', {}).get('date') == ziel_datum:
                titel = show.get('name')
                uhrzeit = show.get('beginning', {}).get('time', '')
                if titel:
                    aktuelle_filme.append(f"{titel} um {uhrzeit} Uhr")
        
        # 4. Der Vergleich: Was ist neu?
        neue_filme = [film for film in aktuelle_filme if film not in alte_filme]

        if neue_filme:
            film_liste = "\n✅ " + "\n✅ ".join(neue_filme)
            send_msg(f"🚨 NEUE TICKETS für Freitag ({ziel_datum})!\n{film_liste}\n\nLink: https://leonberg.traumpalast.de/")
            
            # Notizbuch aktualisieren
            with open(DATEI, "w", encoding="utf-8") as f:
                f.write("\n".join(aktuelle_filme))
        
        elif os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"✅ Tunnel-Check lief. Keine NEUEN Filme für {ziel_datum} dazugekommen.")
            
    else:
        if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"❌ Der Tunnel meldet einen Fehler: Status {response.status_code}")

except Exception as e:
    if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        send_msg(f"❌ Technischer Fehler im Tunnel: {str(e)}")
