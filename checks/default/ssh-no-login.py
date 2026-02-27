import socket
from logger import scoring_log as logger
from termcolor import cprint
from colorama import init

init()

def run(host, metadata):
    """
    Checks if the SSH port is open and returns a valid SSH banner.
    Does NOT attempt to authenticate.
    
    Expected metadata: none
    Optional metadata: port
    """
    port = metadata.get('port', 22)
    timeout = 5  # Connectivity checks should be snappy

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)

    try:
        # 1. Attempt TCP Connection
        s.connect((host, port))
        
        # 2. Receive the Banner
        # SSH servers automatically send a string like "SSH-2.0-OpenSSH_8.9p1..."
        banner = s.recv(1024).decode().strip()

        if banner.startswith("SSH-"):
            # Optional: log the banner for debugging/version tracking
            # logger.info(f"Check Passed: [{host}] - {banner}")
            return True
        else:
            logger.info(f"Check Failed: [{host}] - Port open but no SSH banner received.")
            return False

    except socket.timeout:
        logger.info(f"Check Failed: [{host}] - Connection timed out.")
        return False
    except ConnectionRefusedError:
        logger.info(f"Check Failed: [{host}] - Connection refused.")
        return False
    except Exception as e:
        logger.info(f"Check Failed: [{host}] - Error: {str(e)}")
        return False
    finally:
        s.close()
