"""Non geometry models."""

from datetime import date  # noqa: TC003

from pydantic import (
    EmailStr,
    NonNegativeFloat,
    PositiveFloat,
    PositiveInt,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy_utils import EmailType
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
    literal,
    text,
)
from sqlmodel._compat import SQLModelConfig

from defaults import default_model_config
from models.constraints import (
    _ekipa_ime,
    _ekipa_prezime,
    ck_all_positive_unique_lokacije_ids,
    ck_antena_frekvencija_positive,
    ck_integer_string_keys_and_values_dubina_gain,
    ck_mb_format,
    ck_nule,
    ck_pib_format,
    ck_projekat_datum_opseg,
    uq_projekat_datum,
)
from models.enums import OnDelete, TipMag, TipMagEnum


class SpatialRefSys(SQLModel, table=True):
    """The default PostGIS created table for coordinate systems."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "spatial_ref_sys"

    srid: PositiveInt = Field(primary_key=True)
    auth_name: str | None = Field(default=None, max_length=256)
    auth_srid: PositiveInt | None = None
    srtext: str | None = Field(default=None, max_length=2048)
    proj4text: str | None = Field(default=None, max_length=2048)


class Ekipa(SQLModel, table=True):
    """Tabela članova ekipe."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "ekipa"
    __table_args__: tuple[dict[str, str],] = ({"comment": str(object=__doc__)},)

    ekipa_id: PositiveInt | None = Field(
        default=None,
        description="ID člana ekipe.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID člana ekipe."},
    )

    ekipa_ime: str = Field(
        description="Ime člana ekipe.",
        max_length=20,
        index=True,
        sa_column_kwargs={"comment": "Ime člana ekipe."},
    )

    ekipa_prezime: str = Field(
        description="Prezime člana ekipe.",
        max_length=20,
        index=True,
        sa_column_kwargs={"comment": "Prezime člana ekipe."},
    )

    ekipa_full_name: str | None = Field(
        default=None,
        description="Puno ime i prezime člana ekipe.",
        max_length=50,
        sa_column=(
            Column(
                String(length=50),
                Computed(
                    sqltext=_ekipa_ime.op(opstring="||")(
                        literal(value=" ", type_=String(length=1)),
                    ).op(opstring="||")(_ekipa_prezime),
                ),
                unique=True,
                index=True,
                comment="Puno ime i prezime člana ekipe.",
            )
        ),
    )


