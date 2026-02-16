"""Geometry models."""

from __future__ import annotations

from datetime import date  # noqa: TC003

from geoalchemy2 import Geometry
from geoalchemy2.functions import (
    ST_X,
    ST_Y,
    ST_Area,
    ST_Length,
    ST_MakeValid,
    ST_UnaryUnion,
)
from pydantic import NonNegativeFloat, PositiveInt  # noqa: TC002
from sqlalchemy import Column, Computed, func
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlmodel import (
    CheckConstraint,
    Date,
    Enum,
    Field,
    Index,
    Integer,
    Numeric,
    SQLModel,
    cast,
    literal_column,
    text,
)
from sqlmodel._compat import SQLModelConfig  # noqa: TC002

from models.constraints import (
    check_rectangular_polygon,
    ck_all_positive,
    ck_file_name_format_gpr,
    ck_file_name_format_mag,
    ck_polje_naziv_format,
    ck_profil_naziv_format,
    ck_shift_x_non_negative,
    ck_shift_y_non_negative,
    uq_projekat_polje_concat_gpr,
    uq_projekat_polje_concat_mag,
    uq_projekat_profil_concat_gpr,
    uq_projekat_profil_concat_mag,
)
from models.enums import NacinSnimanjaEnum, NulaEnum

default_model_config: SQLModelConfig = {
    "arbitrary_types_allowed": True,
    "from_attributes": True,
    "extra": "ignore",
}


