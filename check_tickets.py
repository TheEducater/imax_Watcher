import requests
import os
from datetime import datetime, timedelta

# 1. Nächsten Freitag berechnen (z.B. 10.04.2026)
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
ziel_datum = (heute + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

# 2. Die JSON-API-URL direkt von Kinoheld (ID 2631 = Leonberg)
URL = "https://www.kinoheld.de/api/v1/cinemas/2631/shows?format=json"

# WICHTIG: Die "Tarnung", damit Kinoheld uns nicht blockt
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://leonberg.traumpalast.de/', # Das ist der "Ausweis"
    'Accept': 'application/json'
}

def send_msg(text):
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}")

try:
    # Den Jason (JSON) abrufen
    response = requests.get(URL, headers=headers, timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        shows = data.get('shows', [])
        
        gefundene_filme = []
        for show in shows:
            # Wir prüfen das Datum im JSON
            if show.get('beginning', {}).get('date') == ziel_datum:
                titel = show.get('name')
                uhrzeit = show.get('beginning', {}).get('time', '')
                if titel:
                    gefundene_filme.append(f"{titel} um {uhrzeit}")

        if gefundene_filme:
            film_liste = "\n✅ " + "\n✅ ".join(gefundene_filme)
            send_msg(f"🚨 TICKETS DA für {ziel_datum}!\n{film_liste}\n\nLink: https://leonberg.traumpalast.de/")
        elif os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"✅ JSON-Check erfolgreich! Verbindung steht, aber für {ziel_datum} sind noch keine Filme im System.")
            
    else:
        # Falls doch ein Fehler kommt, schick uns den Status-Code
        if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"❌ Kinoheld meldet Fehler-Code: {response.status_code}")

except Exception as e:
    if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        send_msg(f"❌ Technischer Fehler: {str(e)}")
