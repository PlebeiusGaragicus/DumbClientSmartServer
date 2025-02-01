import os
import operator
from typing import Annotated, Optional
# from langchain_core.pydantic_v1 import BaseModel
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langgraph.graph.state import StateGraph, RunnableConfig
from langchain_ollama import ChatOllama

from dataclasses import dataclass, fields
from typing import Any

from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated
from pydantic import BaseModel, Field
from enum import Enum


############################################################################


OLLAMA_HOST = "http://host.docker.internal:11434"



############################################################################

class KeepAlive(str, Enum):
    NONE = "0"
    FIVE_MINUTES = "5m"
    FOREVER = "-1"

class LLMModelsAvailable(str, Enum):
    phi4 = "phi4"
    llama31 = "llama3.1"

############################################################################

class Configuration(BaseModel):
    """The configurable fields for the graph."""

    model: LLMModelsAvailable = Field(LLMModelsAvailable.phi4)
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

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        return cls(**{k: v for k, v in values.items() if v})
