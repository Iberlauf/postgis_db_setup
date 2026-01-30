"""Settings."""

from pydantic import Field, NonNegativeInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    """Settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    postgis_db_name: str
    postgis_db_pass: str
    postgis_db_host: str = Field(
        default="localhost",
        description="Host address.",
    )
    postgis_db_port: NonNegativeInt = Field(
        default=5432,
        description="Port number.",
        le=65535,
    )
    postgis_db_schema: str


settings: DbSettings = DbSettings()  # type: ignore  # noqa: PGH003
