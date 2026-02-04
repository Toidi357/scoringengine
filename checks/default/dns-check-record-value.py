import dns.resolver
import dns.exception
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init
init()

def run(host, metadata):
    """
    This check queries a DNS server for a single key, and checks to make sure the answer contains a value you specified in the scoring.conf
    
    Attempts to query a DNS host for a record and ensure the record value matches.
    Expects metadata: domain, recordtype, key (record name), contains (expected string)
    """
    domain = metadata.get('domain', '')
    recordtype = metadata.get('recordtype', 'A').upper()
    key = metadata.get('key', '')  # The record name to look up (e.g., 'google.com')
    contains = metadata.get('contains', '')

    if not recordtype or not key or not contains:
        cprint(f"{host} dns-check-record-value: - Missing metadata (key, type, or contains)", "red")
        return False
    
    full_query_name = f"{key}.{domain}"

    try:
        # 2. Configure a custom resolver to point specifically at 'host'
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [host]
        resolver.timeout = 5.0
        resolver.lifetime = 5.0

        # 3. Perform the lookup
        answers = resolver.resolve(full_query_name, recordtype)

        # 4. Iterate through records to find the value
        for rdata in answers:
            if contains in str(rdata):
                return True
            
        logger.info(f"Check Failed: [{host}] - {full_query_name} found, but '{contains}' not in result.")
        return False

    except dns.resolver.NoAnswer:
        logger.info(f"Check Failed: [{host}] - {full_query_name} exists but has no {recordtype} record.")
        return False
    except dns.resolver.NXDOMAIN:
        logger.info(f"Check Failed: [{host}] - {full_query_name} does not exist.")
        return False
    except dns.exception.Timeout:
        logger.info(f"Check Failed: [{host}] - Connection to DNS server timed out.")
        return False
    except Exception as e:
        logger.info(f"Check Failed: [{host}] - Unexpected error: {str(e)}")
        return False