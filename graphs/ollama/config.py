import os
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field
# from langgraph.graph.state import RunnableConfig
from langchain_core.runnables import RunnableConfig




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
    # ollama_endpoint: str = Field(
    #     OLLAMA_HOST,
    #     description="Ollama endpoint",
    #     optional=True
    # )

    ##############################################################
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
