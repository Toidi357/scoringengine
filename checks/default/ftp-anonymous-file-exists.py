from ftplib import FTP
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init
init()

def run(host, metadata):
    """
    This check logs into FTP server anonymously, lists contents, and checks if a file exists
    
    Expects metadata: filename
    """
    filename = metadata.get('filename', '')
    
    if not filename:
        cprint(f"FTP Check Failed: [{host}] - Missing metadata (filename).", "red")
        return False

    try:
        ftp = FTP(host, timeout=5)
        
        ftp.login() # anonymous login
        
        output = ftp.nlst()
        
        if filename in output:
            return True
        else:
            logger.info(f"Check Failed: [{host}] - Missing file '{filename}'")
            return False

    except Exception as e:
        logger.info(f"Check Failed: [{host}] - Exception: {str(e)}")
        return False