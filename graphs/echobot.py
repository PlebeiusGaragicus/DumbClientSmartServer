from pydantic import BaseModel, Field
from typing import Optional, Type


class InputSchema(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Message to echo back"
    )


class ConfigSchema(BaseModel):
    capitalize: bool = Field(
        False,
        description="Whether to capitalize the echoed message"
    )
    prefix: str = Field(
        "Echo: ",
        min_length=0,
        max_length=50,
        description="Prefix to add before the echoed message"
    )
    suffix: str = Field(
        "",
        max_length=50,
        description="Suffix to add after the echoed message"
    )
