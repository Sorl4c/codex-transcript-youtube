# llm_service/logger.py
# @docs
import logging
import sys

# Determine log level from environment or default to INFO
# Example: LOG_LEVEL=DEBUG python your_app.py
LOG_LEVEL = logging.INFO # Default level
# Could use os.getenv("LOG_LEVEL", "INFO").upper() if using os module

# Create a custom logger
logger = logging.getLogger("llm_service")
logger.setLevel(LOG_LEVEL)

# Create handlers
# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(LOG_LEVEL)

# File handler (optional, could be added based on config)
# fh = logging.FileHandler('llm_service.log')
# fh.setLevel(LOG_LEVEL)

# Create formatter and add it to handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
)
ch.setFormatter(formatter)
# fh.setFormatter(formatter)

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(ch)
    # logger.addHandler(fh) # Uncomment to add file handler

# Prevent duplicate logging if this module is reloaded (e.g., by Uvicorn's reloader)
logger.propagate = False

# Example usage in other modules:
# from .logger import logger
# logger.info("This is an info message from another module.")
