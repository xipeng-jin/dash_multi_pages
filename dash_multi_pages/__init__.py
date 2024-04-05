import logging
import os

from ._dash_multi_pages import DashMultiPages

__all__ = ["DashMultiPages"]

__version__ = "0.0.1.dev0"

logging.basicConfig(level=os.getenv("DashMultiPages_LOG_LEVEL", "WARNING"))
