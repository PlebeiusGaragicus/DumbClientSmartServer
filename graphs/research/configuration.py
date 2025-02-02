import os
from dataclasses import dataclass, field, fields
from typing import Any, Optional
from enum import Enum


from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from typing_extensions import Annotated

class LLMModelsAvailable(str, Enum):
    phi4 = "phi4"
    llama31 = "llama3.1"

# @dataclass(kw_only=True)
class Configuration(BaseModel):
    """The configurable fields for the research assistant."""
    max_web_research_loops: int = 3
    # local_llm: str = "llama3.2"
    # local_llm: Annotated[str, Field(default="llama3.1:latest")]
    local_llm: LLMModelsAvailable = Field(LLMModelsAvailable.phi4)

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})