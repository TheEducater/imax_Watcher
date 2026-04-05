import requests
import os
from datetime import datetime, timedelta

# 1. Welches Datum suchen wir? (Nächster Freitag)
heute = datetime.now()
# Rechnet aus, wie viele Tage es bis zum nächsten Freitag sind
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
ziel_datum = (heute + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

# 2. Die JSON-Schnittstelle von Kinoheld für Leonberg (ID 2631)
URL = "https://www.kinoheld.de/api/v1/cinemas/2631/shows?format=json"

# Tarnung als Browser, damit wir nicht blockiert werden
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://leonberg.traumpalast.de/',
    'Accept': 'application/json'
}

def send_msg(text):
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}")

try:
    # Den Spielplan abrufen
    response = requests.get(URL, headers=headers, timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        shows = data.get('shows', [])
        
        gefundene_filme = []
        for show in shows:
            # Wir schauen, ob Vorstellungen für unseren Freitag im JSON stehen
            if show.get('beginning', {}).get('date') == ziel_datum:
                titel = show.get('name')
                uhrzeit = show.get('beginning', {}).get('time', '')
                if titel:
                    gefundene_filme.append(f"{titel} um {uhrzeit} Uhr")

        # 3. Die Entscheidung
        if gefundene_filme:
            # Wenn Filme da sind: Alarm schlagen!
            film_liste = "\n✅ " + "\n✅ ".join(gefundene_filme)
            send_msg(f"🚨 TICKETS DA für Freitag ({ziel_datum})!\n{film_liste}\n\nSchnell sein: https://leonberg.traumpalast.de/")
        elif os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            # Wenn du manuell testest, kriegst du eine Status-Bestätigung
            send_msg(f"✅ Verbindung steht! Für Freitag ({ziel_datum}) sind aktuell noch keine Tickets im System.")
            
    else:
        # Falls die API mal zickt
        if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"❌ Kinoheld meldet Fehler: {response.status_code}")

except Exception as e:
    if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        send_msg(f"❌ Technischer Fehler: {str(e)}")
