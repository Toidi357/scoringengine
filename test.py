import requests 
from bs4 import BeautifulSoup

def parse_dashboard(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = []

    # Target the table body rows
    rows = soup.select('tbody tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 4:
            continue

        # 1. Extract Service Name
        service_name = cols[0].text.strip()

        # 2. Extract Host
        host = cols[1].find('code').text.strip() if cols[1].find('code') else "---"

        # 3. Extract Current Status
        status_badge = cols[2].find('span', class_='status-badge')
        current_status = "UNKNOWN"
        if status_badge:
            # Check for 'status-up' or 'status-down' in the class list
            classes = status_badge.get('class', [])
            if 'status-up' in classes:
                current_status = "UP"
            elif 'status-down' in classes:
                current_status = "DOWN"

        # 4. Extract History (The Pips)
        pips = cols[3].find_all('div', class_='pip')
        history = []
        for pip in pips:
            pip_classes = pip.get('class', [])
            history_status = "UP" if "up" in pip_classes else "DOWN"
            timestamp = pip.get('title', '').replace('Recorded at: ', '')
            
            history.append({
                "status": history_status,
                "timestamp": timestamp
            })

        extracted_data.append({
            "service": service_name,
            "host": host,
            "current_status": current_status,
            "history": history
        })

    return extracted_data

url = 'http://localhost:8000/'
r = requests.get(url, timeout=10)


if r.status_code != 200:
    print(f'Scoringengine returned non-200 code')

results = parse_dashboard(r.text)

frieren_entry = next((item for item in results if item["service"] == "FRIEREN-dns"), None)
if not frieren_entry:
    print('Scoringengine doesn\'t have FRIEREN-dns check')

from app import app
from models import ScoreResult

with app.app_context():
    # Finding the 2nd most recent entry as seen in your screenshot
    entry = ScoreResult.query.filter_by(check_name='FRIEREN-dns')\
                            .order_by(ScoreResult.timestamp.desc())\
                            .offset(1)\
                            .first()
    
    