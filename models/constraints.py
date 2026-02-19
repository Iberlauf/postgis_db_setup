"""Constranits for models."""

from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Area, ST_MakeValid, ST_NPoints, ST_OrientedEnvelope
from sqlmodel import (
    CheckConstraint,
    Index,
    UniqueConstraint,
    and_,
    func,
    literal_column,
    text,
)

# Indexes

uq_projekat_polje_concat_mag: Index = Index(
    "uq_projekat_polje_concat_mag",
    text(text="(projekat_id::text || '_' || polje_naziv)"),
    unique=True,
)

uq_projekat_polje_concat_gpr: Index = Index(
    "uq_projekat_polje_concat_gpr",
    text(text="(projekat_id::text || '_' || polje_naziv)"),
    unique=True,
)

uq_projekat_profil_concat_mag: Index = Index(
    "uq_projekat_profil_concat_mag",
    text(text="(projekat_id::text || '_' || profil_naziv)"),
    unique=True,
)

uq_projekat_profil_concat_gpr: Index = Index(
    "uq_projekat_profil_concat_gpr",
    text(text="(projekat_id::text || '_' || profil_naziv)"),
    unique=True,
)

# UniqueConstraints

uq_projekat_datum: UniqueConstraint = UniqueConstraint(
    "projekat_id",
    "datum",
    name="uq_projekat_datum",
)

# CheckConstraints

ck_polje_naziv_format: CheckConstraint = CheckConstraint(
    sqltext="""--sql
            polje_naziv ~ '^Polje \\d+$|^\\d+[a-z]+$'
            """,
    name="ck_polje_naziv_format",
)

ck_profil_naziv_format: CheckConstraint = CheckConstraint(
    sqltext="""--sql
            profil_naziv ~ '^Profil \\d+$'
            """,
    name="ck_profil_naziv_format",
)


ck_file_name_format_gpr: CheckConstraint = CheckConstraint(
    sqltext="""--sql
            file_name ~ '^[^a-z]*$'
            """,
    name="ck_file_name_format_gpr",
)

ck_shift_x_non_negative: CheckConstraint = CheckConstraint(
    sqltext="""--sql
            shift_x >= 0
            """,
    name="ck_shift_x_non_negative",
)

ck_shift_y_non_negative: CheckConstraint = CheckConstraint(
    sqltext="""--sql
            shift_y >= 0
            """,
    name="ck_shift_y_non_negative",
)

ck_all_positive: CheckConstraint = CheckConstraint(
    sqltext=func.array_position(
        literal_column(text="pogresni_redovi"),
        0,
    ).is_(other=None),
    name="ck_all_positive",
)

ck_rectangular_polygon: CheckConstraint = CheckConstraint(
    sqltext=and_(
        ST_NPoints(ST_MakeValid(literal_column(text="geom", type_=Geometry))) == 5,
        func.abs(
            1
            - ST_Area(ST_MakeValid(literal_column(text="geom", type_=Geometry)))
            / ST_Area(
                ST_OrientedEnvelope(
                    ST_MakeValid(literal_column(text="geom", type_=Geometry)),
                ),
            ),
        )
        < 0.0001,
    ),
    name="check_rectangular_polygon",
)

ck_linestring_two_points: CheckConstraint = CheckConstraint(
    sqltext=ST_NPoints(ST_MakeValid(literal_column(text="geom", type_=Geometry))) == 2,
    name="ck_linestring_two_points",
)


ck_projekat_datum_opseg: CheckConstraint = CheckConstraint(
    sqltext="""--sql
            projekat_start_datum IS NULL
            OR projekat_kraj_datum IS NULL
            OR projekat_start_datum <= projekat_kraj_datum""",
    name="ck_projekat_datum_opseg",
)

ck_antena_frekvencija_positive: CheckConstraint = CheckConstraint(
    sqltext="antena_frekvencija IS NULL OR antena_frekvencija > 0",
    name="ck_antena_frekvencija_positive",
)

ck_pib_format: CheckConstraint = CheckConstraint(
    sqltext="investitor_pib ~ '^[0-9]{9}$'",
    name="ck_pib_format",
)

ck_mb_format: CheckConstraint = CheckConstraint(
    sqltext="investitor_maticni_broj ~ '^[0-9]{8}$'",
    name="ck_mb_format",
)

ck_right_angles: CheckConstraint = CheckConstraint(
    sqltext=func.check_right_angles(literal_column(text="geom", type_=Geometry)),
    name="ck_right_angles",
)
