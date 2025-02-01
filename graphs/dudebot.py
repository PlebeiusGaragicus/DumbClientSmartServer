from pydantic import BaseModel, Field
from typing import Optional, Literal, Type
from enum import Enum


class InputSchema(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Message to dude-ify"
    )



class DudeStyle(str, Enum):
    SURFER = "surfer"
    SKATER = "skater"
    STONER = "stoner"
    CASUAL = "casual"

class ConfigSchema(BaseModel):
    intensity: int = Field(
        1,
        ge=1,
        le=3,
        description="How intense the dude transformation should be (1-3)"
    )
    style: DudeStyle = Field(
        DudeStyle.CASUAL,
        description="The style of dude speak to use"
    )
    add_emoji: bool = Field(
        True,
        description="Whether to add relevant emojis to the response"
    )
    catchphrase: str = Field(
        "Dude!",
        min_length=1,
        max_length=50,
        description="Custom catchphrase to use"
    )
