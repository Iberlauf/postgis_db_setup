"""Init."""

from sqlalchemy import Connection, Engine
from sqlmodel import Session, SQLModel

from default_values import (
    ekipa_defaults,
    investitor_defaults,
    magnetometar_defaults,
    proizvodjac_defaults,
    projekat_defaults,
)
from models.enums import NacinSnimanjaEnum, NulaEnum
from models.geometry_models import PoljaGpr, PoljaMag, ProfilGpr, ProfilMag, Tacke
from models.non_geo_models import (
    Antena,
    Ekipa,
    GeoRadar,
    Investitor,
    Magnetometar,
    Podesavanje,
    PovrsinaPoDatumu,
    Proizvodjac,
    Projekat,
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


def add_defaults(engine: Engine) -> None:
    """Add default values to tables.

    Args:
        engine (Engine): SQLAlchemy engine.

    """
    ekipe: list[Ekipa] = [
        Ekipa.model_validate(obj=data, strict=True, from_attributes=True)
        for data in ekipa_defaults
    ]
    proizvodjaci: list[Proizvodjac] = [
        Proizvodjac.model_validate(obj=data, strict=True, from_attributes=True)
        for data in proizvodjac_defaults
    ]
    uredjaji: list[Magnetometar] = [
        Magnetometar.model_validate(obj=data, strict=True, from_attributes=True)
        for data in magnetometar_defaults
    ]
    investitori: list[Investitor] = [
        Investitor.model_validate(obj=data, strict=True, from_attributes=True)
        for data in investitor_defaults
    ]
    projekti: list[Projekat] = [
        Projekat.model_validate(obj=data, strict=True, from_attributes=True)
        for data in projekat_defaults
    ]

    with Session(bind=engine) as session:
        session.add_all(
            instances=ekipe,
        )
        session.commit()
        for instance in ekipe:
            session.refresh(instance=instance)
        session.add_all(
            instances=proizvodjaci,
        )
        session.commit()
        for instance in proizvodjaci:
            session.refresh(instance=instance)
        session.add_all(
            instances=uredjaji,
        )
        session.commit()
        for instance in uredjaji:
            session.refresh(instance=instance)
        for instance in investitori:
            session.add(instance=instance)
        session.commit()
        for instance in investitori:
            session.refresh(instance=instance)
        session.add_all(
            instances=projekti,
        )
        session.commit()
        for instance in projekti:
            session.refresh(instance=instance)


__all__: list[str] = [
    "Antena",
    "Ekipa",
    "GeoRadar",
    "Investitor",
    "Magnetometar",
    "NacinSnimanjaEnum",
    "NulaEnum",
    "Podesavanje",
    "PoljaGpr",
    "PoljaMag",
    "PovrsinaPoDatumu",
    "ProfilGpr",
    "ProfilMag",
    "Proizvodjac",
    "Projekat",
    "Tacke",
    "create_db_and_tables",
]