class Investitor(SQLModel, table=True):
    """Tabela investitora."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "investitori"
    __table_args__: tuple[
        CheckConstraint,
        CheckConstraint,
        dict[str, str],
    ] = (
        ck_pib_format,
        ck_mb_format,
        {"comment": str(object=__doc__)},
    )

    investitor_id: PositiveInt | None = Field(
        default=None,
        description="ID investitora.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID investitora."},
    )

    investitor_naziv: str = Field(
        description="Naziv investitora.",
        max_length=255,
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Naziv investitora."},
    )

    investitor_adresa: str | None = Field(
        default=None,
        description="Adresa investitora.",
        max_length=255,
        sa_column_kwargs={"comment": "Adresa investitora."},
    )

    investitor_email: EmailStr | None = Field(
        default=None,
        description="Email adresa investitora.",
        max_length=255,
        sa_column=Column(
            type_=EmailType(length=255),
            unique=True,
            comment="Email adresa investitora.",
        ),
    )

    investitor_pib: str | None = Field(
        default=None,
        description="Poreski investicioni broj investitora.",
        unique=True,
        min_length=9,
        max_length=9,
        sa_column_kwargs={"comment": "Poreski investicioni broj investitora."},
    )

    investitor_maticni_broj: str | None = Field(
        default=None,
        description="Matični broj investitora.",
        unique=True,
        min_length=8,
        max_length=8,
        sa_column_kwargs={"comment": "Matični broj investitora."},
    )

    investitor_broj_telefona: str | None = Field(
        default=None,
        description="Broj telefona investitora.",
        max_length=13,
        sa_column_kwargs={"comment": "Broj telefona investitora."},
    )


class Projekat(SQLModel, table=True):
    """Tabela projekata."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "projekti"
    __table_args__: tuple[
        CheckConstraint,
        CheckConstraint,
        dict[str, str],
    ] = (
        ck_projekat_datum_opseg,
        ck_all_positive_unique_lokacije_ids,
        {"comment": str(object=__doc__)},
    )

    projekat_id: PositiveInt | None = Field(
        default=None,
        description="ID projekta.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID projekta."},
    )

    projekat_naziv: str = Field(
        description="Naziv projekta.",
        max_length=255,
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Naziv projekta."},
    )

    broj_ugovora: str | None = Field(
        default=None,
        description="Broj ugovora.",
        max_length=255,
        sa_column_kwargs={"comment": "Broj ugovora."},
    )

    projekat_start_datum: date | None = Field(
        default=None,
        description="Datum početka projekta.",
        sa_column_kwargs={"comment": "Datum početka projekta."},
    )

    projekat_kraj_datum: date | None = Field(
        default=None,
        description="Datum završetka projekta.",
        sa_column_kwargs={"comment": "Datum završetka projekta."},
    )

    pov_mag: NonNegativeFloat | None = Field(
        default=None,
        description="Ugovorena površina za geomagnetsko snimanje.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Ugovorena površina za geomagnetsko snimanje.",
        ),
    )

    total_pov_mag: NonNegativeFloat | None = Field(
        default=None,
        description="Ukupna snimljena površina za geomagnetsko snimanje.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Ukupna snimljena površina za geomagnetsko snimanje.",
        ),
    )

    pov_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Ugovorena površina za georadarsko snimanje.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Ugovorena površina za georadarsko snimanje.",
        ),
    )

    total_pov_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Ukupna snimljena površina za georadarsko snimanje.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Ukupna snimljena površina za georadarsko snimanje.",
        ),
    )

    pov_elektrika: NonNegativeFloat | None = Field(
        default=None,
        description="Ugovorena površina za snimanje elektrike.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Ugovorena površina za snimanje elektrike.",
        ),
    )

    total_pov_elektrika: NonNegativeFloat | None = Field(
        default=None,
        description="Ukupna snimljena površina za snimanje elektrike.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Ukupna snimljena površina za snimanje elektrike.",
        ),
    )

    pov_profajler: NonNegativeFloat | None = Field(
        default=None,
        description="Ugovorena površina za snimanje profajlerom.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Ugovorena površina za snimanje profajlerom.",
        ),
    )

    total_pov_profajler: NonNegativeFloat | None = Field(
        default=None,
        description="Ukupna snimljena površina za snimanje profajlerom.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Ukupna snimljena površina za snimanje profajlerom.",
        ),
    )

    investitor_id: PositiveInt | None = Field(
        default=None,
        description="ID investitora.",
        foreign_key="investitori.investitor_id",
        index=True,
        sa_column_kwargs={"comment": "ID investitora."},
    )

    lokacije_ids: set[PositiveInt] = Field(
        default_factory=set,
        description="Set lokacija na kojima se izvode radovi.",
        sa_column=Column(
            type_=MutableList.as_mutable(sqltype=postgresql.ARRAY(item_type=Integer)),
            nullable=False,
            server_default=postgresql.array([], type_=Integer),
            comment="Set lokacija na kojima se izvode radovi.",
        ),
    )


