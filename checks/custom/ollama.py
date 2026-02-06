import requests
import json
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init
init()

def run(host, metadata):
    """
    Ollama
    
    """

    url = f'http://{host}/api/generate'

    try:
        r = requests.post(url, data=json.dumps({
            "model": "tinyllama",
            "prompt": "what's 1 + 1",
            "stream": False
        }), timeout=10)

        if "tinyllama" in r.text:
            return True
        
        logger.info(f'Check Failed: [{host}] - Ollama failed')
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