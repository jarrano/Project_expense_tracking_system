import logging
import os


# ============================================
# CREATE LOGGING
# ============================================
def setup_logger(name, log_file='server.log', level=logging.DEBUG):
    # Create a custom logger
    logger = logging.getLogger(name)

    # Configure the custom logger
    logger.setLevel(level)

    # Get the absolute path to the 'backend' folder where this script lives
    log_file_path = os.path.join(os.path.dirname(__file__), log_file)

    # Create the file handler
    file_handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger