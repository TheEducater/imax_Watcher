import requests
import os
from datetime import datetime, timedelta

# 1. Datum berechnen (nächster Freitag)
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
ziel_datum = (heute + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

# 2. Die Adresse (Wir nutzen den "Public" Endpunkt von Kinoheld)
CINEMA_ID = "2631" # Leonberg
# Wir nutzen hier den Endpoint, der oft für Widgets verwendet wird - der ist meistens offen
url = f"https://www.kinoheld.de/api/v1/cinemas/{CINEMA_ID}/shows?format=json"

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Referer': 'https://www.kinoheld.de/'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        # Falls v1 nicht geht, probieren wir einen alternativen Pfad
        url = f"https://api.kinoheld.de/v2/cinemas/{CINEMA_ID}/shows"
        response = requests.get(url, headers=headers, timeout=10)

    data = response.json()
    # Kinoheld verschachtelt die Daten manchmal in 'shows' oder 'data'
    shows = data.get('shows', data.get('data', []))

    gefundene_filme = []
    for show in shows:
        # Wir prüfen das Datum. Kinoheld liefert oft "2026-04-10"
        show_date = show.get('beginning', {}).get('date', '')
        if show_date == ziel_datum:
            titel = show.get('name', 'Unbekannter Film')
            if titel not in gefundene_filme:
                gefundene_filme.append(titel)

    # 3. Ergebnis senden
    if gefundene_filme:
        film_liste = "\n✅ " + "\n✅ ".join(gefundene_filme)
        msg = f"🚨 TICKETS DA! ({ziel_datum})\n\n{film_liste}\n\nLink: https://leonberg.traumpalast.de/"
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}")
    
    elif os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        msg = f"✅ Verbindung zu Kinoheld steht! \n\nFür Freitag ({ziel_datum}) sind aber aktuell noch keine Tickets im System von Leonberg."
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}")

except Exception as e:
    # Nur bei manuellem Test Fehler senden, um nicht jeden Montag Fehlalarme zu kriegen
    if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text=❌ Fehler: {str(e)}")
    print(f"Fehler: {e}")