class Proizvodjac(SQLModel, table=True):
    """Tabela proizvođača."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "proizvodjaci"
    __table_args__: tuple[dict[str, str]] = ({"comment": str(object=__doc__)},)

    proizvodjac_id: PositiveInt | None = Field(
        default=None,
        description="ID proizvođača.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID proizvođača."},
    )

    proizvodjac_naziv: str = Field(
        description="Naziv proizvođača.",
        max_length=255,
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Naziv proizvođača."},
    )

    proizvodjac_drzava: str | None = Field(
        default=None,
        description="Država proizvođača.",
        max_length=255,
        sa_column_kwargs={"comment": "Država proizvođača."},
    )


class Podesavanje(SQLModel, table=True):
    """Podešavanja za projekat."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "podesavanja"
    __table_args__: tuple[
        CheckConstraint,
        dict[str, str],
    ] = (
        ck_integer_string_keys_and_values_dubina_gain,
        {"comment": str(object=__doc__)},
    )

    settings_id: PositiveInt | None = Field(
        default=None,
        description="ID podešavanja.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID podešavanja."},
    )

    projekat_id: PositiveInt = Field(
        description="ID projekta.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="projekti.projekat_id",
                ondelete=OnDelete.CASCADE.value,
            ),
            nullable=False,
            index=True,
            comment="ID projekta.",
        ),
    )

    color_ramp: PositiveInt = Field(
        default=1,
        description="Kolor rampa za Surfer.",
        sa_column=Column(
            Integer,
            ForeignKey(column="kolor_rampe.kolor_rampa_id"),
            index=True,
            server_default=text(text="1"),
            comment="Kolor rampa za Surfer.",
        ),
    )

    clr_min: float = Field(
        default=-6.0,
        description="Minimalna vrednost za color rampu.",
        sa_column=Column(
            type_=Numeric(
                precision=5,
                scale=2,
                asdecimal=False,
            ),
            nullable=False,
            server_default=text(text="-6.0"),
            comment="Minimalna vrednost za color rampu.",
        ),
    )

    clr_max: float = Field(
        default=6.0,
        description="Maksimalna vrednost za color rampu.",
        sa_column=Column(
            type_=Numeric(
                precision=5,
                scale=2,
                asdecimal=False,
            ),
            nullable=False,
            server_default=text(text="6.0"),
            comment="Maksimalna vrednost za color rampu.",
        ),
    )

    grid_size: PositiveFloat = Field(
        default=0.2,
        description="Veličina ćelije za interpolaciju u Surferu.",
        sa_column=Column(
            type_=Numeric(
                precision=4,
                scale=2,
                asdecimal=False,
            ),
            nullable=False,
            server_default=text(text="0.2"),
            comment="Veličina ćelije za interpolaciju u Surferu.",
        ),
    )

    sken_po_metru: PositiveInt = Field(
        default=300,
        description="Broj skenova po metru za georadar.",
        sa_column=Column(
            type_=Integer,
            nullable=False,
            server_default=text(text="300"),
            comment="Broj skenova po metru za georadar.",
        ),
    )

    sken_po_sekundi: PositiveInt = Field(
        default=100,
        description="Broj skenova po sekundi za georadar.",
        sa_column=Column(
            type_=Integer,
            nullable=False,
            server_default=text(text="100"),
            comment="Broj skenova po sekundi za georadar.",
        ),
    )

    gain_vals: list[int] = Field(
        default_factory=list,
        description="Lista vrednosti pojačanja za georadar.",
        sa_column=Column(
            type_=MutableList.as_mutable(sqltype=postgresql.ARRAY(item_type=Integer)),
            nullable=False,
            server_default=postgresql.array([], type_=Integer),
            comment="Lista vrednosti pojačanja za georadar.",
        ),
    )

    dubina_gain: dict[str, str] = Field(
        default_factory=dict,
        description="Rečnik sa dubinama i odgovarajućim pojačanjem za georadar.",
        sa_column=Column(
            type_=MutableDict.as_mutable(sqltype=postgresql.HSTORE),
            nullable=False,
            server_default=text(text="''::hstore"),
            comment="Rečnik sa dubinama i odgovarajućim pojačanjem za georadar.",
        ),
    )


