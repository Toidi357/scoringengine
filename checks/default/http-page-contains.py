import requests
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init
init()

def run(host, metadata):
    """
    This check requests a given webpage over http port 80, and ensures that the page contains a string you specified in scoring.conf
    
    Expects metadata: path, contains (expected string)
    """
    path = metadata.get('path', '')
    contains = metadata.get('contains', '')
    
    if not path or not contains:
        cprint(f"{host} http-default: - Missing metadata (path or contains)", "red")
        return False

    url = f'http://{host}/{path}'

    try:
        r = requests.get(url, timeout=5)

        if contains in r.text:
            return True
        
        logger.info(f"Check Failed: [{host}] - String '{contains}' not present in {url}")
        return False

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