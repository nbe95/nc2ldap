"""Module for constants used in several source files."""

import logging
from os import environ

VERSION: str = environ.get("VERSION", "")
DEBUG: bool = bool(environ.get("DEBUG"))
LOG_LEVEL: int = logging.DEBUG if DEBUG else logging.INFO
