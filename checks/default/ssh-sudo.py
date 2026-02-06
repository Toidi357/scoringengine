from fabric import Connection
from invoke import exceptions
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init
init()

def run(host, metadata):
    """
    This check attempts an ssh connection to a host with given credentials, and tests we have sudo by doing echo <password> | sudo -S whoami
    
    Attempts to connect to a host via SSH using Fabric.
    Expected metadata['credentials'] format: "DOMAIN\\username:password" or "username:password"
    """
    creds_raw = metadata.get('credentials', '')
    
    if ':' not in creds_raw:
        cprint(f"{host} SSH-default: Invalid credentials format in config.", "red")
        return False

    # Splitting credentials (handling potential domain backslashes)
    user_part, password = creds_raw.rsplit(':', 1)
    
    # Fabric/Paramiko expects just the username; if domain is present, we keep it in the user string
    username = user_part

    try:
        # Configuration for the connection
        # connect_timeout: How long to wait for the TCP handshake
        # banner_timeout: How long to wait for the SSH banner
        conn_params = {
            "host": host,
            "user": username,
            "connect_kwargs": {
                "password": password,
                "banner_timeout": 7,
                "auth_timeout": 7
            },
            "connect_timeout": 7,
        }

        with Connection(**conn_params) as c:
            result = c.run(f"echo '{password}' | sudo -S whoami", hide=True, pty=True, timeout=7)
            
            if 'root' in result.stdout:
                return True
            else:
                logger.info(f"Check Failed: [{host}] - Sudo command failed.")
                return False

    except exceptions.CommandTimedOut:
        logger.info(f"Check Failed: [{host}] - Command timed out.")
        return False
    except exceptions.UnexpectedExit:
        logger.info(f"Check Failed: [{host}] - SSH session ended unexpectedly.")
        return False
    except Exception as e:
        # This captures Auth failures, Connection Refused, etc.
        logger.info(f"Check Failed: [{host}] - Exception: {str(e)}")
        return False