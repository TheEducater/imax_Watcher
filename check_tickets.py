import os
import requests
import json

# 1. Zugangsdaten aus dem GitHub-Tresor holen
token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
scraper_key = os.getenv('SCRAPER_API_KEY')

def send_msg(text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.get(url, params={"chat_id": chat_id, "text": text})

# 2. Die Datei laden, in der wir uns die alten Filme gemerkt haben
DATEI = "aktuelle_shows.txt"
alte_shows = set()
if os.path.exists(DATEI):
    with open(DATEI, "r", encoding="utf-8") as f:
        alte_shows = set(f.read().splitlines())

# 3. Den Tunnel (ScraperAPI) nutzen, um die echten JSON-Daten zu holen
# Wir holen den kompletten Spielplan für das ganze Kino!
TARGET_URL = "https://www.kinoheld.de/api/v1/cinemas/2631/shows?format=json"
payload = {'api_key': scraper_key, 'url': TARGET_URL}

try:
    print("Hole aktuellen Spielplan...")
    response = requests.get('http://api.scraperapi.com/', params=payload, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        shows = data.get('shows', [])
        
        # Wir erstellen eine Liste aus Titeln, Datum und Uhrzeit
        aktuelle_liste = []
        for s in shows:
            titel = s.get('name', 'Unbekannt')
            datum = s.get('beginning', {}).get('formatted', 'Kein Datum')
            eintrag = f"{titel} am {datum}"
            aktuelle_liste.append(eintrag)
        
        neue_eintraege = [s for s in aktuelle_liste if s not in alte_shows]

        # 4. Der Vergleich
        if neue_eintraege:
            nachricht = "🚨 NEUE TERMINE GEFUNDEN!\n\n" + "\n".join([f"✅ {n}" for n in neue_eintraege])
            nachricht += "\n\nHier buchen: https://leonberg.traumpalast.de/"
            send_msg(nachricht)
            
            # Jetzt die neue Liste für das nächste Mal speichern
            with open(DATEI, "w", encoding="utf-8") as f:
                f.write("\n".join(aktuelle_liste))
            print(f"{len(neue_eintraege)} neue Shows gefunden.")
        else:
            if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
                send_msg("ℹ️ Check lief: Keine neuen Termine im Vergleich zum letzten Mal gefunden.")
            print("Keine Änderungen.")
            
    else:
        print(f"Fehler: Status {response.status_code}")

except Exception as e:
    print(f"Fehler: {str(e)}")
