"""Init."""

from typing import TYPE_CHECKING, TypeVar

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, SQLModel

from mandatory_default_values import (
    epsg_3855,
    nule_defaults,
)
from models.enums import NacinSnimanjaEnum
from models.geometry_models import (
    DsmRaster,
    PoljeGpr,
    PoljeMag,
    ProfilGpr,
    ProfilMag,
    Tacka,
)
from models.non_geo_models import (
    Antena,
    Ekipa,
    GeoRadar,
    Investitor,
    Magnetometar,
    Nula,
    Podesavanje,
    PovrsinaPoDatumu,
    Proizvodjac,
    Projekat,
    SpatialRefSys,
)
from sql_statements import first_sql_statements
from testing_default_values import (
    antena_defaults,
    ekipa_defaults,
    georadar_defaults,
    investitor_defaults,
    magnetometar_defaults,
    proizvodjac_defaults,
    projekat_defaults,
)

if TYPE_CHECKING:
    from sqlalchemy import Engine
    from sqlalchemy.dialects.postgresql.dml import Insert
    from sqlalchemy.sql.schema import Table

T = TypeVar("T", bound=SQLModel)

tables_to_drop: list[Table] = [
    t
    for t in SQLModel.metadata.sorted_tables
    if t.name not in (SpatialRefSys.__tablename__, DsmRaster.__tablename__)
]

insert_epsg_3855: Insert = (
    insert(table=SpatialRefSys)
    .values(epsg_3855)
    .on_conflict_do_nothing(index_elements=["srid"])
)


def create_instances[T: SQLModel](
    model_class: type[T],
    defaults: list[dict[str, int | str]],
) -> list[T]:
    """Create validated SQLModel instances from a list of default value mappings.

    Each dictionary in ``defaults`` is validated against ``model_class`` using
    ``model_validate`` with ``strict=True`` and ``from_attributes=True``,
    ensuring full type validation and no coercion.

    Args:
        model_class: The SQLModel subclass to instantiate.
        defaults: A list of dictionaries containing field values for the model.

    Returns:
        A list of validated instances of type ``T``.

    Raises:
        ValidationError: If any of the provided dictionaries fail validation.

    """
    return [
        model_class.model_validate(obj=data, strict=True, from_attributes=True)
        for data in defaults
    ]


def create_db_and_tables(engine: Engine) -> None:
    """Create db and tables.

    Args:
        engine (Engine): SQLAlchemy engine.

    """
    with engine.begin() as conn:
        for statement in first_sql_statements:
            conn.execute(statement=statement)
        conn.execute(statement=insert_epsg_3855)

        SQLModel.metadata.drop_all(bind=conn, tables=tables_to_drop)
        SQLModel.metadata.create_all(bind=conn)


def populate_defaults(engine: Engine) -> None:
    """Populate the tables with initial default values.

    Args:
        engine (Engine): SQLAlchemy engine.

    """
    defaults_mapping: list[tuple[type[SQLModel], list[dict[str, int | str]]]] = [
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
            instances: list = create_instances(
                model_class=model_class,
                defaults=defaults,
            )

            session.add_all(instances=instances)
            session.commit()
            for instance in instances:
                session.refresh(instance=instance)


__all__: list[str] = [
    "Antena",
    "DsmRaster",
    "Ekipa",
    "GeoRadar",
    "Investitor",
    "Magnetometar",
    "NacinSnimanjaEnum",
    "Nula",
    "Podesavanje",
    "PoljeGpr",
    "PoljeMag",
    "PovrsinaPoDatumu",
    "ProfilGpr",
    "ProfilMag",
    "Proizvodjac",
    "Projekat",
    "Tacka",
    "create_db_and_tables",
    "populate_defaults",
]
