"""Non geometry models."""

from __future__ import annotations

from datetime import date  # noqa: TC003

from pydantic import (  # noqa: TC002
    EmailStr,
    NonNegativeFloat,
    PositiveFloat,
    PositiveInt,
)
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.dialects.postgresql import HSTORE
from sqlmodel import (
    CheckConstraint,
    Column,
    Computed,
    Field,
    ForeignKey,
    Integer,
    Numeric,
    SQLModel,
    String,
    UniqueConstraint,
    text,
)
from sqlmodel._compat import SQLModelConfig  # noqa: TC002

from models.constraints import (
    ck_antena_frekvencija_positive,
    ck_mb_format,
    ck_pib_format,
    ck_projekat_datum_opseg,
    uq_projekat_datum,
)

default_model_config: SQLModelConfig = {
    "arbitrary_types_allowed": True,
    "from_attributes": True,
    "extra": "ignore",
}


class Ekipa(SQLModel, table=True):
    """Tabela članova ekipe."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "ekipa"

    ekipa_id: int | None = Field(
        default=None,
        description="ID člana ekipe.",
        primary_key=True,
    )

    ekipa_ime: str = Field(
        description="Ime člana ekipe.",
        max_length=20,
        index=True,
    )

    ekipa_prezime: str = Field(
        description="prezime člana ekipe.",
        max_length=20,
        index=True,
    )

    ekipa_full_name: str | None = Field(
        default=None,
        description="Puno ime i prezime člana ekipe.",
        max_length=50,
        sa_column=(
            Column(
                String(length=50),
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


class PoljaMagEkipa(SQLModel, table=True):
    """Many-to-many veza između PoljaMag i Ekipa."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "polja_mag_ekipa"

    polje_id: int = Field(
        default=None,
        description="Primary key tabele polja_mag.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="polja_mag.polje_id",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
    )

    ekipa_id: int = Field(
        default=None,
        description="Primary key tabele ekipa.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="ekipa.ekipa_id",
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            primary_key=True,
        ),
    )


class ProfilMagEkipa(SQLModel, table=True):
    """Many-to-many veza između ProfilMag i Ekipa."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "profil_mag_ekipa"

    polje_id: int = Field(
        default=None,
        description="Primary key tabele profili_mag.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="profili_mag.profil_id",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
    )

    ekipa_id: int = Field(
        default=None,
        description="Primary key tabele ekipa.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="ekipa.ekipa_id",
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            primary_key=True,
        ),
    )


class PoljaGprEkipa(SQLModel, table=True):
    """Many-to-many veza između PoljaGpr i Ekipa."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "polja_gpr_ekipa"

    polje_id: int | None = Field(
        default=None,
        description="Primary key tabele polja_gpr.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="polja_gpr.polje_id",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
    )

    ekipa_id: int | None = Field(
        default=None,
        description="Primary key tabele ekipa.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="ekipa.ekipa_id",
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            primary_key=True,
        ),
    )


