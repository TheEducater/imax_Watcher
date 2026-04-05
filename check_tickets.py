import requests
import os
from datetime import datetime, timedelta

# 1. Datum berechnen
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
naechster_freitag = (heute + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')

# Umgebungsvariablen (Tresor)
token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
# GitHub sagt uns, ob wir den Bot manuell gestartet haben
event_name = os.getenv('GITHUB_EVENT_NAME')

# 2. Kinoheld API abrufen (Leonberg ID: 2631)
CINEMA_ID = "2631"
url = f"https://www.kinoheld.de/api/v1/cinemas/{CINEMA_ID}/shows"

try:
    response = requests.get(url).json()
    shows = response.get('shows', [])

    gefundene_filme = []
    for show in shows:
        if show['beginning']['date'] == naechster_freitag:
            titel = show['name']
            if titel not in gefundene_filme:
                gefundene_filme.append(titel)

    # 3. Logik für die Nachricht
    if gefundene_filme:
        film_liste = "\n✅ " + "\n✅ ".join(gefundene_filme)
        msg = f"🚨 TICKETS DA für Freitag ({naechster_freitag})!\n\nFilme:{film_liste}\n\nSchnell sein! 🎟️"
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}")
    
    # NEU: Wenn du manuell auf "Run" klickst, aber keine Filme da sind:
    elif event_name == "workflow_dispatch":
        msg = f"✅ Test erfolgreich! Der Bot ist bereit.\n\nFür Freitag ({naechster_freitag}) sind aber aktuell noch keine Tickets im System von Leonberg online."
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}")
        print("Manuelle Test-Nachricht gesendet.")

except Exception as e:
    print(f"Fehler: {e}")
    
