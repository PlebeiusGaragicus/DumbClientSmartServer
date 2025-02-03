import os
import operator
from enum import Enum
from typing import Optional, Any, Annotated
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages



############################################################################
# STATE
############################################################################

class State(BaseModel):
    query: str = Field(
        "",
        format="multi-line",
        description="What do you want to research?"
    )

    messages: Annotated[list, operator.add]
    lucky_number: int = Field(
        1,
        ge=1,
        le=3,
        description="How intense the dude transformation should be (1-3)"
    )


class Result(BaseModel):
    reply: str


############################################################################
# CONFIG
############################################################################

class RepeatDirection(str, Enum):
    FORWARD = "forward"
    REVERSE = "reverse"

class Config(BaseModel):
    """The configurable fields for the graph."""

    temperature: int = Field(
        50,
        ge=0,
        le=100,
        description="Temperature for the model"
    )
    repeat_direction: RepeatDirection = Field(
        RepeatDirection.FORWARD,
        description="Direction to `echo` back."
    )
    disable_commands: bool = Field(
        False,
        description="Whether to disable commands (i.e. starts with '/')"
    )

    ##############################################################
    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Config":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        return cls(**{k: v for k, v in values.items() if v})



# from pydantic import BaseModel, Field
# from typing import Optional, Literal, Type
# from enum import Enum


# class InputSchema(BaseModel):
#     message: str = Field(
#         ...,
#         description="Message to dude-ify"
#     )



# from pydantic import BaseModel, Field
# from typing import Optional, Type


# class InputSchema(BaseModel):
#     message: str = Field(
#         ...,
#         description="Message to echo back"
#     )


# class ConfigSchema(BaseModel):
#     capitalize: bool = Field(
#         False,
#         description="Whether to capitalize the echoed message"
#     )
#     prefix: str = Field(
#         "Echo: ",
#         description="Prefix to add before the echoed message"
#     )
#     suffix: str = Field(
#         "",
#         format="multi-line",
#         description="Suffix to add after the echoed message"
#     )



# class DudeStyle(str, Enum):
#     SURFER = "surfer"
#     SKATER = "skater"
#     STONER = "stoner"
#     CASUAL = "casual"

# class ConfigSchema(BaseModel):
#     intensity: int = Field(
#         1,
#         ge=1,
#         le=3,
#         description="How intense the dude transformation should be (1-3)"
#     )
#     style: DudeStyle = Field(
#         DudeStyle.CASUAL,
#         description="The style of dude speak to use"
#     )
#     add_emoji: bool = Field(
#         True,
#         description="Whether to add relevant emojis to the response"
#     )
#     catchphrase: str = Field(
#         "Dude!",
#         format="multi-line",
#         description="Custom catchphrase to use"
#     )
