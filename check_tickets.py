import os
import requests
from bs4 import BeautifulSoup

token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

def send_msg(text):
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage", params={"chat_id": chat_id, "text": text})

# 1. Gedächtnis laden
DATEI = "aktuelle_shows.txt"
alte_shows = set()
if os.path.exists(DATEI):
    with open(DATEI, "r", encoding="utf-8") as f:
        alte_shows = set(f.read().splitlines())

# 2. Seite laden
URL = "https://leonberg.traumpalast.de/index.php/PID/11321.html"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

try:
    response = requests.get(URL, headers=headers, timeout=20)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        gefundene_shows = []

        # Wir suchen alle Film-Blöcke
        movies = soup.select('.movie-list .movie')
        for movie in movies:
            titel = movie.select_one('h3[itemprop="name"]').get_text(strip=True)
            
            # Für jeden Film suchen wir die Tage
            day_blocks = movie.select('.day-block')
            for block in day_blocks:
                datum = block.select_one('.day-date').get_text(strip=True)
                
                # In jedem Tag suchen wir die Uhrzeiten
                zeiten = block.select('time[itemprop="startDate"]')
                for zeit_tag in zeiten:
                    uhrzeit = zeit_tag.get_text(strip=True)
                    # Eintrag erstellen: "Filmname | Datum | Uhrzeit"
                    gefundene_shows.append(f"{titel} | {datum} | {uhrzeit}")

        # 3. Vergleich
        neue_eintraege = [s for s in gefundene_shows if s not in alte_shows]

        if neue_eintraege:
            nachricht = "🚨 NEUE TICKETS GEFUNDEN!\n\n" + "\n".join([f"✅ {n}" for n in neue_eintraege[:20]])
            if len(neue_eintraege) > 20: nachricht += "\n..."
            nachricht += f"\n\nLink: {URL}"
            send_msg(nachricht)
            
            with open(DATEI, "w", encoding="utf-8") as f:
                f.write("\n".join(gefundene_shows))
        else:
            if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
                send_msg(f"✅ Check lief perfekt. Keine neuen Shows im Vergleich zum letzten Mal (Aktuell: {len(gefundene_shows)} Vorstellungen).")
    else:
        if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
            send_msg(f"❌ Fehler: Seite meldet Status {response.status_code}")

except Exception as e:
    if os.getenv('GITHUB_EVENT_NAME') == "workflow_dispatch":
        send_msg(f"❌ Technischer Fehler: {str(e)}")
