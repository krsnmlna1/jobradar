"""Konfigurasi dibaca dari environment / file .env. Jangan hardcode kredensial."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Format: postgresql://user:password@host:port/dbname
    database_url: str = "postgresql://odin@localhost:5432/jobradar"

    # Ukuran pool. Dijaga kecil: WSL dibatasin 4 GB, lihat catatan .wslconfig.
    db_pool_min: int = 1
    db_pool_max: int = 4


settings = Settings()
