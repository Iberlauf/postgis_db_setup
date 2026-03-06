"""Enums."""

from enum import StrEnum, auto

from sqlalchemy import Enum as SAEnum
from sqlalchemy import event
from sqlmodel import DDL, SQLModel


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


# način snimanja
class NacinSnimanja(StrEnum):
    """Način snimanja enum."""

    KOLICA = "kolica"
    RUCNO = "ručno"


NacinSnimanjaEnum: SAEnum = SAEnum(
    NacinSnimanja,
    name="nacin_snimanja_enum",
    metadata=SQLModel.metadata,
    values_callable=lambda x: [e.value for e in x],
)

nacin_snimanja_comment: DDL = DDL(
    statement=f"""--sql
COMMENT ON TYPE {NacinSnimanjaEnum.name} IS 'Način snimanja: kolica ili ručno.'
""",
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
    values_callable=lambda x: [e.value for e in x],
)

tip_mag_comment: DDL = DDL(
    statement=f"""--sql
COMMENT ON TYPE {TipMagEnum.name} IS 'Tip magnetometra (tehnologija).'
""",
)

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
