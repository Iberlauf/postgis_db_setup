"""Enums."""

from enum import StrEnum, auto

from sqlalchemy import Enum as SAEnum
from sqlalchemy import event
from sqlmodel import DDL, SQLModel


# tipovi geometrija
class GeomType(StrEnum):
    """Geometry type enum."""

    GEOMETRY = "GEOMETRY"
    POINT = "POINT"
    LINESTRING = "LINESTRING"
    POLYGON = "POLYGON"
    MULTIPOINT = "MULTIPOINT"
    MULTILINESTRING = "MULTILINESTRING"
    MULTIPOLYGON = "MULTIPOLYGON"
    GEOMETRYCOLLECTION = "GEOMETRYCOLLECTION"
    CURVE = "CURVE"


# PostgreSQL ondelete i onupdate
class OnDelete(StrEnum):
    """PostgreSQL ondelete."""

    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
    RESTRICT = "RESTRICT"


class OnUpdate(StrEnum):
    """PostgreSQL onupdate."""

    CASCADE = "CASCADE"
    DELETE = "DELETE"
    RESTRICT = "RESTRICT"


# način snimanja
class NacinSnimanja(StrEnum):
    """Način snimanja."""

    KOLICA = "kolica"
    RUCNO = "ručno"


NacinSnimanjaEnum: SAEnum = SAEnum(
    NacinSnimanja,
    name="nacin_snimanja_enum",
    metadata=SQLModel.metadata,
    values_callable=lambda x: [e.value for e in x if isinstance(e, NacinSnimanja)],
)

nacin_snimanja_vals: str = " ili ".join(e.value for e in NacinSnimanja)
nacin_snimanja_doc: str = (
    str(object=NacinSnimanja.__doc__).replace(".", ":").replace("'", "''")
)
nacin_snimanja_comment: DDL = DDL(
    statement=f"""--sql
COMMENT ON TYPE {NacinSnimanjaEnum.name} IS '{nacin_snimanja_doc} {nacin_snimanja_vals}.'
""",  # noqa: E501
)


# tip magnetometra
class TipMag(StrEnum):
    """Tip magnetometra enum."""

    PROTONSKI_OVERHAUZER = auto()
    FLUKSNI = auto()
    CEZIJUMSKI = auto()


TipMagEnum: SAEnum = SAEnum(
    TipMag,
    name="tip_mag_enum",
    metadata=SQLModel.metadata,
    values_callable=lambda x: [e.value for e in x if isinstance(e, TipMag)],
)

tip_mag_doc: str = str(object=TipMag.__doc__).replace("'", "''")
tip_mag_comment: DDL = DDL(
    statement=f"""--sql
COMMENT ON TYPE {TipMagEnum.name} IS '{tip_mag_doc}'
""",
)


# smer snimanja
class SmerSnimanja(StrEnum):
    """Smer snimanja GPR-a."""

    LEVO = auto()
    DESNO = auto()


SmerSnimanjaEnum: SAEnum = SAEnum(
    SmerSnimanja,
    name="smer_snimanja_enum",
    metadata=SQLModel.metadata,
    values_callable=lambda x: [e.value for e in x if isinstance(e, SmerSnimanja)],
)

smer_snimanja_vals: str = " ili ".join(e.value for e in SmerSnimanja)
smer_snimanja_doc: str = (
    str(object=SmerSnimanja.__doc__).replace(".", ":").replace("'", "''")
)
smer_snimanja_comment: DDL = DDL(
    statement=f"""--sql
COMMENT ON TYPE {SmerSnimanjaEnum.name} IS '{smer_snimanja_doc} {smer_snimanja_vals}.'
""",
)


# event creation
enum_comment_dict: dict[SAEnum, DDL] = {
    NacinSnimanjaEnum: nacin_snimanja_comment,
    TipMagEnum: tip_mag_comment,
}

for enum_, comment_ in enum_comment_dict.items():
    event.listen(
        target=enum_,
        identifier="after_create",
        fn=comment_,
    )