class ProfilGprEkipa(SQLModel, table=True):
    """Many-to-many veza između ProfilGpr i Ekipa."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "profil_gpr_ekipa"

    polje_id: int = Field(
        default=None,
        description="Primary key tabele profili_gpr.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="profili_gpr.profil_id",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
    )

    ekipa_id: int = Field(
        default=None,
        description="Primary key tabele ekipa.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="ekipa.ekipa_id",
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            primary_key=True,
        ),
    )


class Investitor(SQLModel, table=True):
    """Tabela investitora."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "investitori"
    __table_args__: tuple[CheckConstraint, ...] = (
        ck_pib_format,
        ck_mb_format,
    )

    investitor_id: int | None = Field(
        default=None,
        description="ID investitora.",
        primary_key=True,
    )

    investitor_naziv: str = Field(
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
    investitor_pib: str | None = Field(
        default=None,
        description="Poreski investicioni broj investitora.",
        unique=True,
        min_length=9,
        max_length=9,
    )

    investitor_maticni_broj: str | None = Field(
        default=None,
        description="Matični broj investitora.",
        unique=True,
        min_length=8,
        max_length=8,
    )

    investitor_broj_telefona: str | None = Field(
        default=None,
        description="Broj telefona investitora.",
        max_length=13,
    )


class Projekat(SQLModel, table=True):
    """Tabela projekata."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "projekti"
    __table_args__: tuple[CheckConstraint] = (ck_projekat_datum_opseg,)

    projekat_id: int | None = Field(
        default=None,
        description="ID projekta.",
        primary_key=True,
    )

    projekat_naziv: str = Field(
        description="Naziv projekta.",
        max_length=255,
        unique=True,
        index=True,
    )

    broj_ugovora: str | None = Field(
        default=None,
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
        sa_column=Column(
            type_=Numeric(precision=10, scale=3, asdecimal=False),
        ),
    )

    total_pov_mag: NonNegativeFloat | None = Field(
        default=None,
        description="Ukupna snimljena površina za geomagnetsko snimanje",
        sa_column=Column(
            type_=Numeric(precision=10, scale=3, asdecimal=False),
        ),
    )

    pov_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Ugovorena površina za georadarsko snimanje",
        sa_column=Column(
            type_=Numeric(precision=10, scale=3, asdecimal=False),
        ),
    )

    total_pov_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Ukupna snimljena površina za georadarsko snimanje",
        sa_column=Column(
            type_=Numeric(precision=10, scale=3, asdecimal=False),
        ),
    )

    investitor_id: int | None = Field(
        default=None,
        description="ID investitora.",
        foreign_key="investitori.investitor_id",
        index=True,
    )


class ProjekatEkipa(SQLModel, table=True):
    """Many-to-many veza između Projekat i Ekipa."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "projekat_ekipa"

    projekat_id: int | None = Field(
        default=None,
        description="Primary key tabele polja_gpr.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="projekti.projekat_id",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
    )

    ekipa_id: int | None = Field(
        default=None,
        description="Primary key tabele ekipa.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="ekipa.ekipa_id",
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            primary_key=True,
        ),
    )


