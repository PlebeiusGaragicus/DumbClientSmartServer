# from .echobot import EchoBot
# from .dudebot import DudeBot
from typing import Optional, Literal, Type
from pydantic import BaseModel, Field



# This class encapsulates all the information about an agent that is served
class ServedGraph:
    def __init__(self, id: str, name: str, placeholder: str, info: str, version: str,
                 input_schema: Type[BaseModel], config_schema: Type[BaseModel], graph):
        self.id = id
        self.name = name
        self.placeholder = placeholder
        self.info = info
        self.version = version
        self.input_schema = input_schema
        self.config_schema = config_schema
        self.graph = graph



# Import all the graphs
import graphs.echobot
import graphs.dudebot
import graphs.ollama
# TODO: import your new graphs here


# These are the agents that are served by our agent server
AGENTS = [
    # ServedGraph(
    #     id="echobot",
    #     name="Echo bot",
    #     placeholder="Hello, World!",
    #     info="holler back",
    #     version="0.99.1",
    #     input_schema=graphs.echobot.InputSchema,
    #     config_schema=graphs.echobot.ConfigSchema,
    #     graph=graphs.echobot.graph,
    # ),
    # ServedGraph(
    #     id="dudebot",
    #     name="Dude bot",
    #     placeholder="what's up?",
    #     info="are you talking to me?",
    #     version="0.2.0",
    #     input_schema=graphs.dudebot.InputSchema,
    #     config_schema=graphs.dudebot.ConfigSchema,
    #     graph=graphs.dudebot.graph,
    # ),
    ServedGraph(
        id="ollama",
        name="Ollama",
        placeholder="Ask the 🦙",
        info="These models are all run locally!",
        version="0.7.0",
        input_schema=graphs.ollama.State,
        config_schema=graphs.ollama.Configuration,
        graph=graphs.ollama.graph,
    ),
# TODO: add more graphs here

]

# NOTE: we are going to export only the AGENTS variable
__all__ = [
    "AGENTS"
]
