import subprocess
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init
init()

def run(host, metadata):
    """
    This check tests RDP login...quite scuffed, im running this on a windows with wsl so i have to wrap the xfreerdp command in "ubuntu run" kek
    
    Tests RDP credentials using xfreerdp /auth-only.
    Expects metadata['credentials'] in 'user:pass' or 'domain\\user:pass' format.
    """
    creds_raw = metadata.get('credentials', '')
    
    if ':' not in creds_raw:
        cprint(f"RDP Check Failed: [{host}] - Missing credentials.", "red")
        return False

    username, password = creds_raw.rsplit(':', 1)
    
    # Handle domain if present in username (e.g., "MYLAB\Administrator")
    domain = ""
    if "\\" in username:
        domain, username = username.split("\\", 1)

    # Build the xfreerdp command
    # /v: host, /u: user, /p: pass, /d: domain
    # +cert-ignore: skip SSL cert check (common in labs)
    # /auth-only: test login and exit
    if domain:
        cmd = [
            "ubuntu", 
            "run",
            f"xfreerdp /v:{host} /u:{username} /p:'{password}' /d:{domain} /cert:ignore +auth-only /sec:nla /timeout:7000 -clipboard"
        ]
    else:
       cmd = [
            "ubuntu",
            "run",
            f"xfreerdp /v:{host} /u:{username} /p:'{password}' /cert:ignore  +auth-only /sec:nla /timeout:7000 -clipboard"
        ] 

    try:
        # Run command with a timeout
        # xfreerdp returns 0 on success, and usually 1 or 131 on failure
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            timeout=15
        )

        if result.returncode == 0:
            return True
        else:
            # Log the error from stderr for debugging
            err_msg = result.stderr.decode().strip().split('\n')[-1]
            logger.info(f"Check Failed: [{host}] - {err_msg}")
            return False

    except subprocess.TimeoutExpired:
        logger.info(f"Check Failed: [{host}] - Connection timed out.")
        return False
    except Exception as e:
        logger.info(f"Check Failed: [{host}] - Unexpected error: {str(e)}")
        return False