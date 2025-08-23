import os
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # app
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # logging
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    LOG_FILE: str = "logs/app.log"
    LOG_TO_CONSOLE: bool = True

    DISABLE_LOGGING: bool = False

    # db
    POSTGRES_PASSWORD: str = "secret"
    DB_USER: str = "app"
    DB_NAME: str = "app_db"
    DB_HOST: str = "db"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        env_db = os.getenv("DATABASE_URL")
        if env_db:
            return env_db

        host = os.getenv("DB_HOST", self.DB_HOST)
        return f"postgresql+psycopg2://{self.DB_USER}:{self.POSTGRES_PASSWORD}@{host}:5432/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