class Magnetometar(SQLModel, table=True):
    """Tabela magnetometara."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "magnetometri"
    __table_args__: tuple[dict[str, str]] = ({"comment": str(object=__doc__)},)

    mag_id: PositiveInt | None = Field(
        default=None,
        description="ID magnetometra.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID magnetometra."},
    )

    mag_naziv: str = Field(
        description="Interni naziv magnetometra.",
        max_length=255,
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Interni naziv magnetometra."},
    )

    mag_serijski_broj: PositiveInt = Field(
        description="Serijski broj magnetometra.",
        unique=True,
        sa_column_kwargs={"comment": "Serijski broj magnetometra."},
    )

    mag_model: str | None = Field(
        default=None,
        description="Model magnetometra.",
        max_length=255,
        sa_column_kwargs={"comment": "Model magnetometra."},
    )

    mag_tip: TipMag = Field(
        default=TipMag.PROTONSKI_OVERHAUZER.value,
        description="Tip magnetometra (tehnologija).",
        sa_column=Column(
            type_=TipMagEnum,
            nullable=False,
            server_default=text(text=f"'{TipMag.PROTONSKI_OVERHAUZER.value}'"),
            comment="Tip magnetometra (tehnologija).",
        ),
    )

    mag_proizvodjac_id: PositiveInt = Field(
        description="ID proizvođača magnetometra.",
        foreign_key="proizvodjaci.proizvodjac_id",
        index=True,
        sa_column_kwargs={"comment": "ID proizvođača magnetometra."},
    )


class GeoRadar(SQLModel, table=True):
    """Tabela georadara."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "georadari"
    __table_args__: tuple[dict[str, str]] = ({"comment": str(object=__doc__)},)

    gpr_id: PositiveInt | None = Field(
        default=None,
        description="ID georadara.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID georadara."},
    )

    gpr_naziv: str = Field(
        description="Naziv georadara.",
        max_length=255,
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Naziv georadara."},
    )

    gpr_serijski_broj: str | None = Field(
        default=None,
        description="Serijski broj georadara.",
        unique=True,
        sa_column_kwargs={"comment": "Serijski broj georadara."},
    )

    gpr_model: str | None = Field(
        default=None,
        description="Model georadara.",
        max_length=255,
        sa_column_kwargs={"comment": "Model georadara."},
    )

    gpr_proizvodjac_id: PositiveInt | None = Field(
        default=None,
        description="ID proizvođača georadara.",
        foreign_key="proizvodjaci.proizvodjac_id",
        index=True,
        sa_column_kwargs={"comment": "ID proizvođača georadara."},
    )


class Antena(SQLModel, table=True):
    """Tabela antena za georadar."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "antene"
    __table_args__: tuple[
        CheckConstraint,
        dict[str, str],
    ] = (
        ck_antena_frekvencija_positive,
        {"comment": str(object=__doc__)},
    )

    antena_id: PositiveInt | None = Field(
        default=None,
        description="ID antene.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID antene."},
    )

    antena_naziv: str = Field(
        description="Naziv antene.",
        max_length=255,
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Naziv antene."},
    )

    antena_serijski_broj: str | None = Field(
        default=None,
        description="Serijski broj antene.",
        unique=True,
        sa_column_kwargs={"comment": "Serijski broj antene."},
    )

    antena_model: str | None = Field(
        default=None,
        description="Model antene.",
        max_length=255,
        sa_column_kwargs={"comment": "Model antene."},
    )

    antena_proizvodjac_id: PositiveInt | None = Field(
        default=None,
        description="ID proizvođača antene.",
        foreign_key="proizvodjaci.proizvodjac_id",
        index=True,
        sa_column_kwargs={"comment": "ID proizvođača antene."},
    )

    antena_frekvencija: PositiveInt | None = Field(
        default=None,
        description="Frekvencija antene georadara u MHz.",
        sa_column_kwargs={"comment": "Frekvencija antene georadara u MHz."},
    )


class Profajler(SQLModel, table=True):
    """Tabela profajlera."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "profajleri"
    __table_args__: tuple[dict[str, str]] = ({"comment": str(object=__doc__)},)

    profajler_id: PositiveInt | None = Field(
        default=None,
        description="ID profajlera.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID profajlera."},
    )

    profajler_naziv: str = Field(
        description="Naziv profajlera.",
        max_length=255,
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Naziv profajlera."},
    )

    profajler_serijski_broj: str | None = Field(
        default=None,
        description="Serijski broj profajlera.",
        unique=True,
        sa_column_kwargs={"comment": "Serijski broj profajlera."},
    )

    profajler_model: str | None = Field(
        default=None,
        description="Model profajlera.",
        max_length=255,
        sa_column_kwargs={"comment": "Model profajler."},
    )

    profajler_proizvodjac_id: PositiveInt | None = Field(
        default=None,
        description="ID proizvođača profajlera.",
        foreign_key="proizvodjaci.proizvodjac_id",
        index=True,
        sa_column_kwargs={"comment": "ID proizvođača profajlera."},
    )


