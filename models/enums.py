"""Enums."""

from enum import StrEnum

from sqlalchemy import event
from sqlmodel import DDL, Enum, SQLModel


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


NacinSnimanjaEnum: Enum = Enum(
    "kolica",
    "ručno",
    name="nacin_snimanja_enum",
    metadata=SQLModel.metadata,
)

nacin_snimanja_comment: DDL = DDL(
    statement="""--sql
COMMENT ON TYPE nacin_snimanja_enum IS 'Način snimanja: kolica ili ručno.'
""",
)

enum_comment_dict: dict[Enum, DDL] = {
    NacinSnimanjaEnum: nacin_snimanja_comment,
}


for enum, comment in enum_comment_dict.items():
    event.listen(
        target=enum,
        identifier="after_create",
        fn=comment,
    )
