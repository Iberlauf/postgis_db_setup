"""Geometry models."""

from datetime import date  # noqa: TC003

from geoalchemy2 import Geometry
from geoalchemy2.functions import (
    ST_X,
    ST_Y,
    ST_Area,
    ST_Length,
)
from pydantic import (  # noqa: TC002
    NonNegativeFloat,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
)
from sqlalchemy import Column, Computed, func
from sqlalchemy.dialects import postgresql
from sqlmodel import (
    Boolean,
    CheckConstraint,
    Double,
    Enum,
    Field,
    Index,
    Integer,
    Numeric,
    SQLModel,
    String,
    cast,
    literal_column,
    text,
)
from sqlmodel._compat import SQLModelConfig  # noqa: TC002

from models.constraints import (
    ck_all_positive,
    ck_file_name_format_gpr,
    ck_linestring_two_points,
    ck_nule,
    ck_polje_naziv_format,
    ck_profil_naziv_format,
    ck_rectangular_polygon,
    ck_right_angles,
    ck_snimak_broj,
    default_model_config,
    uq_projekat_polje_concat_gpr,
    uq_projekat_polje_concat_mag,
    uq_projekat_profil_concat_gpr,
    uq_projekat_profil_concat_mag,
)
from models.enums import (
    GeomType,
    NacinSnimanjaEnum,
)


