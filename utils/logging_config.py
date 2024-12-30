import logging
import os
from datetime import datetime

def setup_logging(log_dir: str) -> None:
    """
    Configure logging with file handler
    Args:
        log_dir: Directory for log files
    """
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_file = os.path.join(log_dir, f"{current_time}-error.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
