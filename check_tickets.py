import requests
import os
from datetime import datetime, timedelta

# 1. Nächsten Freitag berechnen
heute = datetime.now()
tage_bis_freitag = (4 - heute.weekday() + 7) % 7
if tage_bis_freitag == 0: tage_bis_freitag = 7
naechster_freitag = heute + timedelta(days=tage_bis_freitag)

# Such-Formate für Traumpalast (z.B. "10.04.2026" oder "10.04.")
datum_lang = naechster_freitag.strftime('%d.%m.%Y')
datum_kurz = naechster_freitag.strftime('%d.%m.')

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

# 2. Die direkte IMAX Traumpalast Seite (Kein Kinoheld mehr!)
URL = "https://leonberg.traumpalast.de/index.php/PID/11321.html"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
}

def send_msg(text):
    # Sichere Methode, um Text mit Emojis über Telegram zu senden
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.get(url, params={"chat_id": chat_id, "text": text})

try:
    response = requests.get(URL, headers=headers, timeout=15)
    
    if response.status_code == 200:
        html_text = response.text
        
        # 3. Traumpalast-Webseite scannen
        # Sobald Filme da sind, taucht das Datum im Quelltext der Seite auf
        if datum_lang in html_text or datum_kurz in html_text:
            msg = f"🚨 TICKETS DA! Das Datum für Freitag ({datum_lang}) ist auf der IMAX-Webseite aufgetaucht!\n\nDirekt prüfen: {URL}"
            send_msg(msg)
        else:
            if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
                send_msg(f"✅ Traumpalast-Check läuft! Für Freitag ({datum_lang}) ist noch nichts freigeschaltet.")
    else:
        if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"❌ Fehler: Webseite meldet Status {response.status_code}")

except Exception as e:
    if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        send_msg(f"❌ Technischer Fehler: {str(e)}")
