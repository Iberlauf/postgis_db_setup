"""Project defaults."""

from sqlmodel._compat import SQLModelConfig

default_model_config: SQLModelConfig = {
    "arbitrary_types_allowed": True,
    "extra": "ignore",
    "from_attributes": True,
    "use_enum_values": True,
}
