import logging

# Temporary Loging File
log_path = "/home/madhav/workspace/projects/ganitagya/app.log"

logging.basicConfig(
    filename=log_path,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True,
)

log = logging.getLogger(__name__)
log.info(f"App started! Logs are safely hidden at: {log_path}")
