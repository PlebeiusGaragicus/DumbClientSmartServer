import os
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field
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
class OllamaConfig(BaseModel):
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
    ) -> "OllamaConfig":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        return cls(**{k: v for k, v in values.items() if v})
