import os
import operator
from enum import Enum
from typing import Optional, Any, Annotated
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages

from pydantic import BaseModel, Field

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
    # lucky_number: int = Field(
    #     1,
    #     ge=1,
    #     le=3,
    #     description="How intense the dude transformation should be (1-3)"
    # )
    # draft: str = Field(
    #     "",
    #     format="multi-line",
    #     description="Current state of the draft"
    # )

class Result(BaseModel):
    reply: str







############################################################################
# CONFIG
############################################################################

OLLAMA_HOST = "http://host.docker.internal:11434"

class KeepAlive(str, Enum):
    NONE = "0"
    FIVE_MINUTES = "5m"
    FOREVER = "-1"

class LLMModelsAvailable(str, Enum):
    phi4 = "phi4"
    llama31 = "llama3.1"

############################################################################
class Config(BaseModel):
    """The configurable fields for the graph."""

    model: LLMModelsAvailable = Field(LLMModelsAvailable.llama31)
    temperature: int = Field(
        50,
        ge=0,
        le=100,
        description="Temperature for the model"
    )
    keep_alive: KeepAlive = Field(
        KeepAlive.FIVE_MINUTES,
        description="How long to keep the model in memory"
    )
    disable_commands: bool = Field(
        False,
        description="Whether to disable commands (i.e. starts with '/')"
    )
    # ollama_endpoint: str = Field(
    #     OLLAMA_HOST,
    #     description="Ollama endpoint",
    #     optional=True
    # )

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
