import operator
from langgraph.graph.message import add_messages
from typing import Annotated

from pydantic import BaseModel, Field


class State(BaseModel):
    query: str = Field(
        "Tell me about ",
        description="What do you want to research?"
    )

    messages: Annotated[list, operator.add]
    # lucky_number: int = Field(
    #     1,
    #     ge=1,
    #     le=3,
    #     description="How intense the dude transformation should be (1-3)"
    # )
    draft: str = Field(
        "",
        format="multi-line",
        description="Current state of the draft"
    )