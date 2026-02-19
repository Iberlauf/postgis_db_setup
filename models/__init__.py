"""Init."""

from typing import Any

from sqlalchemy import Connection, Engine
from sqlmodel import Session, SQLModel

from default_values import (
    antena_defaults,
    ekipa_defaults,
    georadar_defaults,
    investitor_defaults,
    magnetometar_defaults,
    nule_defaults,
    proizvodjac_defaults,
    projekat_defaults,
)
from models.enums import (
    NacinSnimanjaEnum,
)
from models.geometry_models import PoljaGpr, PoljaMag, ProfilGpr, ProfilMag, Tacke
from models.non_geo_models import (
    Antena,
    Ekipa,
    GeoRadar,
    Investitor,
    Magnetometar,
    Nula,
    Podesavanje,
    PoljaGprEkipa,
    PoljaMagEkipa,
    PovrsinaPoDatumu,
    ProfilGprEkipa,
    ProfilMagEkipa,
    Proizvodjac,
    Projekat,
    ProjekatEkipa,
)
from sql_statements import (
    first_sql_statements,
    insert_epsg_3855,
)


def create_db_and_tables(engine: Engine) -> None:
    """Create db and tables.

    Args:
        engine (Engine): SQLAlchemy engine.

    """
    with engine.begin() as conn:
        if isinstance(conn, Connection):
            for statement in first_sql_statements:
                conn.execute(statement=statement)
            conn.execute(statement=insert_epsg_3855)

            SQLModel.metadata.drop_all(bind=conn)
            SQLModel.metadata.create_all(bind=conn)

            conn.commit()


def populate_defaults(engine: Engine) -> None:
    """Populate the tables with initial default values.

    Args:
        engine (Engine): SQLAlchemy engine.

    """
    defaults_mapping: list[tuple[type[SQLModel], list[dict[str, Any]]]] = [
        (Ekipa, ekipa_defaults),
        (Proizvodjac, proizvodjac_defaults),
        (Magnetometar, magnetometar_defaults),
        (Investitor, investitor_defaults),
        (GeoRadar, georadar_defaults),
        (Antena, antena_defaults),
        (Projekat, projekat_defaults),
        (Nula, nule_defaults),
    ]

    with Session(bind=engine) as session:
        for model_class, defaults in defaults_mapping:
            instances: list = [
                model_class.model_validate(obj=data, strict=True, from_attributes=True)
                for data in defaults
            ]

            session.add_all(instances=instances)
            session.commit()
            for instance in instances:
                session.refresh(instance=instance)


__all__: list[str] = [
    "Antena",
    "Ekipa",
    "GeoRadar",
    "Investitor",
    "Magnetometar",
    "NacinSnimanjaEnum",
    "Nula",
    "Podesavanje",
    "PoljaGpr",
    "PoljaGprEkipa",
    "PoljaMag",
    "PoljaMagEkipa",
    "PovrsinaPoDatumu",
    "ProfilGpr",
    "ProfilGprEkipa",
    "ProfilMag",
    "ProfilMagEkipa",
    "Proizvodjac",
    "Projekat",
    "ProjekatEkipa",
    "Tacke",
    "create_db_and_tables",
]
