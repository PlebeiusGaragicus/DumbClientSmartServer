"""This 'echobot' graph outlines the simplest example of a LangGraph agent."""

from langgraph.graph.state import StateGraph

from .state import State, Result, Config

graph_builder = StateGraph(State, input=State, output=Result, config_schema=Config)


## ADD NODES
from .nodes import echobot
graph_builder.add_node("echobot", echobot)


## CONNECT NODES
graph_builder.add_conditional_edges("__start__", "echobot")
graph_builder.add_edge("echobot", "__end__")

graph = graph_builder.compile()
#NOTE: Don't do this, we want the name to default to "LangGraph" so we can 'skip it'
# graph.name = "Ollama with commands"