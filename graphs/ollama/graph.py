"""This 'ollama' graph outlines the simplest example of a LangGraph agent."""

from langgraph.graph.state import StateGraph


## DEFINE OUR GRAPH, ALONG WITH ITS SCHEMAS
from .state import State, Result, Config
graph_builder = StateGraph(State, input=State, output=Result, config_schema=Config)


## ADD ALL OUR NODES
from .nodes import ollama, _check_for_command, handle_command
graph_builder.add_node("ollama", ollama)
graph_builder.add_node("handle_command", handle_command)


## CONNECT ALL OUR NODES
graph_builder.add_conditional_edges("__start__", _check_for_command)
graph_builder.add_edge("handle_command", "__end__")
graph_builder.add_edge("ollama", "__end__")


## COMPILE AND CONFIGURE
graph = graph_builder.compile()