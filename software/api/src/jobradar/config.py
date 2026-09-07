from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    db_pool_min: int = 1
    db_pool_max: int = 4


settings = Settings()
