import requests
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init

init()

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

from app import app
from models import ScoreResult
from datetime import datetime

def run(host, metadata):
    """
    scoringengine
    """

    url = f'http://{host}:8000/'

    try:
        r = requests.get(url, timeout=10)
        

        if r.status_code != 200:
            logger.info(f'Check Failed: [{host}] - Scoringengine returned non-200 code')
            return False
        
        results = parse_dashboard(r.text)
        
        frieren_entry = next((item for item in results if item["service"] == "FRIEREN-dns"), None)
        if not frieren_entry:
            logger.info(f'Check Failed: [{host}] - Scoringengine doesn\'t have FRIEREN-dns check')
            return False
        
        if len(frieren_entry['history']) < 2:
            return True
        
        check = frieren_entry['history'][1]
        
        with app.app_context():
            # Finding the most recent entry in db
            entry = ScoreResult.query.filter_by(check_name='FRIEREN-dns')\
                                    .order_by(ScoreResult.timestamp.desc())\
                                    .first()
            
            if not entry:
                return True
            
            entry = entry.to_dict()
            
            check['status'] = True if check['status'] == 'UP' else False
            if check['status'] != entry['status']:
                logger.info(f'Check Failed: [{host}] - Scoringengine FRIEREN-dns check mismatch with local')
                return False
            local_dt = datetime.fromisoformat(entry['timestamp'])
            scraped_dt = datetime.strptime(check['timestamp'], '%Y-%m-%d %H:%M:%S')
            if abs((local_dt - scraped_dt).total_seconds()) >= 30:
                logger.info(f'Check Failed: [{host}] - Scoringengine FRIEREN-dns check not within 30 seconds of local')
                return False
            
        return True

    except requests.exceptions.Timeout as e:
        logger.info(f"Check Failed: [{host}] - Timeout: {e}")
        return False
    except requests.exceptions.RequestException as e:
        # Handle other potential requests errors (e.g., ConnectionError)
        logger.info(f"Check Failed: [{host}] - Exception: {str(e)}")
        return False
    except Exception as e:
        logger.info(f"Check Failed: [{host}] - Exception: {str(e)}")
        return False