from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "AxleFlow TMS"
    DATABASE_URL: str

    # Auth secrets
    JWT_SECRET: str
    SECRET_KEY: str | None = None

    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours default

    # Fallback: if SECRET_KEY not set, reuse JWT_SECRET
    @property
    def session_secret(self) -> str:
        return self.SECRET_KEY or self.JWT_SECRET


settings = Settings()
