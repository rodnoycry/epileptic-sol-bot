import os
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set up file handler with rotation
    file_handler = RotatingFileHandler(
        'logs/bot.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Set up logger
    logger = logging.getLogger('TelegramBot')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()