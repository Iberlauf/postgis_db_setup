"""Main function."""

from typing import TYPE_CHECKING

from sqlmodel import create_engine

from config import settings
from models import add_defaults, create_db_and_tables

if TYPE_CHECKING:
    from sqlalchemy.engine.base import Engine

DATABASE_URL: str = f"postgresql+psycopg://{settings.postgis_db_user}:{settings.postgis_db_pass}@{settings.postgis_db_host}:{settings.postgis_db_port}/{settings.postgis_db_name}"
if __name__ == "__main__":
    engine: Engine = create_engine(url=DATABASE_URL, echo=True)
    create_db_and_tables(engine=engine)
    add_defaults(engine=engine)
