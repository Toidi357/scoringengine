import smbclient
from logger import scoring_log as logger
from termcolor import cprint
from colorama import init

init()


def run(host, metadata):
    """
    Attempts to check if a file exists in an SMB share using an anonymous/guest session.
    
    Expects metadata: share, file
    """
    share = metadata.get('share', '')
    file = metadata.get('file', '')
    
    if not share or not file:
        cprint(f"{host} smb-anonymous-file-exists: Missing metadata (share, file).", "red")
        return False

    try:
        smbclient.ClientConfig(require_secure_negotiate=False)
        
        # Registering an anonymous session: 
        # Use 'Guest' or 'Anonymous' with an empty password.
        smbclient.reset_connection_cache()
        smbclient.register_session(
            host, 
            username='Guest', 
            password='', 
            connection_timeout=10,
            encrypt=False, 
            #require_signing=False,
        )

        # Attempt to list the directory
        # Note: smbclient handles the backslashes, but ensure the path is valid
        share_path = f"\\\\{host}\\{share}"
        dir_contents = smbclient.listdir(share_path)
        
        if file in dir_contents:
            return True
        
        logger.info(f"Check Failed: [{host}] - File '{file}' not found in anonymous share '{share}'")
        return False

    except Exception as e:
        # This will catch 'Access Denied' if Guest access is disabled on the server
        logger.info(f"Check Failed: [{host}] - Anonymous Access Error: {str(e)}")
        return False
    
    finally:
        try:
            smbclient.reset_connection_cache()
        except:
            pass