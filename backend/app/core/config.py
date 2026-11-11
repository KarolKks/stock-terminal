from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    
    # PostgreSQL database credentials (required from environment)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # PostgreSQL server host and port (with sensible defaults for Docker setup)
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: int = 5432

    # JWT Authentication configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # 7 days

    @property
    def async_database_url(self) -> str:
        """Construct the async SQLAlchemy connection string for asyncpg."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Pydantic Settings configuration specifying .env file source
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instantiate single configuration instance for application-wide use
settings = Settings()