"""Models."""

from __future__ import annotations

from datetime import date  # noqa: TC003

from geoalchemy2 import Geometry
from geoalchemy2.functions import (
    ST_X,
    ST_Y,
    ST_Area,
    ST_NPoints,
    ST_OrientedEnvelope,
)
from pydantic import EmailStr, NonNegativeFloat, PositiveInt  # noqa: TC002
from sqlalchemy import Column, Computed, Connection, Engine, func
from sqlmodel import (
    CheckConstraint,
    Date,
    Enum,
    Field,
    Integer,
    Numeric,
    Relationship,  # noqa: F401
    Session,
    SQLModel,
    String,
    and_,
    cast,
    literal_column,
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
                String(length=100),
                Computed(
                    sqltext="""--sql
                         ekipa_ime || ' ' || ekipa_prezime
                         """,
                ),
                unique=True,
                index=True,
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
    investitor_pib: PositiveInt | None = Field(
        default=None,
        description="PIB investitora.",
        unique=True,
    )

    investitor_maticni_broj: PositiveInt | None = Field(
        default=None,
        description="Matični broj investitora.",
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

    investitor_id: int | None = Field(
        default=None,
        description="ID investitora.",
        foreign_key="investitori.investitor_id",
        index=True,
    )

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
    tacka_datum: date | None = Field(
        description="Datum kotiranja.",
        sa_column=Column(
            type_=Date,
            server_default=func.current_date(),
            nullable=True,
        ),
    )

    x: NonNegativeFloat | None = Field(
        default=None,
        description="X koordinata",
        sa_column=Column(
            Computed(sqltext=ST_X(literal_column(text="geometry")), persisted=True),
            type_=Numeric(precision=10, scale=3, asdecimal=False),
            nullable=True,
        ),
    )
    y: NonNegativeFloat | None = Field(
        default=None,
        description="Y koordinata",
        sa_column=Column(
            Computed(sqltext=ST_Y(literal_column(text="geometry")), persisted=True),
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


class Uredjaj(SQLModel, table=True):
    """Tabela uređaja."""

    model_config: SQLModelConfig = {
        "arbitrary_types_allowed": True,
        "from_attributes": True,
    }
    __tablename__: str = "uredjaji"

    uredjaj_id: int | None = Field(
        default=None,
        description="ID uređaja.",
        primary_key=True,
    )
    uredjaj_ime: str = Field(
        description="Naziv uređaja.",
        max_length=255,
        unique=True,
        index=True,
    )
    uredjaj_serijski_broj: PositiveInt = Field(
        description="Serijski broj uređaja.",
        unique=True,
    )


class PoljaMag(SQLModel, table=True):
    """PoljaMag."""

    model_config: SQLModelConfig = {
        "arbitrary_types_allowed": True,
        "from_attributes": True,
    }

    __tablename__: str = "polja_mag"
    __table_args__: tuple[CheckConstraint, ...] = (
        CheckConstraint(
            sqltext="""--sql
            polje_ime ~ '^Polje \\d+$|^\\d+[a-z]+$'
            """,
            name="ck_polje_ime_format",
        ),
        CheckConstraint(
            sqltext="""--sql
            file_name ~ '^\\d{2}survey\\.wg$'
            """,
            name="ck_filename_format",
        ),
        CheckConstraint(
            sqltext="""--sql
            shift_x >= 0
            """,
            name="ck_shift_x_non_negative",
        ),
        CheckConstraint(
            sqltext="""--sql
            shift_y >= 0
            """,
            name="ck_shift_y_non_negative",
        ),
        CheckConstraint(
            and_(
                ST_NPoints(literal_column(text="geometry", type_=Geometry)) == 5,
                func.abs(
                    1
                    - ST_Area(literal_column(text="geometry", type_=Geometry))
                    / ST_Area(
                        ST_OrientedEnvelope(
                            literal_column(text="geometry", type_=Geometry),
                        ),
                    ),
                )
                < 0.0001,
            ),
            name="check_rectangular_polygon",
        ),
    )

    polje_id: int | None = Field(
        default=None,
        description="ID polja.",
        primary_key=True,
    )

    polje_ime: str = Field(
        description="Naziv polja.",
        max_length=255,
        index=True,
    )

    datum: date | None = Field(
        description="Datum snimanja.",
        sa_column=Column(
            type_=Date,
            server_default=func.current_date(),
            nullable=True,
        ),
    )

    file_name: str | None = Field(
        default=None,
        description="Naziv fajla.",
        max_length=255,
    )

    povrsina: NonNegativeFloat | None = Field(
        default=None,
        description="Površina polja.",
        sa_column=Column(
            Computed(sqltext=ST_Area(literal_column(text="geometry")), persisted=True),
            type_=Numeric(precision=10, scale=3, asdecimal=False),
            nullable=True,
        ),
    )

    broj_polja: int | None = Field(
        default=None,
        description="Broj polja.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=cast(
                    expression=func.substring(
                        literal_column(text="polje_ime"),
                        r"\d+",
                    ),
                    type_=Integer,
                ),
                persisted=True,
            ),
        ),
    )

    projekat_id: int | None = Field(
        default=None,
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        index=True,
    )

    uredjaj_id: int | None = Field(
        default=None,
        description="ID uređaja.",
        foreign_key="uredjaji.uredjaj_id",
        index=True,
    )

    nule: str | None = Field(
        default=None,
        description="Početak snimanja.",
        max_length=5,
        sa_column=Column(
            type_=Enum(
                "sever",
                "jug",
                "istok",
                "zapad",
                name="uredjaj_enum",
                metadata=SQLModel.metadata,
            ),
        ),
    )

    snimio: int | None = Field(
        default=None,
        description="ID člana ekipe koji je snimio polje.",
        foreign_key="ekipa.ekipa_id",
        index=True,
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga snimanja.",
        max_length=255,
    )

    shift_x: NonNegativeFloat | None = Field(
        default=0,
        description="Pomeranje u desno.",
        ge=0,
        sa_column=Column(
            type_=Numeric(precision=5, scale=2, asdecimal=False),
            server_default=text(text="0.0"),
            nullable=False,
        ),
    )

    shift_y: NonNegativeFloat | None = Field(
        default=0.0,
        description="Pomeranje na gore.",
        ge=0.0,
        sa_column=Column(
            type_=Numeric(precision=5, scale=2, asdecimal=False),
            server_default=text(text="0.0"),
            nullable=False,
        ),
    )

    shift_z: float | None = Field(
        default=0.0,
        description="Podešavanje z.",
        sa_column=Column(
            type_=Numeric(precision=5, scale=2, asdecimal=False),
            server_default=text(text="0.0"),
            nullable=False,
        ),
    )

    geometry: Geometry = Field(
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type="POLYGON",
                srid=6316,
                dimension=2,
                spatial_index=True,
            ),
        ),
    )


