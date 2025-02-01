from pydantic import BaseModel, Field
from typing import Optional, Type


class InputSchema(BaseModel):
    message: str = Field(
        ...,
        description="Message to echo back"
    )


class ConfigSchema(BaseModel):
    capitalize: bool = Field(
        False,
        description="Whether to capitalize the echoed message"
    )
    prefix: str = Field(
        "Echo: ",
        description="Prefix to add before the echoed message"
    )
    suffix: str = Field(
        "",
        format="multi-line",
        description="Suffix to add after the echoed message"
    )
