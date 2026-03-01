"""Constraints for models."""

from typing import TYPE_CHECKING, Any

from geoalchemy2 import Geometry
from geoalchemy2.functions import (
    ST_Area,
    ST_NPoints,
    ST_OrientedEnvelope,
)
from sqlmodel import (
    CheckConstraint,
    Date,
    Index,
    Integer,
    String,
    UniqueConstraint,
    and_,
    cast,
    func,
    literal,
    literal_column,
    or_,
)
from sqlmodel._compat import SQLModelConfig  # noqa: TC002

if TYPE_CHECKING:
    from datetime import date

    from sqlalchemy import BinaryExpression, ColumnClause

default_model_config: SQLModelConfig = {
    "arbitrary_types_allowed": True,
    "extra": "ignore",
    "from_attributes": True,
    "use_enum_values": True,
}

# Reusable column references
_geom: ColumnClause[Geometry] = literal_column(text="geom", type_=Geometry)
_polje_naziv: ColumnClause[str] = literal_column(text="polje_naziv", type_=String)
_profil_naziv: ColumnClause[str] = literal_column(text="profil_naziv", type_=String)
_file_name: ColumnClause[str] = literal_column(text="file_name", type_=String)
_pogresni_redovi: ColumnClause[int] = literal_column(
    text="pogresni_redovi",
    type_=Integer,
)
_projekat_id: ColumnClause[int] = literal_column(text="projekat_id", type_=Integer)
_datum: ColumnClause[date] = literal_column(text="datum", type_=Date)
_projekat_start_datum: ColumnClause[date] = literal_column(
    text="projekat_start_datum",
    type_=Date,
)
_projekat_kraj_datum: ColumnClause[date] = literal_column(
    text="projekat_kraj_datum",
    type_=Date,
)
_antena_frekvencija: ColumnClause[int] = literal_column(
    text="antena_frekvencija",
    type_=Integer,
)
_investitor_pib: ColumnClause[str] = literal_column(text="investitor_pib", type_=String)
_investitor_maticni_broj: ColumnClause[str] = literal_column(
    text="investitor_maticni_broj",
    type_=String,
)
_snimak_broj: ColumnClause[int] = literal_column(text="snimak_broj", type_=Integer)
_nule_id: ColumnClause[int] = literal_column(text="nule_id", type_=Integer)


# Indexes


def _concat_id_name(name_col: ColumnClause[str]) -> BinaryExpression[Any]:
    """Concatenate projekat_id and a name column into a single unique string expression.

    Generates a PostgreSQL-immutable expression of the form:
    ``CAST(projekat_id AS VARCHAR) || '_' || name_col``
    suitable for use in unique index definitions.

    Args:
        name_col (ColumnClause[str]): The column to concatenate with projekat_id,
            e.g. ``_polje_naziv`` or ``_profil_naziv``.

    Returns:
        BinaryExpression[Any]: A SQLAlchemy binary expression representing
            the concatenated index expression.

    """
    return (
        cast(expression=_projekat_id, type_=String)
        .op(opstring="||")(literal(value="_", type_=String))
        .op(opstring="||")(name_col)
    )


uq_projekat_polje_concat_mag: Index = Index(
    "uq_projekat_polje_concat_mag",
    _concat_id_name(name_col=_polje_naziv),
    unique=True,
)

uq_projekat_polje_concat_gpr: Index = Index(
    "uq_projekat_polje_concat_gpr",
    _concat_id_name(name_col=_polje_naziv),
    unique=True,
)

uq_projekat_profil_concat_mag: Index = Index(
    "uq_projekat_profil_concat_mag",
    _concat_id_name(name_col=_profil_naziv),
    unique=True,
)

uq_projekat_profil_concat_gpr: Index = Index(
    "uq_projekat_profil_concat_gpr",
    _concat_id_name(name_col=_profil_naziv),
    unique=True,
)

# UniqueConstraints

uq_projekat_datum: UniqueConstraint = UniqueConstraint(
    _projekat_id,
    _datum,
    name="uq_projekat_datum",
)

# CheckConstraints

ck_polje_naziv_format: CheckConstraint = CheckConstraint(
    sqltext=_polje_naziv.op(opstring="~")(r"^Polje \d+$|^\d+[a-z]+$"),
    name="ck_polje_naziv_format",
)

ck_profil_naziv_format: CheckConstraint = CheckConstraint(
    sqltext=_profil_naziv.op(opstring="~")(r"^Profil \d+$"),
    name="ck_profil_naziv_format",
)

ck_file_name_format_gpr: CheckConstraint = CheckConstraint(
    sqltext=_file_name.op(opstring="~")(r"^[^a-z]*$"),
    name="ck_file_name_format_gpr",
)

ck_all_positive: CheckConstraint = CheckConstraint(
    sqltext=func.array_position(_pogresni_redovi, 0).is_(other=None),
    name="ck_all_positive",
)

ck_rectangular_polygon: CheckConstraint = CheckConstraint(
    sqltext=and_(
        ST_NPoints(_geom) == 5,
        func.abs(1 - ST_Area(_geom) / ST_Area(ST_OrientedEnvelope(_geom))) < 0.0001,
    ),
    name="ck_rectangular_polygon",
)

ck_linestring_two_points: CheckConstraint = CheckConstraint(
    sqltext=ST_NPoints(_geom) == 2,
    name="ck_linestring_two_points",
)

ck_projekat_datum_opseg: CheckConstraint = CheckConstraint(
    sqltext=(
        _projekat_start_datum.is_(other=None)
        | _projekat_kraj_datum.is_(other=None)
        | (_projekat_start_datum <= _projekat_kraj_datum)
    ),
    name="ck_projekat_datum_opseg",
)

ck_antena_frekvencija_positive: CheckConstraint = CheckConstraint(
    sqltext=_antena_frekvencija.is_(other=None) | (_antena_frekvencija > 0),
    name="ck_antena_frekvencija_positive",
)

ck_pib_format: CheckConstraint = CheckConstraint(
    sqltext=_investitor_pib.op(opstring="~")(r"^[0-9]{9}$"),
    name="ck_pib_format",
)

ck_mb_format: CheckConstraint = CheckConstraint(
    sqltext=_investitor_maticni_broj.op(opstring="~")(r"^[0-9]{8}$"),
    name="ck_mb_format",
)

ck_right_angles: CheckConstraint = CheckConstraint(
    sqltext=func.check_right_angles(_geom),
    name="ck_right_angles",
)

ck_snimak_broj: CheckConstraint = CheckConstraint(
    sqltext=or_(
        _snimak_broj.is_(other=None),
        and_(
            _snimak_broj >= 1,
            _snimak_broj <= 99,
        ),
    ),
    name="ck_snimak_broj",
)

ck_nule: CheckConstraint = CheckConstraint(
    sqltext=and_(
        _nule_id >= 1,
        _nule_id <= 4,
    ),
    name="ck_nule_id",
)
