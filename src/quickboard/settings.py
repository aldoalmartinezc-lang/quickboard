from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "QuickBoard"
    version: str = "0.1.0"
    database_url: str = "sqlite:///./quickboard.db"
