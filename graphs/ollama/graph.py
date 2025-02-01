from langgraph.graph.state import StateGraph

from .state import State
from .config import Configuration

from .nodes import chatbot


graph_builder = StateGraph(State, input=State, output=State, config_schema=Configuration)



graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge("__start__", "chatbot")
graph_builder.add_edge("chatbot", "__end__")

graph = graph_builder.compile()
graph.name = "Ollama with commands"
