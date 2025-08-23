import logging
import logging.handlers
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from app.config import settings


def setup_logging() -> None:
    if getattr(settings, "DISABLE_LOGGING", False):
        root = logging.getLogger()
        for h in list(root.handlers):
            root.removeHandler(h)
        root.addHandler(logging.NullHandler())
        root.setLevel("CRITICAL")
        return

    level = getattr(settings, "LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO")).upper()
    log_to_file = getattr(
        settings,
        "LOG_TO_FILE",
        os.getenv("LOG_TO_FILE", "true").lower() in ("1", "true", "yes"),
    )

    log_file = getattr(settings, "LOG_FILE", os.getenv("LOG_FILE", "logs/app.log"))
    log_to_console = getattr(settings, "LOG_TO_CONSOLE", True)

    if log_to_file:
        log_dir = os.path.dirname(log_file) or "logs"
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception:
            log_to_file = False

    root = logging.getLogger()
    root.setLevel(level)

    for h in list(root.handlers):
        root.removeHandler(h)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    if log_to_console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(fmt)
        root.addHandler(ch)

    if log_to_file:
        try:
            fh = TimedRotatingFileHandler(
                log_file, when="midnight", backupCount=14, encoding="utf-8"
            )
            fh.setLevel(level)
            fh.setFormatter(fmt)
            root.addHandler(fh)
        except PermissionError:
            root.debug("failed to open log file; skipping file handler", exc_info=True)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
