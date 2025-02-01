import operator
from langgraph.graph.message import add_messages
from typing import Annotated

from pydantic import BaseModel


class State(BaseModel):
    # messages: Annotated[list, operator.add]
    messages: Annotated[list, add_messages]