clan_1: Ekipa = Ekipa(
    ekipa_ime="Željko",
    ekipa_prezime="Jovanović",
)
clan_2: Ekipa = Ekipa(
    ekipa_ime="Igor",
    ekipa_prezime="Milošević",
)
clan_3: Ekipa = Ekipa(
    ekipa_ime="Ivan",
    ekipa_prezime="Marjanović",
)
clan_4: Ekipa = Ekipa(
    ekipa_ime="Vladimir",
    ekipa_prezime="Miletić",
)

uredjaj_stari: Uredjaj = Uredjaj(
    uredjaj_ime="stari",
    uredjaj_serijski_broj=3111330,
)

uredjaj_novi: Uredjaj = Uredjaj(
    uredjaj_ime="novi",
    uredjaj_serijski_broj=6017391,
)

default_list: list[Ekipa | Uredjaj] = [
    clan_1,
    clan_2,
    clan_3,
    clan_4,
    uredjaj_stari,
    uredjaj_novi,
]


def create_db_and_tables(engine: Engine) -> None:
    """Create db and tables.

    Args:
        engine (Engine): SQLAlchemy engine.

    """
    with engine.begin() as conn:
        if isinstance(conn, Connection):
            for statement in sql_statements:
                conn.execute(statement=statement)
            conn.execute(statement=insert_epsg_3855)
            SQLModel.metadata.create_all(bind=conn)

            conn.execute(statement=create_z_trigger_function)
            conn.execute(statement=create_z_trigger)
            conn.commit()


def add_defaults(engine: Engine) -> None:
    """Add default values to tables.

    Args:
        engine (Engine): SQLAlchemy engine.

    """
    with Session(bind=engine) as session:
        session.add_all(
            instances=default_list,
        )
        session.commit()
        for instance in default_list:
            session.refresh(instance=instance)


if __name__ == "__main__":
    ...
