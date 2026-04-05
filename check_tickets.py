import cloudscraper
import os
from datetime import datetime, timedelta

# 1. Datum berechnen
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
ziel_datum = (heute + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

def send_msg(text):
    import requests
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage", params={"chat_id": chat_id, "text": text})

# 2. Das Gedächtnis des Bots (Notizbuch laden)
DATEI = "alte_filme.txt"
alte_filme = []
if os.path.exists(DATEI):
    with open(DATEI, "r", encoding="utf-8") as f:
        alte_filme = f.read().splitlines()

# 3. Der VIP-Pass für die JSON-Daten (umgeht den 404-Blocker)
scraper = cloudscraper.create_scraper()
URL = "https://www.kinoheld.de/api/v1/cinemas/2631/shows?format=json"

try:
    response = scraper.get(URL, timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        shows = data.get('shows', [])
        
        aktuelle_filme = []
        for show in shows:
            # Hier prüfen wir im echten System, ob die Filme da sind!
            if show.get('beginning', {}).get('date') == ziel_datum:
                titel = show.get('name')
                uhrzeit = show.get('beginning', {}).get('time', '')
                if titel:
                    aktuelle_filme.append(f"{titel} um {uhrzeit} Uhr")
        
        # 4. Der Vergleich: Was ist WIRKLICH neu?
        neue_filme = [film for film in aktuelle_filme if film not in alte_filme]

        if neue_filme:
            film_liste = "\n✅ " + "\n✅ ".join(neue_filme)
            send_msg(f"🚨 NEUE TICKETS für Freitag ({ziel_datum})!\n{film_liste}\n\nLink: https://leonberg.traumpalast.de/")
            
            # Das Notizbuch aktualisieren und für GitHub speichern
            with open(DATEI, "w", encoding="utf-8") as f:
                f.write("\n".join(aktuelle_filme))
        
        elif os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"✅ Check lief. Keine NEUEN Filme für {ziel_datum} dazugekommen.")
            
    else:
        if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"❌ Kinoheld blockt noch immer: Status {response.status_code}")

except Exception as e:
    if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        send_msg(f"❌ Technischer Fehler: {str(e)}")
