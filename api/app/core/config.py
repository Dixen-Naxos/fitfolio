from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Known-insecure placeholder/default values shipped in .env.example. These are fine for local
# development but must never reach production, so `validate_for_production` rejects them.
PLACEHOLDER_JWT_SECRET = "change-me-to-a-long-random-string"
DEFAULT_DB_CREDENTIALS = "fitfolio:fitfolio"
DEFAULT_MINIO_ACCESS_KEY = "fitfolio"
DEFAULT_MINIO_SECRET_KEYS = {"fitfolio123", "fitfolio123fitfolio123fitfolio1"}
# A production JWT secret should carry real entropy; reject anything obviously too short.
MIN_JWT_SECRET_LENGTH = 32


class ConfigError(RuntimeError):
    """Raised at startup when the effective configuration is unsafe for production."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Deployment environment. Set ENVIRONMENT=production to enable fail-fast config validation.
    environment: str = "development"

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
    # Must match the S3-compatible server's configured region (e.g. Garage's `s3_region`),
    # otherwise SigV4 signature validation fails.
    minio_region: str = "garage"
    # Optional externally reachable endpoint used only to sign browser/mobile-facing presigned URLs.
    # Keep MINIO_ENDPOINT internal for server-to-server MinIO operations.
    minio_presign_endpoint: str | None = None
    minio_presign_secure: bool | None = None

    # Rate limiting (brute-force / credential-stuffing protection on auth endpoints).
    # Set RATE_LIMIT_ENABLED=false to disable entirely (e.g. in tests). Limit strings use
    # slowapi/limits syntax, e.g. "10/minute", "5/hour".
    rate_limit_enabled: bool = True
    auth_login_rate_limit: str = "10/minute"
    auth_register_rate_limit: str = "10/hour"
    auth_refresh_rate_limit: str = "30/minute"

    # CORS
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() == "production"

    def production_config_problems(self) -> list[str]:
        """Return the list of insecure-default problems that must be fixed before production."""
        problems: list[str] = []

        if self.jwt_secret_key == PLACEHOLDER_JWT_SECRET:
            problems.append(
                "JWT_SECRET_KEY is still the placeholder value; generate one with "
                '`python -c "import secrets; print(secrets.token_urlsafe(64))"`.'
            )
        elif len(self.jwt_secret_key) < MIN_JWT_SECRET_LENGTH:
            problems.append(
                f"JWT_SECRET_KEY is too short (< {MIN_JWT_SECRET_LENGTH} chars); use a long random secret."
            )

        if "*" in self.cors_origin_list:
            problems.append(
                "CORS_ORIGINS is a wildcard ('*'); set it to your explicit frontend origin(s)."
            )

        if DEFAULT_DB_CREDENTIALS in self.database_url:
            problems.append(
                "DATABASE_URL still uses the default 'fitfolio:fitfolio' credentials; set a real password."
            )

        if self.minio_access_key == DEFAULT_MINIO_ACCESS_KEY:
            problems.append("MINIO_ACCESS_KEY is still the default 'fitfolio'; set a real access key.")
        if self.minio_secret_key in DEFAULT_MINIO_SECRET_KEYS:
            problems.append("MINIO_SECRET_KEY is still the default 'fitfolio123'; set a real secret key.")

        return problems

    def validate_for_production(self) -> None:
        """Fail fast when running in production with insecure default configuration."""
        if not self.is_production:
            return
        problems = self.production_config_problems()
        if problems:
            bullets = "\n".join(f"  - {p}" for p in problems)
            raise ConfigError(
                "Refusing to start in production with insecure configuration:\n" + bullets
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
