import logging
from pathlib import Path

# Log relative path
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "app.log"
BASE_DIR = Path(__file__).resolve().parent.parent
log_path= BASE_DIR / "app.log"


logging.basicConfig(
    filename=log_path,
    filemode='a',
    level=logging.INFO,
    # Added [%(filename)s:%(lineno)d] to track the source file and line number
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True,
)

# --- SILENCE UVICORN AND POSTGRES LOGS ---
noisy_loggers = [
    "uvicorn", 
    "uvicorn.error", 
    "uvicorn.access", 
    "sqlalchemy.engine", 
    "psycopg", 
    "asyncpg"
]

for logger_name in noisy_loggers:
    muted_logger = logging.getLogger(logger_name)
    muted_logger.setLevel(logging.CRITICAL)
    muted_logger.propagate = False

# --- CONTINUE YOUR APP LOGGING ---
log = logging.getLogger(__name__)
log.info(f"Application Bootup")
