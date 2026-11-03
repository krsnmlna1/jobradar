from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    db_pool_min: int = 1
    db_pool_max: int = 4
    db_pool_timeout: float = 5.0


settings = Settings()
