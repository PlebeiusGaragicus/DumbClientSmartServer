# from .echobot import EchoBot
# from .dudebot import DudeBot
from typing import Optional, Literal, Type
from pydantic import BaseModel, Field

import graphs.echobot
import graphs.dudebot

class ServedGraph:
    def __init__(self, id: str, name: str, placeholder: str, info: str, version: str, 
                 input_schema: Type[BaseModel], config_schema: Type[BaseModel]):
        self.id = id
        self.name = name
        self.placeholder = placeholder
        self.info = info
        self.version = version
        self.input_schema = input_schema
        self.config_schema = config_schema


AGENTS = [
    ServedGraph(
        id="echobot",
        name="Echo bot",
        placeholder="Hello, World!",
        info="holler back",
        version="0.99.1",
        input_schema=graphs.echobot.InputSchema,
        config_schema=graphs.echobot.ConfigSchema,
    ),
    ServedGraph(
        id="dudebot",
        name="Dude bot",
        placeholder="what's up?",
        info="are you talking to me?",
        version="0.2.0",
        input_schema=graphs.dudebot.InputSchema,
        config_schema=graphs.dudebot.ConfigSchema,
    )
]

__all__ = [
    "AGENTS"
]
