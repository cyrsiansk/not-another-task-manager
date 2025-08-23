from pydantic_settings import BaseSettings


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

    class Config:
        env_file = ".env"


settings = Settings()
