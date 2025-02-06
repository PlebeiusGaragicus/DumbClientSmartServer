import os
import operator
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional
from typing_extensions import Annotated
from langchain_core.runnables import RunnableConfig


############################################################################
# STATE
############################################################################

class SummaryState(BaseModel):
    # Report topic
    query: str = Field(default=None)
    
    # Search query
    search_query: str = Field(default=None)

    #TODO:
    web_research_results: Annotated[list, operator.add] = Field(default_factory=list)

    # TODO:
    sources_gathered: Annotated[list, operator.add] = Field(default_factory=list)
    
    # Research loop count
    research_loop_count: int = Field(default=0)
    
    # Final report
    running_summary: str = Field(default=None)


# Report topic
class SummaryStateInput(BaseModel):
    query: str = Field(default=None)

# Final report
class SummaryStateOutput(BaseModel):
    running_summary: str = Field(default=None)



############################################################################
# CONFIG
############################################################################

from ..local_models import LLMModelsAvailable, DEFAULT_LOCAL_MODEL
# class LLMModelsAvailable(str, Enum):
#     phi4 = "phi4"
#     llama31 = "llama3.1"


class Configuration(BaseModel):
    """The configurable fields for the research assistant."""

    max_web_research_loops: int = Field(
        1,
        ge=1,
        le=5,
        description="Number of times to search the web"
    )

    # local_llm: LLMModelsAvailable = Field(DEFAULT_LOCAL_MODEL)
    local_llm: LLMModelsAvailable = Field(LLMModelsAvailable.deepseekR214b)

    # system_prompt: str = Field(
    #     SYSTEM_PROMPT,
    #     format="multi-line",
    #     description="What do you want to research?"
    # )


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

    # NOTE: keep
    # def from_runnable_config(
    #     cls, config: Optional[RunnableConfig] = None
    # ) -> "Configuration":
    #     """Create a Configuration instance from a RunnableConfig."""
    #     configurable = (
    #         config["configurable"] if config and "configurable" in config else {}
    #     )
    #     values: dict[str, Any] = {
    #         f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
    #         for f in fields(cls)
    #         if f.init
    #     }
    #     return cls(**{k: v for k, v in values.items() if v})