class Tacke(SQLModel, table=True):
    """Tabela tačaka."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "tacke"
    __table_args__: tuple[dict[str, str]] = ({"comment": str(object=__doc__)},)

    tacka_id: int | None = Field(
        default=None,
        description="ID tačke.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID tačke."},
    )
    tacka_naziv: str = Field(
        description="Naziv tačke.",
        max_length=255,
        index=True,
        sa_column_kwargs={"comment": "Naziv tačke."},
    )
    datum: date | None = Field(
        default=None,
        description="Datum.",
        sa_column_kwargs={"comment": "Datum."},
    )

    x: NonNegativeFloat | None = Field(
        default=None,
        description="X koordinata.",
        sa_column=Column(
            Computed(
                sqltext=ST_X(literal_column(text="geom", type_=Geometry)),
                persisted=True,
            ),
            type_=Numeric(precision=10, scale=3, asdecimal=False),
            nullable=True,
            comment="X koordinata.",
        ),
    )
    y: NonNegativeFloat | None = Field(
        default=None,
        description="Y koordinata.",
        sa_column=Column(
            Computed(
                sqltext=ST_Y(literal_column(text="geom", type_=Geometry)),
                persisted=True,
            ),
            type_=Numeric(precision=10, scale=3, asdecimal=False),
            nullable=True,
            comment="Y koordinata.",
        ),
    )

    z: float | None = Field(
        default=None,
        description="Nadmorska visina.",
        sa_column=Column(
            type_=Numeric(precision=10, scale=3, asdecimal=False),
            nullable=True,
            comment="Nadmorska visina.",
        ),
    )

    geom: Geometry = Field(
        default=None,
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type=GeomType.POINT,
                srid=6316,
                dimension=2,
                spatial_index=True,
            ),
            comment="Geometrijska kolona.",
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
        dict[str, str],
    ] = (
        uq_projekat_polje_concat_mag,
        ck_polje_naziv_format,
        ck_all_positive,
        ck_snimak_broj,
        ck_nule,
        ck_rectangular_polygon,
        ck_right_angles,
        {"comment": str(object=__doc__)},
    )

    polje_id: int | None = Field(
        default=None,
        description="ID polja.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID polja."},
    )

    polje_naziv: str = Field(
        description="Naziv polja.",
        max_length=255,
        index=True,
        sa_column_kwargs={"comment": "Naziv polja."},
    )

    datum: date | None = Field(
        default=None,
        description="Datum.",
        sa_column_kwargs={"comment": "Datum snimanja."},
    )

    snimak_broj: PositiveInt | None = Field(
        default=None,
        description="Broj snimka.",
        le=99,
        sa_column_kwargs={"comment": "Broj snimka."},
    )

    broj_polja: PositiveInt | None = Field(
        default=None,
        description="Broj polja; dobijen iz naziva polja.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=cast(
                    expression=func.substring(
                        literal_column(
                            text="polje_naziv",
                            type_=String,
                        ),
                        r"\d+",
                    ),
                    type_=Integer,
                ),
                persisted=True,
            ),
            comment="Broj polja; dobijen iz naziva polja.",
        ),
    )

    projekat_id: PositiveInt = Field(
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        nullable=False,
        sa_column_kwargs={"comment": "ID projekta."},
    )

    mag_id: PositiveInt = Field(
        description="ID magnetometra.",
        ge=1,
        foreign_key="magnetometri.mag_id",
        index=True,
        sa_column_kwargs={"comment": "ID magnetometra."},
    )

    nule_id: PositiveInt = Field(
        description="Početak snimanja.",
        ge=1,
        le=4,
        foreign_key="nule.nule_id",
        index=True,
        sa_column_kwargs={"comment": "Početak snimanja."},
    )

    ekipa_ids: set[PositiveInt] | None = Field(
        default_factory=set,
        description="Set ID-jeva članova ekipe (mesto many-to-many tabele).",
        min_items=1,
        sa_column=Column(
            type_=postgresql.ARRAY(item_type=Integer),
            comment="Set ID-jeva članova ekipe (mesto many-to-many tabele).",
        ),
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga po kojoj je polje snimljeno.",
        max_length=255,
        sa_column_kwargs={"comment": "Podloga po kojoj je polje snimljeno."},
    )

    shift_z: float = Field(
        default=0.0,
        description="Podešavanje Z-vrednosti.",
        sa_column=Column(
            type_=Numeric(precision=5, scale=2, asdecimal=False),
            server_default=text(text="0.0"),
            nullable=False,
            comment="Podešavanje Z-vrednosti.",
        ),
    )

    pogresni_redovi: set[PositiveInt] | None = Field(
        default_factory=set,
        description="Set pogrešno snimljenih redova.",
        sa_column=Column(
            type_=postgresql.ARRAY(item_type=Integer),
            comment="Set pogrešno snimljenih redova.",
        ),
    )

    promena_znaka: bool = Field(
        default=False,
        description="Promena znaka.",
        sa_column=Column(
            type_=Boolean,
            server_default=text(text="FALSE"),
            comment="Promena znaka.",
        ),
    )

    pov_mag: PositiveFloat | None = Field(
        default=None,
        description="Površina polja magnetometra (sa uračunatim preklapanjem).",
        sa_column=Column(
            Numeric(precision=8, scale=3, asdecimal=False),
            Computed(
                sqltext=func.round(
                    cast(
                        expression=ST_Area(
                            literal_column(
                                text="geom",
                                type_=Geometry,
                            ),
                        ),
                        type_=Numeric(precision=10, scale=3, asdecimal=False),
                    ),
                    3,
                ),
                persisted=True,
            ),
            comment="Površina polja magnetometra (sa uračunatim preklapanjem).",
        ),
    )

    nula_x: PositiveFloat | None = Field(
        default=None,
        description="X koordinata nule polja.",
        sa_column=Column(
            type_=Double,
            comment="X koordinata nule polja.",
        ),
    )

    nula_y: PositiveFloat | None = Field(
        default=None,
        description="Y koordinata nule polja.",
        sa_column=Column(
            type_=Double,
            comment="Y koordinata nule polja.",
        ),
    )

    mag_nula_angle: float | None = Field(
        default=None,
        description="Ugao nule polja u odnosu na sledeći verteks u smeru kazaljke na satu (u radijanima).",  # noqa: E501
        sa_column=Column(
            type_=Double,
            comment="Ugao nule polja u odnosu na sledeći verteks u smeru kazaljke na satu (u radijanima).",  # noqa: E501
        ),
    )

    duzina_profila: PositiveInt | None = Field(
        default=None,
        description="Dužina profila.",
        sa_column_kwargs={
            "comment": "Dužina profila.",
        },
    )

    sirina_polja: PositiveInt | None = Field(
        default=None,
        description="Širina polja.",
        sa_column_kwargs={
            "comment": "Širina polja.",
        },
    )

    geom: Geometry = Field(
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type=GeomType.POLYGON,
                srid=6316,
                dimension=2,
                spatial_index=True,
            ),
            comment="Geometrijska kolona.",
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
        CheckConstraint,
        dict[str, str],
    ] = (
        uq_projekat_polje_concat_gpr,
        ck_polje_naziv_format,
        ck_nule,
        ck_file_name_format_gpr,
        ck_right_angles,
        {"comment": str(object=__doc__)},
    )

    polje_id: int | None = Field(
        default=None,
        description="ID polja.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID polja."},
    )

    polje_naziv: str = Field(
        description="Naziv polja.",
        max_length=255,
        index=True,
        sa_column_kwargs={"comment": "Naziv polja."},
    )

    datum: date | None = Field(
        default=None,
        description="Datum snimanja.",
        sa_column_kwargs={"comment": "Datum snimanja."},
    )

    file_name: str | None = Field(
        default=None,
        description="Naziv fajla.",
        max_length=255,
        sa_column_kwargs={"comment": "Naziv fajla."},
    )

    broj_polja: PositiveInt | None = Field(
        default=None,
        description="Broj polja; dobijen iz naziva polja.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=cast(
                    expression=func.substring(
                        literal_column(
                            text="polje_naziv",
                            type_=String,
                        ),
                        r"\d+",
                    ),
                    type_=Integer,
                ),
                persisted=True,
            ),
            comment="Broj polja; dobijen iz naziva polja.",
        ),
    )

    projekat_id: PositiveInt = Field(
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        index=True,
        sa_column_kwargs={"comment": "ID projekta."},
    )

    nule_id: PositiveInt = Field(
        description="Početak snimanja.",
        ge=1,
        le=4,
        foreign_key="nule.nule_id",
        index=True,
        sa_column_kwargs={"comment": "Početak snimanja."},
    )

    ekipa_ids: set[PositiveInt] | None = Field(
        default_factory=set,
        description="Set ID-jeva članova ekipe (mesto many-to-many tabele).",
        sa_column=Column(
            type_=postgresql.ARRAY(item_type=Integer),
            comment="Set ID-jeva članova ekipe (mesto many-to-many tabele).",
        ),
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga po kojoj je polje snimljeno.",
        max_length=255,
        sa_column_kwargs={"comment": "Podloga po kojoj je polje snimljeno."},
    )

    gpr_id: PositiveInt = Field(
        description="ID georadara.",
        foreign_key="georadari.gpr_id",
        index=True,
        sa_column_kwargs={"comment": "ID georadara."},
    )

    antena_id: PositiveInt | None = Field(
        description="ID antene.",
        foreign_key="antene.antena_id",
        index=True,
        sa_column_kwargs={"comment": "ID antene."},
    )

    nacin_snimanja: Enum = Field(
        default="kolica",
        description="Način snimanja.",
        sa_column=Column(
            type_=NacinSnimanjaEnum,
            nullable=False,
            server_default=text(text="'kolica'"),
            comment="Način snimanja.",
        ),
    )

    pov_gpr: PositiveFloat | None = Field(
        default=None,
        description="Površina polja georadara (sa uračunatim preklapanjem).",
        sa_column=Column(
            Numeric(precision=8, scale=3, asdecimal=False),
            Computed(
                sqltext=func.round(
                    cast(
                        expression=ST_Area(literal_column(text="geom", type_=Geometry)),
                        type_=Numeric(precision=10, scale=3, asdecimal=False),
                    ),
                    3,
                ),
                persisted=True,
            ),
            comment="Površina polja georadara (sa uračunatim preklapanjem).",
        ),
    )

    nula_x: PositiveFloat | None = Field(
        default=None,
        description="X koordinata nule polja.",
        sa_column=Column(
            type_=Double,
            comment="X koordinata nule polja.",
        ),
    )

    nula_y: PositiveFloat | None = Field(
        default=None,
        description="Y koordinata nule polja.",
        sa_column=Column(
            type_=Double,
            comment="Y koordinata nule polja.",
        ),
    )

    gpr_nula_angle: float | None = Field(
        default=None,
        description="Ugao nule polja u odnosu na sledeći verteks u obrnutom smeru kazaljke na satu (u radijanima).",  # noqa: E501
        sa_column=Column(
            type_=Double,
            comment="Ugao nule polja u odnosu na sledeći verteks u obrnutom smeru kazaljke na satu (u radijanima).",  # noqa: E501
        ),
    )

    geom: Geometry = Field(
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type=GeomType.POLYGON,
                srid=6316,
                dimension=2,
                spatial_index=True,
            ),
            comment="Geometrijska kolona.",
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
        CheckConstraint,
        dict[str, str],
    ] = (
        uq_projekat_profil_concat_mag,
        ck_profil_naziv_format,
        ck_snimak_broj,
        ck_linestring_two_points,
        {"comment": str(object=__doc__)},
    )

    profil_id: int | None = Field(
        default=None,
        description="ID profila.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID profila."},
    )

    profil_naziv: str = Field(
        description="Naziv profila.",
        max_length=255,
        index=True,
        sa_column_kwargs={"comment": "Naziv profila."},
    )

    datum: date | None = Field(
        default=None,
        description="Datum snimanja.",
        sa_column_kwargs={"comment": "Datum snimanja."},
    )

    snimak_broj: PositiveInt | None = Field(
        default=None,
        description="Broj snimka.",
        le=99,
        sa_column_kwargs={"comment": "Broj snimka."},
    )

    projekat_id: PositiveInt = Field(
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        index=True,
        sa_column_kwargs={"comment": "ID projekta."},
    )

    mag_id: PositiveInt = Field(
        description="ID magnetometra.",
        foreign_key="magnetometri.mag_id",
        index=True,
        sa_column_kwargs={"comment": "ID magnetometra."},
    )

    ekipa_id: PositiveInt = Field(
        description="ID člana ekipe koji je snimio profil.",
        foreign_key="ekipa.ekipa_id",
        index=True,
        sa_column_kwargs={"comment": "ID člana ekipe koji je snimio profil."},
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga snimanja.",
        max_length=255,
        sa_column_kwargs={"comment": "Podloga snimanja."},
    )

    shift_z: float = Field(
        default=0.0,
        description="Podešavanje Z-vrednosti.",
        sa_column=Column(
            type_=Numeric(precision=5, scale=2, asdecimal=False),
            server_default=text(text="0.0"),
            nullable=False,
            comment="Podešavanje Z-vrednosti.",
        ),
    )

    promena_znaka: bool = Field(
        default=False,
        description="Promena znaka.",
        sa_column=Column(
            type_=Boolean,
            server_default=text(text="FALSE"),
            comment="Promena znaka.",
        ),
    )

    duzina_mag: NonNegativeInt | None = Field(
        default=None,
        description="Dužina snimljenog profila.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=func.round(
                    ST_Length(literal_column(text="geom", type_=Geometry)),
                ),
                persisted=True,
            ),
            comment="Dužina snimljenog profila.",
        ),
    )

    geom: Geometry = Field(
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type=GeomType.LINESTRING,
                srid=6316,
                dimension=2,
                spatial_index=True,
            ),
            comment="Geometrijska kolona.",
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
        dict[str, str],
    ] = (
        uq_projekat_profil_concat_gpr,
        ck_profil_naziv_format,
        ck_file_name_format_gpr,
        {"comment": str(object=__doc__)},
    )

    profil_id: int | None = Field(
        default=None,
        description="ID profila.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID profila."},
    )

    profil_naziv: str = Field(
        description="Naziv profila.",
        max_length=255,
        index=True,
        sa_column_kwargs={"comment": "Naziv profila."},
    )

    datum: date | None = Field(
        default=None,
        description="Datum snimanja.",
        sa_column_kwargs={"comment": "Datum snimanja."},
    )

    file_name: str | None = Field(
        default=None,
        description="Naziv fajla.",
        max_length=255,
        sa_column_kwargs={"comment": "Naziv fajla."},
    )

    projekat_id: PositiveInt = Field(
        description="ID projekta.",
        foreign_key="projekti.projekat_id",
        index=True,
        sa_column_kwargs={"comment": "ID projekta."},
    )

    podloga: str | None = Field(
        default=None,
        description="Podloga snimanja.",
        max_length=255,
        sa_column_kwargs={"comment": "Podloga snimanja."},
    )

    gpr_id: PositiveInt = Field(
        description="ID georadara.",
        foreign_key="georadari.gpr_id",
        index=True,
        sa_column_kwargs={"comment": "ID georadara."},
    )

    antena_id: PositiveInt = Field(
        description="ID antene.",
        foreign_key="antene.antena_id",
        index=True,
        sa_column_kwargs={"comment": "ID antene."},
    )

    ekipa_ids: set[PositiveInt] | None = Field(
        default_factory=set,
        description="Set ID-jeva članova ekipe (mesto many-to-many tabele).",
        sa_column=Column(
            type_=postgresql.ARRAY(item_type=Integer),
            comment="Set ID-jeva članova ekipe (mesto many-to-many tabele).",
        ),
    )

    nacin_snimanja: Enum = Field(
        default="kolica",
        description="Način snimanja.",
        sa_column=Column(
            type_=NacinSnimanjaEnum,
            nullable=False,
            server_default=text(text="'kolica'"),
            comment="Način snimanja.",
        ),
    )

    duzina_gpr: NonNegativeInt | None = Field(
        default=None,
        description="Dužina snimljenog profila.",
        sa_column=Column(
            Integer,
            Computed(
                sqltext=func.round(
                    ST_Length(literal_column(text="geom", type_=Geometry)),
                ),
                persisted=True,
            ),
            comment="Dužina snimljenog profila.",
        ),
    )

    geom: Geometry = Field(
        description="Geometrijska kolona.",
        sa_column=Column(
            type_=Geometry(
                geometry_type=GeomType.LINESTRING,
                srid=6316,
                dimension=2,
                spatial_index=True,
            ),
            comment="Geometrijska kolona.",
        ),
    )
