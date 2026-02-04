import logging
import os

"""
DO NOT TOUCH
"""

def get_scoring_logger():
    """
    Returns a configured logger instance isolated from Flask's default logging.
    """
    logger = logging.getLogger("scoring_engine")
    
    # Prevent logs from leaking into Flask/Werkzeug console
    logger.propagate = False 
    
    # Only add handlers if they don't exist (prevents duplicate logs)
    if not logger.handlers:
        # Ensure the log file is created in the current working directory
        log_file = os.path.join(os.getcwd(), "scoring.log")
        
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', 
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        
    return logger

# Create a singleton-like instance for easy import
scoring_log = get_scoring_logger()