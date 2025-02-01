from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import StateGraph, RunnableConfig
from langchain_ollama import ChatOllama

from .config import Configuration, OLLAMA_HOST
from .state import State



def check_for_command(state: State, config: RunnableConfig):
    # check if the last message starts with a '/'
    if state.messages[-1].content.startswith("/"):
        return True
    return False



def handle_command(state: State, config: RunnableConfig):
    # configurable = Configuration.from_runnable_config(config)

    # extract command
    split = state.messages[-1].content.split(" ")
    command = split[0][1:].lower() # Remove the slash and take the first word
    arguments = split[1:]
    command_result = configurable.commands[command]()

    return {"messages": [{"role": "assistant", "content": command_result}]}



def chatbot(state: State, config: RunnableConfig):
    configurable = Configuration.from_runnable_config(config)

    llm = ChatOllama(
        model=configurable.model,
        keep_alive=configurable.keep_alive,
        temperature=configurable.temperature / 100,
        base_url=OLLAMA_HOST,
    )

    # The messages are already LangChain message objects, use them directly
    response = llm.stream(state.messages)

    return {"messages": [{"role": "assistant", "content": chunk.content} for chunk in response]}


############################################################################