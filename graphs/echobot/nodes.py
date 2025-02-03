from langchain_core.runnables import RunnableConfig

from .state import State, Config, RepeatDirection

############################################################################
# NODE
# simply return what the user said, according to configuration
############################################################################
def echobot(state: State, config: RunnableConfig):
    configurable = Config.from_runnable_config(config)

    if configurable.repeat_direction == RepeatDirection.FORWARD:
        reply = state.query
    else:
        reply = state.query[::-1]

    return {"messages": [{"role": "assistant", "content": reply}]}