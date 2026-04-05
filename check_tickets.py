import requests
import os
from datetime import datetime, timedelta

# 1. Datum für den nächsten Freitag automatisch berechnen
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
naechster_freitag = (heute + timedelta(days=tage_bis_freitag)).strftime('%Y-%m-%d')

# 2. Kinoheld API für IMAX Leonberg (ID: 2631)
CINEMA_ID = "2631"
url = f"https://www.kinoheld.de/api/v1/cinemas/{CINEMA_ID}/shows"

try:
    response = requests.get(url).json()
    shows = response.get('shows', [])

    # 3. Alle Filme für diesen Freitag sammeln
    gefundene_filme = []
    for show in shows:
        if show['beginning']['date'] == naechster_freitag:
            titel = show['name']
            if titel not in gefundene_filme:
                gefundene_filme.append(titel)

    # 4. Nachricht senden, wenn Filme gefunden wurden
    if gefundene_filme:
        token = os.getenv('TELEGRAM_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Liste der Filme hübsch formatieren
        film_liste = "\n✅ " + "\n✅ ".join(gefundene_filme)
        nachricht = f"🚨 TICKETS DA für Freitag ({naechster_freitag})!\n\nFolgende Filme wurden gefunden:{film_liste}\n\nSchnell sein! 🎟️"
        
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={nachricht}")
        print(f"Tickets gefunden für: {gefundene_filme}")
    else:
        print(f"Noch keine Tickets für {naechster_freitag} online.")

except Exception as e:
    print(f"Fehler: {e}")
    
