from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    default_usd_rate: Decimal = Decimal("750.00")
    exchange_api_url: str = "https://api.exchangerate-api.com/v4/latest/USD"
    exchange_timeout_seconds: float = 5.0
    margin_percentage: Decimal = Decimal("40")


settings = Settings()
