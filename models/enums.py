"""Enums."""

from __future__ import annotations

from sqlalchemy import event
from sqlmodel import DDL, Enum, SQLModel

NacinSnimanjaEnum: Enum = Enum(
    "kolica",
    "ručno",
    name="nacin_snimanja_enum",
    metadata=SQLModel.metadata,
)

nacin_snimanja_comment: DDL = DDL(
    statement="""--sql
        COMMENT ON TYPE nula_enum IS 'Način snimanja: kolica ili ručno.'
        """,
)

enum_coment_dict: dict[Enum, DDL] = {
    NacinSnimanjaEnum: nacin_snimanja_comment,
}


for enum, comment in enum_coment_dict.items():
    event.listen(
        target=enum,
        identifier="after_create",
        fn=comment,
    )
