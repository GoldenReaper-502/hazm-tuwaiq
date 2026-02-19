from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "HAZM TUWAIQ HSE Platform"
    api_version: str = "v1"
    env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    cors_origins: list[str] = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",")]
    db_path: str = os.getenv("DB_PATH", "backend/platform/hse_demo.db")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))


settings = Settings()
