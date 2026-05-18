import os
from dataclasses import dataclass

from . import __version__


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "QuickBoard"
    version: str = __version__
    database_url: str = os.getenv("QUICKBOARD_DATABASE_URL", "sqlite:///./quickboard.db")
