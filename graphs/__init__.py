import os
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
# import graphs.echobot
import graphs.ollama
import graphs.research
# TODO: import your new graphs here


# These are the agents that are served by our agent server
AGENTS = [
    ServedGraph(
        id="ollama",
        name="Ollama",
        placeholder="Ask the 🦙",
        info=graphs.ollama.DESCRIPTION,
        version=graphs.ollama.VERSION,
        input_schema=graphs.ollama.State,
        config_schema=graphs.ollama.Config,
        graph=graphs.ollama.graph,
    ),
    ServedGraph(
        id="researchrabbit",
        name="Research Rabbit",
        placeholder="Ask the rabbit...",
        info=graphs.research.DESCRIPTION,
        version=graphs.research.VERSION,
        input_schema=graphs.research.SummaryStateInput,
        config_schema=graphs.research.Configuration,
        graph=graphs.research.graph,
    ),
# TODO: add more graphs here
]


## NOTE: DEBUG ONLY - this is our "echobot" we can use for testing
# if os.getenv("DEBUG", None):
#     AGENTS.append(
#         ServedGraph(
#             id="echobot",
#             name="Echo bot",
#             placeholder="Hello, World!",
#             info=graphs.echobot.DESCRIPTION,
#             version=graphs.echobot.VERSION,
#             input_schema=graphs.echobot.State,
#             config_schema=graphs.echobot.Config,
#             graph=graphs.echobot.graph,
#         )
#     )


# NOTE: we are going to export only the AGENTS variable
__all__ = [
    "AGENTS"
]
