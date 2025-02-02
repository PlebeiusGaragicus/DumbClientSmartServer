import os
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig




class RepeatDirection(str, Enum):
    FORWARD = "forward"
    REVERSE = "reverse"

############################################################################
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
