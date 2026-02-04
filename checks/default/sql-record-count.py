import mysql.connector
from logger import scoring_log as logger
from termcolor import colored, cprint
from colorama import init
init()

def run(host, metadata):
    """
    This check performs an SQL query and checks the number of records returned matches as specified in scoring.conf
    
    Expects metadata: credentials (user:pass), database, table, count (expected count)
    """
    credentials = metadata.get('credentials', '')
    database = metadata.get('database', '')
    table = metadata.get('table', '')
    count = metadata.get('count', '')
    
    if ':' not in credentials or not database or not table or not count or not count.isdigit():
        cprint(f"SQL Check Failed: [{host}] - Missing metadata (credentials, database, table, count).", "red")
        return False

    username, password = credentials.split(":")
    count = int(count)


    try:
        mydb = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database,
            connection_timeout=5
        )
        
        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT COUNT(*) FROM {table}")

        myresult = mycursor.fetchall()
        
        if count == myresult[0][0]:
            return True
        else:
            logger.info(f"Check Failed: [{host}] - Got expected '{count}' but got '{myresult[0][0]}'")
            return False

    except Exception as e:
        logger.info(f"Check Failed: [{host}] - Exception: {str(e)}")
        return False