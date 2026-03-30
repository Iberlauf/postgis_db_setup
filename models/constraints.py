"""Constraints for models."""

from collections.abc import Sequence  # noqa: TC003
from typing import TYPE_CHECKING, Any

from geoalchemy2 import Geometry, Raster
from geoalchemy2.functions import (
    ST_Area,
    ST_ConvexHull,
    ST_NPoints,
    ST_OrientedEnvelope,
)
from pydantic import PositiveInt
from sqlalchemy import Cast
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.elements import ColumnClause
from sqlmodel import (
    CheckConstraint,
    Date,
    Index,
    Integer,
    String,
    UniqueConstraint,
    all_,
    and_,
    cast,
    func,
    literal,
    literal_column,
    null,
    or_,
)

if TYPE_CHECKING:
    from datetime import date

    from sqlalchemy import BinaryExpression, ColumnClause


# Reusable column references

_geom: ColumnClause[Geometry] = literal_column(
    text="geom",
    type_=Geometry,
)
_rast: ColumnClause[Raster] = literal_column(
    text="rast",
    type_=Raster,
)
_polje_naziv: ColumnClause[str] = literal_column(
    text="polje_naziv",
    type_=String(length=255),
)
_profil_naziv: ColumnClause[str] = literal_column(
    text="profil_naziv",
    type_=String(length=255),
)
_file_name: ColumnClause[str] = literal_column(
    text="file_name",
    type_=String(length=255),
)
_pogresni_redovi: ColumnClause[Sequence[PositiveInt]] = literal_column(
    text="pogresni_redovi",
    type_=postgresql.ARRAY(item_type=Integer),
)
_projekat_id: ColumnClause[PositiveInt] = literal_column(
    text="projekat_id",
    type_=Integer,
)
_datum: ColumnClause[date] = literal_column(
    text="datum",
    type_=Date,
)
_projekat_start_datum: ColumnClause[date] = literal_column(
    text="projekat_start_datum",
    type_=Date,
)
_projekat_kraj_datum: ColumnClause[date] = literal_column(
    text="projekat_kraj_datum",
    type_=Date,
)
_antena_frekvencija: ColumnClause[PositiveInt] = literal_column(
    text="antena_frekvencija",
    type_=Integer,
)
_investitor_pib: ColumnClause[str] = literal_column(
    text="investitor_pib",
    type_=String(length=9),
)
_investitor_maticni_broj: ColumnClause[str] = literal_column(
    text="investitor_maticni_broj",
    type_=String(length=8),
)
_snimak_broj: ColumnClause[PositiveInt] = literal_column(
    text="snimak_broj",
    type_=Integer,
)
_nule_id: ColumnClause[PositiveInt] = literal_column(
    text="nule_id",
    type_=Integer,
)
_ekipa_ime: ColumnClause[str] = literal_column(
    text="ekipa_ime",
    type_=String(length=20),
)
_ekipa_prezime: ColumnClause[str] = literal_column(
    text="ekipa_prezime",
    type_=String(length=20),
)
_ekipa_ids: ColumnClause[Sequence[PositiveInt]] = literal_column(
    text="ekipa_ids",
    type_=postgresql.ARRAY(item_type=Integer),
)

_lokacije_ids: ColumnClause[Sequence[PositiveInt]] = literal_column(
    text="lokacije_ids",
    type_=postgresql.ARRAY(item_type=Integer),
)

_dubina_gain: ColumnClause[dict[str, str]] = literal_column(
    text="dubina_gain",
    type_=postgresql.HSTORE,
)
_parc_br: ColumnClause[str] = literal_column(
    text="parc_br",
    type_=String(length=50),
)
_parc_ko: ColumnClause[str] = literal_column(
    text="parc_k",
    type_=String(length=255),
)

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
        .op(opstring="||")(literal(value="_", type_=String(length=1)))
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

uq_projekat_polje_concat_elektrika: Index = Index(
    "uq_projekat_profil_concat_elektrika",
    _concat_id_name(name_col=_polje_naziv),
    unique=True,
)

uq_projekat_polje_concat_profiler: Index = Index(
    "uq_projekat_profil_concat_profiler",
    _concat_id_name(name_col=_polje_naziv),
    unique=True,
)

dsm_rasteri_st_convexhull_idx: Index = Index(
    "dsm_rasteri_st_convexhull_idx",
    ST_ConvexHull(_rast),
    postgresql_using="gist",
    postgresql_with={"fillfactor": 90, "buffering": "auto"},
)

# UniqueConstraints

uq_projekat_datum: UniqueConstraint = UniqueConstraint(
    _projekat_id,
    _datum,
    name="uq_projekat_datum",
)

