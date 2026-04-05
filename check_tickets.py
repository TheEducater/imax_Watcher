import os
import requests
import re

# 1. Zugangsdaten
token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

def send_msg(text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.get(url, params={"chat_id": chat_id, "text": text})

# 2. Gedächtnis laden
DATEI = "aktuelle_shows.txt"
alte_shows = set()
if os.path.exists(DATEI):
    with open(DATEI, "r", encoding="utf-8") as f:
        alte_shows = set(f.read().splitlines())

# 3. Traumpalast direkt anklopfen (ohne ScraperAPI)
URL = "https://leonberg.traumpalast.de/index.php/PID/11321.html"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

try:
    response = requests.get(URL, headers=headers, timeout=15)
    if response.status_code == 200:
        html = response.text
        
        # Wir suchen nach Uhrzeiten (z.B. "20:00 Uhr")
        # Das verhindert Fehlalarme durch leere Kalender-Daten
        funde = re.findall(r'(\d{2}:\d{2})\s*Uhr', html)
        
        # Wir merken uns einfach, wie viele Uhrzeiten auf der Seite stehen
        aktuelle_anzahl = len(funde)
        
        # 4. Vergleich
        # Wir speichern die Anzahl als "Zustand"
        anzahl_alt = "0"
        if os.path.exists("anzahl.txt"):
            with open("anzahl.txt", "r") as f: anzahl_alt = f.read().strip()

        if aktuelle_anzahl > 0 and str(aktuelle_anzahl) != anzahl_alt:
            msg = f"🚨 TICKETS AKTIV! Es wurden {aktuelle_anzahl} Vorstellungen im IMAX gefunden!\n\nLink: {URL}"
            send_msg(msg)
            
            with open("anzahl.txt", "w") as f: f.write(str(aktuelle_anzahl))
        else:
            if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
                send_msg(f"✅ Check lief: Seite geladen, aber noch keine aktiven Uhrzeiten gefunden ({aktuelle_anzahl} Shows).")
    else:
        if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"❌ Traumpalast blockt GitHub jetzt doch (Status {response.status_code})")

except Exception as e:
    if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        send_msg(f"❌ Fehler: {str(e)}")
