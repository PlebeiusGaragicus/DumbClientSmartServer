import operator
# from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Annotated

# @dataclass(kw_only=True)
class SummaryState(BaseModel):
    research_topic: str = Field(default=None) # Report topic     
    search_query: str = Field(default=None) # Search query
    web_research_results: Annotated[list, operator.add] = Field(default_factory=list) 
    sources_gathered: Annotated[list, operator.add] = Field(default_factory=list) 
    research_loop_count: int = Field(default=0) # Research loop count
    running_summary: str = Field(default=None) # Final report

# @dataclass(kw_only=True)
class SummaryStateInput(BaseModel):
    research_topic: str = Field(default=None) # Report topic     

# @dataclass(kw_only=True)
class SummaryStateOutput(BaseModel):
    running_summary: str = Field(default=None) # Final report


##########

# @dataclass(kw_only=True)
class GraphState(BaseModel):
    running_summary: str = Field(default=None)
