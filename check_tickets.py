import requests
import os
from datetime import datetime, timedelta

# 1. Das Datum für den nächsten Freitag automatisch berechnen
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7 # Wenn heute Freitag ist, nimm den nächsten
naechster_freitag = (heute + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')

# 2. Kinoheld API für IMAX Leonberg (ID: 2631) abrufen
CINEMA_ID = "2631"
url = f"https://www.kinoheld.de/api/v1/cinemas/{CINEMA_ID}/shows"

try:
    response = requests.get(url).json()
    shows = response.get('shows', [])

    # 3. Prüfen, ob für diesen Freitag schon Vorstellungen existieren
    gefunden = False
    for show in shows:
        if show['beginning']['date'] == naechster_freitag:
            gefunden = True
            break

    # 4. Wenn gefunden, schick die Nachricht über deinen Bot
    if gefunden:
        token = os.getenv('TELEGRAM_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        nachricht = f"🚨 TICKETS DA! IMAX Leonberg hat Vorstellungen für Freitag ({naechster_freitag}) veröffentlicht! 🎟️"
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={nachricht}")
        print(f"Tickets für {naechster_freitag} gefunden!")
    else:
        print(f"Noch keine Tickets für {naechster_freitag}.")

except Exception as e:
    print(f"Fehler beim Abrufen: {e}")
  
