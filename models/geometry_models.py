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
from pydantic import NonNegativeFloat, PositiveFloat, PositiveInt  # noqa: TC002
from sqlalchemy import Column, Computed, func
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlmodel import (
    CheckConstraint,
    Double,
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
    ck_all_positive,
    ck_file_name_format_gpr,
    ck_linestring_two_points,
    ck_polje_naziv_format,
    ck_profil_naziv_format,
    ck_rectangular_polygon,
    ck_right_angles,
    ck_shift_x_non_negative,
    ck_shift_y_non_negative,
    uq_projekat_polje_concat_gpr,
    uq_projekat_polje_concat_mag,
    uq_projekat_profil_concat_gpr,
    uq_projekat_profil_concat_mag,
)
from models.enums import (
    NacinSnimanjaEnum,
)

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
    datum: date | None = Field(
        default=None,
        description="Datum kotiranja.",
    )

    x: NonNegativeFloat | None = Field(
        default=None,
        description="X koordinata",
        sa_column=Column(
            Computed(
                sqltext=ST_X(ST_MakeValid(literal_column(text="geom"))),
                persisted=True,
            ),
            type_=Numeric(precision=10, scale=3, asdecimal=False),
            nullable=True,
        ),
    )
    y: NonNegativeFloat | None = Field(
        default=None,
        description="Y koordinata",
        sa_column=Column(
            Computed(
                sqltext=ST_Y(ST_MakeValid(literal_column(text="geom"))),
                persisted=True,
            ),
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

    geom: Geometry = Field(
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
        ck_shift_x_non_negative,
        ck_shift_y_non_negative,
        ck_all_positive,
        ck_rectangular_polygon,
        ck_right_angles,
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
        default=None,
        description="Datum snimanja.",
    )

    snimak_broj: PositiveInt | None = Field(
        default=None,
        description="Broj snimka.",
        le=99,
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

    projekat_id: int = Field(
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        nullable=False,
    )

    mag_id: int = Field(
        description="ID magnetometra.",
        ge=1,
        foreign_key="magnetometri.mag_id",
        index=True,
    )

    nule_id: int = Field(
        description="Početak snimanja.",
        ge=1,
        le=4,
        foreign_key="nule.nule_id",
        index=True,
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga snimanja.",
        max_length=255,
    )

    shift_x: NonNegativeFloat = Field(
        default=0.0,
        description="Pomeranje u desno.",
        sa_column=Column(
            type_=Numeric(precision=5, scale=2, asdecimal=False),
            server_default=text(text="0.0"),
            nullable=False,
        ),
    )

    shift_y: NonNegativeFloat = Field(
        default=0.0,
        description="Pomeranje na gore.",
        sa_column=Column(
            type_=Numeric(precision=5, scale=2, asdecimal=False),
            server_default=text(text="0.0"),
            nullable=False,
        ),
    )

    shift_z: float = Field(
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
        ),
    )

    pov_mag: PositiveFloat | None = Field(
        default=None,
        description="Površina polja magnetometra (sa uračunatim preklapanjem).",
        sa_column=Column(
            Numeric,
            Computed(
                sqltext=func.round(
                    cast(
                        expression=ST_Area(
                            ST_MakeValid(
                                ST_UnaryUnion(literal_column(text="geom")),
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

    nula_x: PositiveFloat | None = Field(
        default=None,
        description="X koodinata nule polja.",
        sa_column=Column(
            type_=Double,
        ),
    )

    nula_y: PositiveFloat | None = Field(
        default=None,
        description="Y koodinata nule polja.",
        sa_column=Column(
            type_=Double,
        ),
    )

    mag_nula_angle: float | None = Field(
        default=None,
        description="Ugao nule polja u odnosu na sledeći verteks u smeru kazaljke na satu (u radijanima).",  # noqa: E501
        sa_column=Column(
            type_=Double,
        ),
    )
    duzina_profila: PositiveInt | None = Field(
        default=None,
        description="Dužina profila.",
    )

    sirina_profila: PositiveInt | None = Field(
        default=None,
        description="Širina profila.",
    )

    geom: Geometry = Field(
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
    __table_args__: tuple[
        Index,
        CheckConstraint,
        CheckConstraint,
        CheckConstraint,
    ] = (
        uq_projekat_polje_concat_gpr,
        ck_polje_naziv_format,
        ck_file_name_format_gpr,
        ck_right_angles,
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
        default=None,
        description="Datum snimanja.",
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

    projekat_id: int = Field(
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        index=True,
    )

    nule_id: int = Field(
        description="Početak snimanja.",
        ge=1,
        le=4,
        foreign_key="nule.nule_id",
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga snimanja.",
        max_length=255,
    )

    gpr_id: int = Field(
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
            nullable=False,
            server_default=text(text="'kolica'"),
        ),
    )

    pov_gpr: PositiveFloat | None = Field(
        default=None,
        description="Površina polja georadara (sa uračunatim preklapanjem).",
        sa_column=Column(
            Numeric,
            Computed(
                sqltext=func.round(
                    cast(
                        expression=ST_Area(
                            ST_MakeValid(
                                ST_UnaryUnion(literal_column(text="geom")),
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

    nula_x: PositiveFloat | None = Field(
        default=None,
        description="X koodinata nule polja.",
        sa_column=Column(
            type_=Double,
        ),
    )
    nula_y: PositiveFloat | None = Field(
        default=None,
        description="Y koodinata nule polja.",
        sa_column=Column(
            type_=Double,
        ),
    )

    gpr_nula_angle: float | None = Field(
        default=None,
        description="Ugao nule polja u odnosu na sledeći verteks u obrnutom smeru kazaljke na satu (u radijanima).",  # noqa: E501
        sa_column=Column(
            type_=Double,
        ),
    )

    geom: Geometry = Field(
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
        ck_linestring_two_points,
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
        default=None,
        description="Datum snimanja.",
    )

    survey_number: PositiveInt | None = Field(
        default=None,
        description="Broj snimka.",
        le=99,
    )

    projekat_id: int = Field(
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        index=True,
    )

    mag_id: int = Field(
        default=None,
        description="ID magnetometra.",
        ge=1,
        le=4,
        foreign_key="magnetometri.mag_id",
        index=True,
    )

    ekipa_id: int = Field(
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

    duzina_mag: NonNegativeFloat | None = Field(
        default=None,
        description="Dužina snimljenog profila.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=ST_Length(ST_MakeValid(literal_column(text="geom"))),
                persisted=True,
            ),
        ),
    )

    geom: Geometry = Field(
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
    __table_args__: tuple[
        Index,
        CheckConstraint,
        CheckConstraint,
    ] = (
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

    datum: date = Field(
        default=None,
        description="Datum snimanja.",
    )

    file_name: str | None = Field(
        default=None,
        description="Naziv fajla.",
        max_length=255,
    )

    projekat_id: int = Field(
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

    gpr_id: int = Field(
        description="ID georadara.",
        foreign_key="georadari.gpr_id",
        index=True,
    )

    antena_id: int = Field(
        description="ID antene.",
        foreign_key="antene.antena_id",
        index=True,
    )

    nacin_snimanja: Enum = Field(
        default="kolica",
        description="Način snimanja.",
        sa_column=Column(
            type_=NacinSnimanjaEnum,
            nullable=False,
            server_default=text(text="'kolica'"),
        ),
    )

    duzina_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Dužina snimljenog profila.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=ST_Length(ST_MakeValid(literal_column(text="geom"))),
                persisted=True,
            ),
        ),
    )

    geom: Geometry = Field(
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
