import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_dir='logs', log_file='thumbnail_api.log', max_bytes=5*1024*1024, backup_count=3):
    """
    Configure logging for the Thumbnail API.
    
    Args:
        log_dir (str): Directory to store logs (default: 'logs').
        log_file (str): Log file name (default: 'thumbnail_api.log').
        max_bytes (int): Max size per log file (default: 5MB).
        backup_count (int): Number of backup files (default: 3).
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logger
    logger = logging.getLogger('ThumbnailAPI')
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # Create rotating file handler
        log_path = os.path.join(log_dir, log_file)
        handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger