"""Models."""

from __future__ import annotations

from datetime import date  # noqa: TC003

from geoalchemy2 import Geometry
from geoalchemy2.functions import (
    ST_X,
    ST_Y,
)
from pydantic import EmailStr, NonNegativeFloat  # noqa: TC002
from sqlalchemy import Column, Computed, Connection, Engine
from sqlmodel import (
    CheckConstraint,
    Date,
    Field,
    Numeric,
    Relationship,  # noqa: F401
    SQLModel,
    String,
    text,
)
from sqlmodel._compat import SQLModelConfig  # noqa: TC002

from sql_statements import (
    create_z_trigger,
    create_z_trigger_function,
    insert_epsg_3855,
    sql_statements,
)


class Ekipa(SQLModel, table=True):
    """Tabela članova ekipe."""

    model_config: SQLModelConfig = {
        "arbitrary_types_allowed": True,
        "from_attributes": True,
    }
    __tablename__: str = "ekipa"

    ekipa_id: int | None = Field(
        default=None,
        description="ID člana ekipe.",
        primary_key=True,
    )

    ekipa_ime: str = Field(
        description="Ime člana ekipe.",
        max_length=255,
        index=True,
    )

    ekipa_prezime: str = Field(
        description="prezime člana ekipe.",
        max_length=255,
        index=True,
    )

    ekipa_full_name: str | None = Field(
        default=None,
        description="Puno ime i prezime člana ekipe.",
        max_length=255,
        sa_column=(
            Column(
                String(length=255),
                Computed(
                    sqltext="""--sql
                         ekipa_ime || '_' || ekipa_prezime
                         """,
                ),
            )
        ),
    )


class Investitor(SQLModel, table=True):
    """Tabela investitora."""

    model_config: SQLModelConfig = {
        "arbitrary_types_allowed": True,
        "from_attributes": True,
    }

    __tablename__: str = "investitori"

    investitor_id: int | None = Field(
        default=None,
        description="ID investitora.",
        primary_key=True,
    )

    investitor_ime: str = Field(
        description="Naziv investitora.",
        max_length=255,
        unique=True,
        index=True,
    )
    investitor_adresa: str | None = Field(
        default=None,
        description="Adresa investitora.",
        max_length=255,
    )
    investitor_email: EmailStr | None = Field(
        default=None,
        description="Email adresa investitora.",
        max_length=255,
        unique=True,
    )

    # projekti: list[Projekat] = Relationship(back_populates="investitor")  # noqa: E501, ERA001


class Projekat(SQLModel, table=True):
    """Tabela projekata."""

    model_config: SQLModelConfig = {
        "arbitrary_types_allowed": True,
        "from_attributes": True,
    }

    __tablename__: str = "projekti"
    __table_args__: tuple[CheckConstraint] = (
        CheckConstraint(
            sqltext="""--sql
            projekat_start_datum IS NULL
            OR projekat_kraj_datum IS NULL
            OR projekat_start_datum <= projekat_kraj_datum""",
            name="ck_projekat_datum_opseg",
        ),
    )

    projekat_id: int | None = Field(
        default=None,
        description="ID projekta.",
        primary_key=True,
    )

    projekat_ime: str = Field(
        description="Naziv projekta.",
        max_length=255,
        unique=True,
        index=True,
    )

    broj_ugovora: str = Field(
        description="Broj ugovora.",
        max_length=255,
    )

    projekat_start_datum: date | None = Field(
        default=None,
        description="Datum početka projekta.",
    )

    projekat_kraj_datum: date | None = Field(
        default=None,
        description="Datum završetka projekta.",
    )

    pov_mag: NonNegativeFloat | None = Field(
        default=None,
        description="Ugovorena površina za geomagnetsko snimanje",
    )

    pov_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Ugovorena površina za georadarsko snimanje",
    )

    # investitor_id: int | None = Field(
    #     default=None,  # noqa: ERA001
    #     description="ID investitora.",  # noqa: ERA001
    #     foreign_key="public.investitori.investitor_id",  # noqa: ERA001
    #     index=True,  # noqa: ERA001
    # )  # noqa: ERA001, RUF100

    # investitor: Investitor | None = Relationship(
    #     back_populates="projekti",  # noqa: ERA001
    # )  # noqa: ERA001, RUF100


class ProjectSettings(SQLModel):
    """Podešavanja za projekat."""

    __tablename__: str = "podesavanja"


class Tacke(SQLModel, table=True):
    """Tabela tačaka."""

    model_config: SQLModelConfig = {
        "arbitrary_types_allowed": True,
        "from_attributes": True,
    }

    __tablename__: str = "tacke"

    tacka_id: int | None = Field(
        default=None,
        description="ID tačke.",
        primary_key=True,
    )
    tacka_ime: str = Field(
        description="Naziv tačke.",
        max_length=255,
        index=True,
    )
    datum: date | None = Field(
        default=None,
        description="Datum kotiranja.",
        sa_column=Column(
            type_=Date,
            server_default=text(
                text="""--sql
                    CURRENT_DATE
                    """,
            ),
        ),
    )

    x: NonNegativeFloat | None = Field(
        default=None,
        description="X koordinata",
        sa_column=Column(
            Computed(sqltext=ST_X(text(text="geometry")), persisted=True),
            type_=Numeric(precision=10, scale=3, asdecimal=False),
            nullable=True,
        ),
    )
    y: NonNegativeFloat | None = Field(
        default=None,
        description="Y koordinata",
        sa_column=Column(
            Computed(sqltext=ST_Y(text(text="geometry")), persisted=True),
            type_=Numeric(precision=10, scale=3, asdecimal=False),
            nullable=True,
        ),
    )

    z: float | None = Field(
        default=None,
        description="Nadmorska visina.",
        sa_column=Column(
            type_=Numeric(precision=10, scale=3, asdecimal=False),
            nullable=True,
        ),
    )

    geometry: Geometry = Field(
        default=None,
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type="POINT",
                srid=6316,
                dimension=2,
                spatial_index=True,
                nullable=True,
            ),
        ),
    )


def create_db_and_tables(engine: Engine) -> None:
    """Create db and tables."""
    with engine.begin() as conn:
        if isinstance(conn, Connection):
            for statement in sql_statements:
                conn.execute(statement=statement)
            conn.execute(statement=insert_epsg_3855)
            SQLModel.metadata.create_all(bind=conn)

            conn.execute(statement=create_z_trigger_function)
            conn.execute(statement=create_z_trigger)
            conn.commit()


if __name__ == "__main__":
    ...
