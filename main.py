"""Main function."""

from typing import TYPE_CHECKING

from sqlmodel import create_engine

from config import settings
from models import create_db_and_tables, populate_defaults
from sql_statements import register_immutability_triggers, register_triggers

if TYPE_CHECKING:
    from sqlalchemy.engine.base import Engine

DATABASE_URL: str = f"postgresql+psycopg://{settings.postgis_db_user}:{settings.postgis_db_pass}@{settings.postgis_db_host}:{settings.postgis_db_port}/{settings.postgis_db_name}"
if __name__ == "__main__":
    engine: Engine = create_engine(url=DATABASE_URL, echo=True)
    register_triggers()
    create_db_and_tables(engine=engine)
    populate_defaults(engine=engine)
    register_immutability_triggers(engine=engine)
