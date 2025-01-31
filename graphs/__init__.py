from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from enum import Enum

class ModelName(str, Enum):
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    GPT35_16K = "gpt-3.5-turbo-16k"

class Speed(str, Enum):
    SLOW = "slow"
    AVERAGE = "average"
    FAST = "fast"

class AgentInfo(BaseModel):
    id: str = Field(..., min_length=1, max_length=50, description="Unique identifier for the agent")
    display_name: str = Field(..., min_length=1, max_length=50, description="Human-readable name for the agent")
    description: str = Field(..., min_length=10, max_length=500, description="Detailed description of what the agent does")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$", description="Semantic version of the agent")
    author: Optional[str] = Field(None, max_length=100, description="Author of the agent")
    input_box_placeholder: str = Field("Let's Chat", min_length=1, max_length=100, description="Placeholder text for the input box")

class InputSchema(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000, description="The main input prompt for the agent")
    speed: Speed = Field(
        Speed.AVERAGE,
        description="Controls the speed-quality tradeoff of the agent's response"
    )

class ConfigSchema(BaseModel):
    model: ModelName = Field(
        ModelName.GPT35,
        description="The language model to use"
    )
    temperature: float = Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Controls randomness in the output. Higher values mean more random"
    )
    max_tokens: Optional[int] = Field(
        None,
        ge=1,
        le=32000,
        description="Maximum number of tokens to generate. None means no limit"
    )

class Agent(BaseModel):
    info: AgentInfo
    input_schema: InputSchema
    config_schema: ConfigSchema

class EchoBot(Agent):
    info: AgentInfo = AgentInfo(
        id="echobot",
        display_name="Echo Bot",
        description="A simple echo bot that returns the input",
        version="0.1.0",
        author="DumbClientSmartServer",
        input_box_placeholder="Type a message to echo..."
    )
    input_schema: InputSchema = InputSchema(
        prompt="Message to echo back"
    )
    config_schema: ConfigSchema = ConfigSchema()


class DudeBot(Agent):
    info: AgentInfo = AgentInfo(
        id="dudebot",
        display_name="Dude Bot",
        description="A simple dude",
        version="9.1.0",
        author="you",
        input_box_placeholder="Type a message to echo..."
    )
    input_schema: InputSchema = InputSchema(
        prompt="Message to echo back"
    )
    config_schema: ConfigSchema = ConfigSchema()

AGENTS = {
    "echobot": EchoBot,
    "dudebot": DudeBot
}
