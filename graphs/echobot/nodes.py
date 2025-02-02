from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama



from .config import Config, RepeatDirection
from .state import State




############################################################################
def echobot(state: State, config: RunnableConfig):
    configurable = Config.from_runnable_config(config)

    messages = state.messages


    if configurable.repeat_direction == RepeatDirection.FORWARD:
        reply = state.query
    else:
        reply = state.query[::-1]


    return {"messages": [
        {"role": "assistant", "content": reply}
    ]}