class PovrsinaPoDatumu(SQLModel, table=True):
    """Tabela površina snimanja."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "povrsine_po_datumu"
    __table_args__: tuple[
        UniqueConstraint,
        dict[str, str],
    ] = (
        uq_projekat_datum,
        {"comment": str(object=__doc__)},
    )

    pov_id: PositiveInt | None = Field(
        default=None,
        description="ID površine snimanja.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID površine snimanja."},
    )

    datum: date | None = Field(
        default=None,
        description="Datum snimanja.",
        sa_column_kwargs={"comment": "Datum snimanja."},
    )

    projekat_id: PositiveInt = Field(
        description="ID projekta.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="projekti.projekat_id",
                ondelete=OnDelete.CASCADE.value,
            ),
            nullable=False,
            index=True,
            comment="ID projekta.",
        ),
    )

    pov_mag: NonNegativeFloat | None = Field(
        default=None,
        description="Dnevna površina snimljena magnetometrom.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Dnevna površina snimljena magnetometrom.",
        ),
    )

    pov_gpr: NonNegativeFloat | None = Field(
        default=None,
        description="Dnevna površina snimljena georadarom.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Dnevna površina snimljena georadarom.",
        ),
    )

    pov_elektrika: NonNegativeFloat | None = Field(
        default=None,
        description="Dnevna površina snimljena elektrikom.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Dnevna površina snimljena elektrikom.",
        ),
    )

    pov_profajler: NonNegativeFloat | None = Field(
        default=None,
        description="Dnevna površina snimljena profajlerom.",
        sa_column=Column(
            type_=Numeric(
                precision=10,
                scale=3,
                asdecimal=False,
            ),
            comment="Dnevna površina snimljena profajlerom.",
        ),
    )


class Nula(SQLModel, table=True):
    """Tabela nula."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "nule"
    __table_args__: tuple[
        CheckConstraint,
        dict[str, str],
    ] = (
        ck_nule,
        {"comment": str(object=__doc__)},
    )

    nule_id: PositiveInt | None = Field(
        default=None,
        description="ID nule.",
        ge=1,
        le=4,
        primary_key=True,
        sa_column_kwargs={"comment": "ID nule."},
    )

    nule_naziv: str = Field(
        description="Nula - početak snimanja.",
        max_length=5,
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Nula - početak snimanja."},
    )


class Lokacija(SQLModel, table=True):
    """Tabela lokacija."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "lokacije"
    __table_args__: tuple[dict[str, str]] = ({"comment": str(object=__doc__)},)

    lokacija_id: PositiveInt | None = Field(
        default=None,
        description="ID lokacije.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID lokacije."},
    )

    lokacija_naziv: str = Field(
        description="Naziv lokacije.",
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Naziv lokacije."},
    )

    projekat_id: PositiveInt = Field(
        description="ID projekta.",
        sa_column=Column(
            Integer,
            ForeignKey(
                column="projekti.projekat_id",
                ondelete=OnDelete.CASCADE.value,
            ),
            nullable=False,
            index=True,
            comment="ID projekta.",
        ),
    )


class KolorRampa(SQLModel, table=True):
    """Tabela kolor rampi za Surfer."""

    model_config: SQLModelConfig = default_model_config
    __tablename__: str = "kolor_rampe"
    __table_args__: tuple[dict[str, str]] = ({"comment": str(object=__doc__)},)

    kolor_rampa_id: PositiveInt | None = Field(
        default=None,
        description="ID kolor rampe.",
        primary_key=True,
        sa_column_kwargs={"comment": "ID kolor rampe."},
    )

    kolor_rampa_naziv: str = Field(
        description="Naziv kolor rampe.",
        unique=True,
        index=True,
        sa_column_kwargs={"comment": "Naziv kolor rampe."},
    )
