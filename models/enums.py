"""Enums."""

from __future__ import annotations

from sqlalchemy import event
from sqlmodel import DDL, Enum, SQLModel

NulaEnum: Enum = Enum(
    "sever",
    "jug",
    "istok",
    "zapad",
    name="nula_enum",
    metadata=SQLModel.metadata,
)

event.listen(
    target=NulaEnum,
    identifier="after_create",
    fn=DDL("""--sql
        COMMENT ON TYPE nula_enum IS 'Pravac snimanja: sever, jug, istok, zapad.'
        """),
)


NacinSnimanjaEnum: Enum = Enum(
    "kolica",
    "ručno",
    name="nacin_snimanja_enum",
    metadata=SQLModel.metadata,
)

event.listen(
    target=NacinSnimanjaEnum,
    identifier="after_create",
    fn=DDL("""--sql
        COMMENT ON TYPE nacin_snimanja_enum IS 'Način snimanja: kolica, ručno.'
        """),
)
