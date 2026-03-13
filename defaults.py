"""Project defaults."""

from sqlmodel._compat import SQLModelConfig

default_model_config: SQLModelConfig = {
    "arbitrary_types_allowed": True,
    "extra": "ignore",
    "from_attributes": True,
    "use_enum_values": True,
}

srid: int = 6316
default_geom_dim: int = 2
