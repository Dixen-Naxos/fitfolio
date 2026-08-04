from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://fitfolio:fitfolio@localhost:5432/fitfolio"

    # JWT
    jwt_secret_key: str = "change-me-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "fitfolio"
    minio_secret_key: str = "fitfolio123"
    minio_bucket: str = "fitfolio-images"
    minio_secure: bool = False

    # CORS
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