uq_parc_ko: UniqueConstraint = UniqueConstraint(
    _parc_br,
    _parc_ko,
    name="uq_parc_br_parc_ko",
)

# CheckConstraints


def all_positive_and_unique_constraint(
    name_col: ColumnClause[Sequence[PositiveInt]],
) -> CheckConstraint:
    """Create a CheckConstraint verifying all array elements are positive and unique.

    Uses the PostgreSQL intarray extension to efficiently check that every element
    in the array name_col is greater than zero and that no duplicates exist.

    Args:
        name_col: A column clause typed as a sequence of positive integers. The
            constraint name is derived from the column's key attribute.

    Returns:
        A CheckConstraint that passes when the column is NULL, or when all
        elements are strictly positive and no two elements are equal.

    """
    sorted_column: Cast[Sequence[PositiveInt]] = cast(
        expression=func.sort(name_col),
        type_=postgresql.ARRAY(item_type=Integer),
    )
    return CheckConstraint(
        sqltext=or_(
            name_col == null(),
            and_(
                literal(value=0, type_=Integer) < all_(expr=name_col),
                func.uniq(sorted_column) == sorted_column,
            ),
        ),
        name=f"ck_all_positive_and_unique_{name_col.key}",
    )


ck_all_positive_unique_pogresni_redovi: CheckConstraint = (
    all_positive_and_unique_constraint(
        name_col=_pogresni_redovi,
    )
)

ck_all_positive_unique_ekipa_ids: CheckConstraint = all_positive_and_unique_constraint(
    name_col=_ekipa_ids,
)

ck_all_positive_unique_lokacije_ids: CheckConstraint = (
    all_positive_and_unique_constraint(
        name_col=_lokacije_ids,
    )
)

ck_polje_naziv_format: CheckConstraint = CheckConstraint(
    sqltext=_polje_naziv.op(opstring="~")(
        literal(value=r"^Polje \d+$|^\d+[a-z]+$", type_=String),
    ),
    name="ck_polje_naziv_format",
)

ck_profil_naziv_format: CheckConstraint = CheckConstraint(
    sqltext=_profil_naziv.op(opstring="~")(
        literal(value=r"^Profil \d+$", type_=String),
    ),
    name="ck_profil_naziv_format",
)

ck_file_name_format_gpr: CheckConstraint = CheckConstraint(
    sqltext=_file_name.op(opstring="~")(literal(value=r"^[^a-z]*$", type_=String)),
    name="ck_file_name_format_gpr",
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
    sqltext=or_(
        _projekat_start_datum.is_(other=None),
        _projekat_kraj_datum.is_(other=None),
        _projekat_start_datum <= _projekat_kraj_datum,
    ),
    name="ck_projekat_datum_opseg",
)

ck_antena_frekvencija_positive: CheckConstraint = CheckConstraint(
    sqltext=or_(_antena_frekvencija.is_(other=None), _antena_frekvencija > 0),
    name="ck_antena_frekvencija_positive",
)

ck_pib_format: CheckConstraint = CheckConstraint(
    sqltext=_investitor_pib.op(opstring="~")(
        literal(value=r"^[0-9]{9}$", type_=String),
    ),
    name="ck_pib_format",
)

ck_mb_format: CheckConstraint = CheckConstraint(
    sqltext=_investitor_maticni_broj.op(opstring="~")(
        literal(value=r"^[0-9]{8}$", type_=String),
    ),
    name="ck_mb_format",
)

ck_right_angles: CheckConstraint = CheckConstraint(
    sqltext=func.check_right_angles(_geom),
    name="ck_right_angles",
)

ck_snimak_broj: CheckConstraint = CheckConstraint(
    sqltext=or_(
        _snimak_broj.is_(other=None),
        _snimak_broj.between(cleft=1, cright=99),
    ),
    name="ck_snimak_broj",
)

ck_nule: CheckConstraint = CheckConstraint(
    sqltext=_nule_id.between(cleft=1, cright=4),
    name="ck_nule_id",
)

ck_integer_string_keys_and_values_dubina_gain: CheckConstraint = CheckConstraint(
    sqltext=or_(
        _dubina_gain == null(),
        and_(
            literal(value=r"^-?\d+$", type_=String).op(opstring="~")(
                all_(expr=func.akeys(_dubina_gain)),
            ),
            literal(value=r"^-?\d+$", type_=String).op(opstring="~")(
                all_(expr=func.avals(_dubina_gain)),
            ),
        ),
    ),
    name="ck_integer_string_keys_and_values_dubina_gain",
)
