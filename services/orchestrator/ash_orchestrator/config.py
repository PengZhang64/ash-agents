from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    changedetection_url: str = "http://localhost:5000"
    changedetection_api_key: str = ""
    test_product_url: str = "http://localhost:8088"
    orchestrator_webhook_secret: str = "dev-secret-change-me"
    ash_meter_stub_balance: int = 1000
    cloakbrowser_enabled: bool = False
    proxy_pool: str = ""


settings = Settings()
