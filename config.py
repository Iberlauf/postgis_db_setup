"""Settings."""

from pydantic import Field, NonNegativeInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    """Settings."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )
    postgis_db_name: str
    postgis_db_user: str
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


settings: DbSettings = DbSettings()  # type: ignore  # noqa: PGH003

if __name__ == "__main__":
    ...
