"""This 'ollama' graph outlines the simplest example of a LangGraph agent."""

from langgraph.graph.state import StateGraph


## DEFINE OUR GRAPH, ALONG WITH ITS SCHEMAS
from .state import State
from .config import OllamaConfig
graph_builder = StateGraph(State, input=State, output=State, config_schema=OllamaConfig)


## ADD ALL OUR NODES
from .commands import check_for_command, handle_command
from .nodes import chatbot
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("handle_command", handle_command)
graph_builder.add_node("check_for_command", check_for_command)


## CONNECT ALL OUR NODES
graph_builder.add_conditional_edges(
    "__start__",
    check_for_command,
    {
        True: "handle_command",
        False: "chatbot"
    }
)
graph_builder.add_edge("handle_command", "__end__")
graph_builder.add_edge("chatbot", "__end__")


## COMPILE AND CONFIGURE
graph = graph_builder.compile()
graph.name = "Ollama with commands"
