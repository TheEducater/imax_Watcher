import requests
import os
from datetime import datetime, timedelta

# 1. Datum berechnen
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
naechster_freitag = (heute + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
event_name = os.getenv('GITHUB_EVENT_NAME')

# 2. Die Verkleidung (User-Agent)
# Damit sieht der Bot für die Webseite wie ein echter Chrome-Browser aus
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

CINEMA_ID = "2631"
url = f"https://www.kinoheld.de/api/v1/cinemas/{CINEMA_ID}/shows"

try:
    # Wir schicken die Anfrage mit der "Verkleidung" (headers)
    response = requests.get(url, headers=headers)
    
    # Prüfen ob die Antwort ok ist (Status 200)
    if response.status_code != 200:
        raise Exception(f"Kinoheld blockiert uns (Status {response.status_code})")

    data = response.json()
    shows = data.get('shows', [])

    gefundene_filme = []
    for show in shows:
        if show['beginning']['date'] == naechster_freitag:
            titel = show['name']
            if titel not in gefundene_filme:
                gefundene_filme.append(titel)

    # 3. Nachricht senden
    if gefundene_filme:
        film_liste = "\n✅ " + "\n✅ ".join(gefundene_filme)
        msg = f"🚨 TICKETS DA! ({naechster_freitag})\n\n{film_liste}\n\nSchnell sein! 🎟️"
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}")
    
    elif event_name == "workflow_dispatch":
        msg = f"✅ Verbindung steht! Bot ist bereit.\n\nFür Freitag ({naechster_freitag}) sind aber aktuell noch keine Tickets online."
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}")

except Exception as e:
    # Wenn ein Fehler passiert, schick ihn direkt zu Telegram
    error_msg = f"❌ Bot-Fehler: {e}"
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={error_msg}")
    print(f"Fehler: {e}")
