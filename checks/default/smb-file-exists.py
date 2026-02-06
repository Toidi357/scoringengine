import smbclient
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init
init()

def run(host, metadata):
    """
    This check logs into an smb share and sees if a given filename is present

    Expects metadata: share (share name), credentials (user:pass), file (which file we're testing for existence)
    """

    share = metadata.get('share', '')
    credentials = metadata.get('credentials', '')
    file = metadata.get('file', '')
    
    if ':' not in credentials or not share or not file:
        cprint(f"{host} smb-file-exists: Missing metadata (share, credentials, file)", "red")
        return False
    
    username, password = credentials.split(":")
    

    try:
        smbclient.register_session(host, username=username, password=password, connection_timeout=10)

        dir_contents = smbclient.listdir(f"\\\\{host}\\{share}")
        
        if file in dir_contents:
            return True
        
        logger.info(f"Check Failed: [{host}] - File '{file}' not present in share")
        return False

    except Exception as e:
        logger.info(f"Check Failed: [{host}] - Exception: {str(e)}")
        return False
    
    finally:
        try:
            smbclient.reset_connection_cache()
        except:
            pass