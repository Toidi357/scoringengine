import socket
from logger import scoring_log as logger
from termcolor import cprint
from colorama import init

init()

def run(host, metadata):
    """
    Checks if the MySQL port is open and responding with a MySQL handshake packet.
    Does NOT attempt to authenticate or query data.
    
    Expected metadata: none
    Optional metadata: port
    """
    
    port = metadata.get('port', 3306)
    timeout = 5
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)

    try:
        s.connect((host, port))
        packet = s.recv(1024)

        # 0x0a is the standard "Greeting"
        # 0xff is the MySQL "Error" packet
        if len(packet) > 5 and (packet[4] == 0x0a or packet[4] == 0xff):
            # If we get 0xff, the server told us to go away, 
            # which means the server IS alive!
            return True
        
        logger.info(f"Check Failed: [{host}] - Port open but unexpected data received.")
        return False

    except (socket.timeout, ConnectionRefusedError):
        return False
    except Exception as e:
        logger.info(f"Check Failed: [{host}] - Error: {str(e)}")
        return False
    finally:
        s.close()