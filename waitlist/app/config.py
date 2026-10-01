from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    storage: str = "sqlite"  # "sqlite" for local dev, "firestore" in production
    sqlite_path: str = "waitlist.db"
    firestore_collection: str = "waitlist"

    # Comma-separated, e.g. "https://ganitagya.com,http://localhost:5173"
    allowed_origins: str = "http://localhost:5173"

    rate_limit_max: int = 5            # signups allowed...
    rate_limit_window_seconds: int = 600  # ...per IP in this window

    debug: bool = False  # enables /docs when true

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()