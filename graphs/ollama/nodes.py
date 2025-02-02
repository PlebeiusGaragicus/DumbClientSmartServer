from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama



from .config import OllamaConfig, OLLAMA_HOST
from .state import State




############################################################################
def chatbot(state: State, config: RunnableConfig):
    configurable = OllamaConfig.from_runnable_config(config)

    llm = ChatOllama(
        model=configurable.model,
        keep_alive=configurable.keep_alive,
        temperature=configurable.temperature / 100,
        base_url=OLLAMA_HOST,
    )

    # The messages are already LangChain message objects, use them directly
    messages = state.messages
    # append user query to messages
    #NOTE: we don't do this anymore - it's done in the UI
    # messages.append(HumanMessage(content=state.query))

    response = llm.stream(messages)

    # Join all chunks into a single response
    full_response = "".join(chunk.content for chunk in response)
    # return {"reply": full_response}
    return {"messages": [
        # {"role": "human", "content": state.query},
        {"role": "assistant", "content": full_response}
    ]}

    # return {"messages": [{"role": "assistant", "content": chunk.content} for chunk in response]}
