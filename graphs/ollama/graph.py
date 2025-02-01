"""
This 'ollama' graph outlines the simplest example of a LangGraph agent.
"""

## DEFINE OUR GRAPH, ALONG WITH ITS SCHEMAS
from langgraph.graph.state import StateGraph
from .state import State
from .config import Configuration
graph_builder = StateGraph(State, input=State, output=State, config_schema=Configuration)

## ADD ALL OUR NODES
from .nodes import chatbot
graph_builder.add_node("chatbot", chatbot)

## CONNECT ALL OUR NODES
graph_builder.add_edge("__start__", "chatbot")
graph_builder.add_edge("chatbot", "__end__")

## COMPILE AND CONFIGURE
graph = graph_builder.compile()
graph.name = "Ollama with commands"
