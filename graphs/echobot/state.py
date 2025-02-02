import operator
from langgraph.graph.message import add_messages
from typing import Annotated

from pydantic import BaseModel, Field


class State(BaseModel):
    query: str = Field(
        "what is 17 * 17?",
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
