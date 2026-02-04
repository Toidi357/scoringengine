import requests
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init
init()

def run(host, metadata):
    """
    This check requests a given webpage over http port 80, and ensures response code begins with 2 or 3
    
    Expects metadata: path,
    """
    path = metadata.get('path', '')
    
    if not path:
        cprint(f"{host} http-exists: - Missing metadata (path)", "red")
        return False

    url = f'http://{host}/{path}'

    try:
        r = requests.get(url, timeout=5)

        if r.status_code > 199 and r.status_code < 400: # what a way to check this lol
            return True
        
        logger.info(f"Check Failed: [{host}] - Path returns status code {r.status_code}")
        return False

    except requests.exceptions.Timeout as e:
        logger.info(f"Check Failed: [{host}] - Timeout: {e}")
    except requests.exceptions.RequestException as e:
        # Handle other potential requests errors (e.g., ConnectionError)
        logger.info(f"Check Failed: [{host}] - Exception: {str(e)}")
    except Exception as e:
        logger.info(f"Check Failed: [{host}] - Exception: {str(e)}")
        return False