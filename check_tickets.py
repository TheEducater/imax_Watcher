import requests
import os
from datetime import datetime, timedelta

# 1. Nächsten Freitag berechnen
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
naechster_freitag = heute + timedelta(days=tage_bis_freitag)

# Wir suchen nach der kurzen Schreibweise, die Kinoheld meist nutzt (z.B. "10.04.")
such_datum = naechster_freitag.strftime('%d.%m.') 

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

# 2. Das direkte Kinoheld-Widget für Leonberg (Kein API-Stress mehr!)
URL = "https://www.kinoheld.de/widget/cinema/2631/shows/list"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
}

def send_msg(text):
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}")

try:
    # Den Quelltext des eingebetteten Widgets laden
    response = requests.get(URL, headers=headers, timeout=15)
    
    if response.status_code == 200:
        html_text = response.text
        
        # 3. Wir suchen einfach stumpf nach dem Datum im Text
        if such_datum in html_text:
            msg = f"🚨 TICKETS DA! Im IMAX Leonberg sind Vorstellungen für Freitag ({such_datum}) aufgetaucht!\n\nLink: https://leonberg.traumpalast.de/"
            send_msg(msg)
        else:
            # Nur bei manuellem Klick bei GitHub:
            if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
                send_msg(f"✅ Widget-Check läuft! Für Freitag ({such_datum}) ist noch nichts gelistet.")
    else:
        if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"❌ Kinoheld blockt das Widget (Status {response.status_code})")

except Exception as e:
    if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        send_msg(f"❌ Technischer Fehler: {str(e)}")
