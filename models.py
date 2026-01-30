"""Models."""

from __future__ import annotations

import datetime

from geoalchemy2 import Geometry
from pydantic import ConfigDict, EmailStr, PositiveFloat
from sqlalchemy import Computed, Engine
from sqlmodel import (
    CheckConstraint,
    Column,
    Field,
    Numeric,
    Relationship,
    SQLModel,
    String,
)


class Ekipa(SQLModel, table=True):
    """Tabela članova ekipe."""

    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    __tablename__: str = "ekipa"
    __table_args__: dict[str, str] = {
        "schema": "public",
    }

    ekipa_id: int | None = Field(
        default=None,
        description="ID člana ekipe.",
        primary_key=True,
    )

    ekipa_ime: str = Field(
        description="Ime člana ekipe.",
        max_length=255,
        unique=True,
        nullable=False,
        index=True,
    )

    ekipa_prezime: str = Field(
        description="prezime člana ekipe.",
        max_length=255,
        unique=True,
        nullable=False,
        index=True,
    )

    ekipa_full_name: str | None = Field(
        default=None,
        description="Puno ime i prezime člana ekipe",
        max_length=255,
        sa_column=(
            Column(
                "ekipa_full_name",
                String(length=255),
                Computed(sqltext="ekipa_ime || '_' || ekipa_prezime"),
            )
        ),
    )


class Investitor(SQLModel, table=True):
    """Tabela investitora."""

    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )

    __tablename__: str = "investitori"
    __table_args__: dict[str, str] = {
        "schema": "public",
    }

    investitor_id: int | None = Field(
        default=None,
        description="ID investitora.",
        primary_key=True,
    )

    investitor_ime: str = Field(
        description="Naziv investitora.",
        max_length=255,
        unique=True,
        nullable=False,
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
        unique_items=True,
    )

    projekti: list[Projekat] = Relationship(back_populates="investitor")


class Projekat(SQLModel, table=True):
    """Tabela projekata."""

    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )

    __tablename__: str = "projekti"
    __table_args__: tuple[CheckConstraint, dict[str, str]] = (
        CheckConstraint(
            sqltext="projekat_start_datum IS NULL "
            "OR projekat_kraj_datum IS NULL "
            "OR projekat_start_datum <= projekat_kraj_datum",
            name="ck_projekat_datum_opseg",
        ),
        {
            "schema": "public",
        },
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
        nullable=False,
        index=True,
    )

    broj_ugovora: str = Field(
        description="Broj ugovora.",
        max_length=255,
        nullable=False,
    )

    projekat_start_datum: datetime.date | None = Field(
        default=None,
        description="Datum početka projekta.",
        nullable=True,
    )

    projekat_kraj_datum: datetime.date | None = Field(
        default=None,
        description="Datum završetka projekta.",
        nullable=True,
    )

    pov_mag: PositiveFloat | None = Field(
        default=None,
        description="Ugovorena površina za geomagnetsko snimanje",
        nullable=True,
    )

    pov_gpr: PositiveFloat | None = Field(
        default=None,
        description="Ugovorena površina za georadarsko snimanje",
        nullable=True,
    )

    investitor_id: int | None = Field(
        default=None,
        description="ID investitora.",
        foreign_key="public.investitori.investitor_id",
        index=True,
    )

    investitor: Investitor | None = Relationship(
        back_populates="projekti",
    )


class ProjectSettings(SQLModel):
    """Podešavanja za projekat."""

    __tablename__: str = "podesavanja"
    __table_args__: dict[str, str] = {"schema": "public"}


class Tacke(SQLModel, table=True):
    """Tabela tačaka."""

    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )

    __tablename__: str = "tacke"
    __table_args__: dict[str, str] = {"schema": "public"}

    tacka_id: int | None = Field(
        default=None,
        description="ID tačke.",
        primary_key=True,
    )
    tacka_ime: str = Field(
        description="Naziv tačke.",
        max_length=255,
        nullable=False,
        index=True,
    )
    datum: datetime.date = Field(
        default_factory=datetime.date.today,
        description="Datum kotiranja.",
    )
    x: float | None = Field(
        default=None,
        description="X koordinata",
        sa_column=Column(type_=Numeric(precision=10, scale=3), nullable=True),
    )
    y: float | None = Field(
        default=None,
        description="Y koordinata",
        sa_column=Column(type_=Numeric(precision=10, scale=3), nullable=True),
    )
    z: float | None = Field(
        default=None,
        description="Nadmorska visina.",
        sa_column=Column(type_=Numeric(precision=10, scale=3), nullable=True),
    )
    geometry: Geometry | None = Field(
        default=None,
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type="POINT",
                srid=6316,
                dimension=3,
                spatial_index=True,
                nullable=True,
            ),
        ),
    )


def create_db_and_tables(engine: Engine) -> None:
    """Create db and tables."""
    SQLModel.metadata.create_all(bind=engine)
