"""Configuration unifiee de Loguru pour le package iatos_core."""

import sys
from loguru import logger
from iatos_core.config import LOGS_DIR

# Supprimer la configuration par defaut
logger.remove()

# 1. Sortie console lisible et coloree
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# 2. Rotation quotidienne de fichier de log
log_file_path = LOGS_DIR / "iatos_service.log"
logger.add(
    str(log_file_path),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="00:00",
    retention="14 days",
    encoding="utf-8",
)

__all__ = ["logger"]