class Tacke(SQLModel, table=True):
    """Tabela tačaka."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "tacke"

    tacka_id: int | None = Field(
        default=None,
        description="ID tačke.",
        primary_key=True,
    )
    tacka_naziv: str = Field(
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


class PoljaMag(SQLModel, table=True):
    """PoljaMag."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "polja_mag"
    __table_args__: tuple[
        Index,
        CheckConstraint,
        CheckConstraint,
        CheckConstraint,
        CheckConstraint,
        CheckConstraint,
        CheckConstraint,
    ] = (
        uq_projekat_polje_concat_mag,
        ck_polje_naziv_format,
        ck_file_name_format_mag,
        ck_shift_x_non_negative,
        ck_shift_y_non_negative,
        ck_all_positive,
        check_rectangular_polygon,
    )

    polje_id: int | None = Field(
        default=None,
        description="ID polja.",
        primary_key=True,
    )

    polje_naziv: str = Field(
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

    broj_polja: PositiveInt | None = Field(
        default=None,
        description="Broj polja.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=cast(
                    expression=func.substring(
                        literal_column(text="polje_naziv"),
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

    mag_id: int | None = Field(
        default=None,
        description="ID magnetometra.",
        foreign_key="magnetometri.mag_id",
        index=True,
    )

    nule: str | None = Field(
        default=None,
        description="Početak snimanja.",
        max_length=5,
        sa_column=Column(
            type_=NulaEnum,
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

    pogresni_redovi: set[PositiveInt] | None = Field(
        default_factory=set,
        description="Set pogrešno snimljenih redova.",
        sa_column=Column(
            type_=PG_ARRAY(item_type=Integer),
            nullable=True,
        ),
    )

    pov_mag: NonNegativeFloat | None = Field(
        default=None,
        description="Površina polja magnetometra (sa uračunatim preklapanjem).",
        sa_column=Column(
            Numeric,
            Computed(
                sqltext=func.round(
                    cast(
                        expression=ST_Area(
                            ST_MakeValid(
                                ST_UnaryUnion(literal_column(text="geometry")),
                            ),
                        ),
                        type_=Numeric,
                    ),
                    3,
                ),
                persisted=True,
            ),
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


class PoljaGpr(SQLModel, table=True):
    """PoljaGPR."""

    model_config: SQLModelConfig = default_model_config

    __tablename__: str = "polja_gpr"
    __table_args__: tuple[Index, CheckConstraint, CheckConstraint] = (
        uq_projekat_polje_concat_gpr,
        ck_polje_naziv_format,
        ck_file_name_format_gpr,
    )

    polje_id: int | None = Field(
        default=None,
        description="ID polja.",
        primary_key=True,
    )

    polje_naziv: str = Field(
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

    broj_polja: PositiveInt | None = Field(
        default=None,
        description="Broj polja.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=cast(
                    expression=func.substring(
                        literal_column(text="polje_naziv"),
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

    nule: str | None = Field(
        default=None,
        description="Početak snimanja.",
        max_length=5,
        sa_column=Column(
            type_=NulaEnum,
        ),
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga snimanja.",
        max_length=255,
    )

    gpr_id: int | None = Field(
        default=None,
        description="ID georadara.",
        foreign_key="georadari.gpr_id",
        index=True,
    )

    antena_id: int | None = Field(
        default=None,
        description="ID antene.",
        foreign_key="antene.antena_id",
        index=True,
    )

    nacin_snimanja: Enum = Field(
        default="kolica",
        description="Način snimanja.",
        sa_column=Column(
            type_=NacinSnimanjaEnum,
            server_default=text(text="'kolica'"),
        ),
    )

    pov_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Površina polja georadara (sa uračunatim preklapanjem).",
        sa_column=Column(
            Numeric,
            Computed(
                sqltext=func.round(
                    cast(
                        expression=ST_Area(
                            ST_MakeValid(
                                ST_UnaryUnion(literal_column(text="geometry")),
                            ),
                        ),
                        type_=Numeric,
                    ),
                    3,
                ),
                persisted=True,
            ),
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


class ProfilMag(SQLModel, table=True):
    """ProfiliMag."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "profili_mag"
    __table_args__: tuple[
        Index,
        CheckConstraint,
        CheckConstraint,
    ] = (
        uq_projekat_profil_concat_mag,
        ck_profil_naziv_format,
        ck_file_name_format_mag,
    )

    profil_id: int | None = Field(
        default=None,
        description="ID profila.",
        primary_key=True,
    )

    profil_naziv: str = Field(
        description="Naziv profila.",
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

    projekat_id: int | None = Field(
        default=None,
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        index=True,
    )

    mag_id: int | None = Field(
        default=None,
        description="ID magnetometra.",
        foreign_key="magnetometri.mag_id",
        index=True,
    )

    snimio: int = Field(
        description="ID člana ekipe koji je snimio polje.",
        foreign_key="ekipa.ekipa_id",
        index=True,
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga snimanja.",
        max_length=255,
    )

    duzina_mag: NonNegativeFloat | None = Field(
        default=None,
        description="Dužina snimljenog profila.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=ST_Length(literal_column(text="geometry")),
                persisted=True,
            ),
        ),
    )

    geometry: Geometry = Field(
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type="LINESTRING",
                srid=6316,
                dimension=2,
                spatial_index=True,
            ),
        ),
    )


class ProfilGpr(SQLModel, table=True):
    """ProfiliGPR."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "profili_gpr"
    __table_args__: tuple[Index, CheckConstraint, CheckConstraint] = (
        uq_projekat_profil_concat_gpr,
        ck_profil_naziv_format,
        ck_file_name_format_gpr,
    )

    profil_id: int | None = Field(
        default=None,
        description="ID profila.",
        primary_key=True,
    )

    profil_naziv: str = Field(
        description="Naziv profila.",
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

    projekat_id: int | None = Field(
        default=None,
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        index=True,
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga snimanja.",
        max_length=255,
    )

    gpr_id: int | None = Field(
        default=None,
        description="ID georadara.",
        foreign_key="georadari.gpr_id",
        index=True,
    )

    antena_id: int | None = Field(
        default=None,
        description="ID antene.",
        foreign_key="antene.antena_id",
        index=True,
    )

    nacin_snimanja: Enum = Field(
        default="kolica",
        description="Način snimanja.",
        sa_column=Column(
            type_=NacinSnimanjaEnum,
            server_default=text(text="'kolica'"),
        ),
    )

    duzina_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Dužina snimljenog profila.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=ST_Length(literal_column(text="geometry")),
                persisted=True,
            ),
        ),
    )

    geometry: Geometry = Field(
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type="LINESTRING",
                srid=6316,
                dimension=2,
                spatial_index=True,
            ),
        ),
    )
