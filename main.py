"""Main function."""

from typing import TYPE_CHECKING

from sqlmodel import (
    create_engine,
)

from config import settings
from models import create_db_and_tables
from sql_statements import (
    add_sync_trigger,
    apply_sql_config,
    populate_z_from_dsm,
    sort_triggers,
    sql_statements,
)

if TYPE_CHECKING:
    from sqlalchemy.engine.base import Engine

DATABASE_URL: str = f"postgresql+psycopg://postgres:{settings.postgis_db_pass}@{settings.postgis_db_host}:{settings.postgis_db_port}/{settings.postgis_db_name}"


if __name__ == "__main__":
    engine: Engine = create_engine(url=DATABASE_URL, echo=True)
    create_db_and_tables(engine=engine)
    apply_sql_config(engine=engine, statements=sql_statements)
    add_sync_trigger(engine=engine)
    populate_z_from_dsm(engine=engine)
    sort_triggers(engine=engine)
