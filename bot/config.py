from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str
    database_url: str = "sqlite+aiosqlite:///./tutor_bot.db"
    timezone: str = "Europe/Moscow"
    reminder_check_interval: int = 60


settings = Settings()