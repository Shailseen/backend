import logging
import os
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

SENSITIVE_PATTERN = re.compile(r'("?(password|token|secret|authorization)"?\s*:\s*")[^"]+(")', re.IGNORECASE)

def mask_sensitive(text: str) -> str:
    try:
        return SENSITIVE_PATTERN.sub(r'\1****\3', text)
    except Exception:
        return text

def configure_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file_path = os.getenv("LOG_FILE_PATH", "logs/app.log")
    max_bytes = int(os.getenv("LOG_MAX_BYTES", "1048576"))  # 1 MB
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    root.addHandler(sh)

    # Rotating file handler
    fh = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # App logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