class Proizvodjac(SQLModel, table=True):
    """Tabela proizvođača."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "proizvodjaci"

    proizvodjac_id: int | None = Field(
        default=None,
        description="ID proizvođača.",
        primary_key=True,
    )

    proizvodjac_naziv: str = Field(
        description="Naziv proizvođača.",
        max_length=255,
        unique=True,
        index=True,
    )

    proizvodjac_zemlja: str | None = Field(
        default=None,
        description="Zemlja proizvođača.",
        max_length=255,
    )


class Podesavanje(SQLModel, table=True):
    """Podešavanja za projekat."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "podesavanja"

    settings_id: int | None = Field(
        default=None,
        description="ID podešavanja.",
        primary_key=True,
    )

    projekat_id: int = Field(
        description="ID projekta.",
        sa_column=Column(
            Integer,
            ForeignKey(column="projekti.projekat_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )

    color_ramp: str | None = Field(
        default="GrayScale",
        description="Color rampa za Surfer.",
        max_length=20,
        sa_column=Column(
            type_=String(length=20),
            nullable=True,
            server_default=text(text="'GrayScale'"),
        ),
    )

    clr_min: float | None = Field(
        default=-6.0,
        description="Minimalna vrednost za color rampu.",
        sa_column=Column(
            type_=Numeric(precision=5, scale=2, asdecimal=False),
            nullable=True,
            server_default=text(text="-6.0"),
        ),
    )

    clr_max: float | None = Field(
        default=6.0,
        description="Maksimalna vrednost za color rampu.",
        sa_column=Column(
            type_=Numeric(precision=5, scale=2, asdecimal=False),
            nullable=True,
            server_default=text(text="6.0"),
        ),
    )

    grid_size: PositiveFloat | None = Field(
        default=0.2,
        description="Veličina ćelije za interpolaciju u Surferu.",
        sa_column=Column(
            type_=Numeric(precision=2, scale=2, asdecimal=False),
            nullable=True,
            server_default=text(text="0.2"),
        ),
    )

    sken_po_metru: PositiveInt | None = Field(
        default=300,
        description="Broj skenova po metru za georadar.",
        sa_column=Column(
            type_=Integer,
            nullable=True,
            server_default=text(text="300"),
        ),
    )

    sken_po_sekundi: PositiveInt | None = Field(
        default=100,
        description="Broj skenova po sekundi za georadar.",
        sa_column=Column(
            type_=Integer,
            nullable=True,
            server_default=text(text="100"),
        ),
    )

    gain_vals: list[int] | None = Field(
        default_factory=list,
        description="Lista vrednosti pojačanja za georadar.",
        sa_column=Column(
            type_=PG_ARRAY(item_type=Integer),
            nullable=True,
        ),
    )

    dubina_gain: dict[str, str] | None = Field(
        default_factory=dict,
        description="Rečnik sa dubinama i odgovarajućim pojačanjem za georadar.",
        sa_column=Column(type_=HSTORE),
    )


class Magnetometar(SQLModel, table=True):
    """Tabela magnetometara."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "magnetometri"

    mag_id: int | None = Field(
        default=None,
        description="ID magnetometra.",
        primary_key=True,
    )
    mag_naziv: str = Field(
        description="Naziv magnetometra.",
        max_length=255,
        unique=True,
        index=True,
    )

    mag_serijski_broj: PositiveInt = Field(
        description="Serijski broj magnetometra.",
        unique=True,
    )

    mag_model: str | None = Field(
        default=None,
        description="Model magnetometra.",
        max_length=255,
    )

    mag_proizvodjac_id: int = Field(
        description="ID proizvođača magnetometra.",
        foreign_key="proizvodjaci.proizvodjac_id",
        index=True,
    )


class GeoRadar(SQLModel, table=True):
    """Tabela georadara."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "georadari"

    gpr_id: int | None = Field(
        default=None,
        description="ID georadara.",
        primary_key=True,
    )

    gpr_naziv: str = Field(
        description="Naziv georadara.",
        max_length=255,
        unique=True,
        index=True,
    )

    gpr_serijski_broj: str | None = Field(
        default=None,
        description="Serijski broj georadara.",
        unique=True,
    )

    gpr_model: str | None = Field(
        default=None,
        description="Model georadara.",
        max_length=255,
    )

    gpr_proizvodjac_id: int | None = Field(
        default=None,
        description="ID proizvođača georadara.",
        foreign_key="proizvodjaci.proizvodjac_id",
        index=True,
    )


class Antena(SQLModel, table=True):
    """Tabela antena za georadar."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "antene"
    __table_args__: tuple[CheckConstraint] = (ck_antena_frekvencija_positive,)

    antena_id: int | None = Field(
        default=None,
        description="ID antene.",
        primary_key=True,
    )
    antena_naziv: str = Field(
        description="Naziv antene.",
        max_length=255,
        unique=True,
        index=True,
    )
    antena_serijski_broj: str | None = Field(
        default=None,
        description="Serijski broj antene georadara.",
        unique=True,
    )

    antena_model: str | None = Field(
        default=None,
        description="Model georadara.",
        max_length=255,
    )

    antena_proizvodjac_id: int | None = Field(
        default=None,
        description="ID proizvođača antene georadara.",
        foreign_key="proizvodjaci.proizvodjac_id",
        index=True,
    )

    antena_frekvencija: PositiveInt | None = Field(
        default=None,
        description="Frekvencija antene georadara u MHz.",
    )


class PovrsinaPoDatumu(SQLModel, table=True):
    """Tabela površina snimanja."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "povrsine_po_datumu"
    __table_args__: tuple[UniqueConstraint] = (uq_projekat_datum,)

    pov_id: int | None = Field(
        default=None,
        description="ID površine snimanja.",
        primary_key=True,
    )

    datum: date | None = Field(
        default=None,
        description="Datum snimanja.",
    )

    projekat_id: int = Field(
        description="ID projekta.",
        sa_column=Column(
            Integer,
            ForeignKey(column="projekti.projekat_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )

    pov_mag: NonNegativeFloat | None = Field(
        default=None,
        description="Površina snimljena magnetometrom.",
        sa_column=Column(
            type_=Numeric(precision=10, scale=3, asdecimal=False),
        ),
    )

    pov_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Površina snimljena georadarom.",
        sa_column=Column(
            type_=Numeric(precision=10, scale=3, asdecimal=False),
        ),
    )


class Nula(SQLModel, table=True):
    """Tabela normalizovanih koordinata vertikala pravougaonika."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "nule"

    nule_id: int | None = Field(
        default=None,
        description="ID vertikala.",
        primary_key=True,
    )

    nule_naziv: str = Field(
        description="Nula - početak snimanja.",
        max_length=5,
        unique=True,
        index=True,
    )
