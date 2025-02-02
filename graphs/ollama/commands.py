import json

from langchain_core.runnables import RunnableConfig

from .config import OllamaConfig
from .state import State


def check_for_command(state: State, config: RunnableConfig):
    configurable = OllamaConfig.from_runnable_config(config)

    if configurable.disable_commands:
        return False

    # check if the last message starts with a '/'
    if state.query.startswith("/"):
        return True
    return False



def handle_command(state: State, config: RunnableConfig):
    # configurable = OllamaConfig.from_runnable_config(config)

    # extract command
    split = state.query.split(" ")
    # Remove the slash and take the first word
    command = split[0][1:].lower()
    arguments = split[1:]

    return {"messages": [{"role": "assistant", "content": f"Command: {command} with arguments {arguments}"}]}




# Markdown text to explain this construct
CONSTRUCT_INFORMATION = """
**Chatbot Agent**

Hi, I'm just some agent dude...

Try `/usage` for a list of commands.
"""


# Markdown text to explain the commands available
USAGE = """
/version                  Get the version of the agent

/info, /about             Get information about the agent

/help, /usage             Get a list of commands

/random [digits]          Get a random number (1-100 by default, or with specified digits)
"""



def handle_commands(request):
    split = request.user_message.split(" ")
    command = split[0][1:].lower() # Remove the slash and take the first word
    arguments = split[1:]


######################################
    if command == "version":
        from .VERSION import VERSION
        yield format_sse_message(f"Version `{VERSION}`")

    elif command == "info" or command == "about":
        yield format_sse_message(CONSTRUCT_INFORMATION)

    elif command == "usage" or command == "help":
        # Send entire usage text as a single event
        response = f"Available commands:\n```\n{USAGE.strip()}```"
        yield format_sse_message(response)
    
    elif command == "random":
        import random
        # If no argument provided, return random number between 1-100
        if len(arguments) == 0:
            random_number = random.randint(1, 100)
            yield format_sse_message(f"`{random_number}`")
        else:
            try:
                digits = int(arguments[0])
                random_number = random.randint(1, 10**digits)
                # yield format_sse_message(f"Random number: {random_number}")
                yield format_sse_message(f"`{random_number}`")
            except ValueError:
                yield format_sse_message("Invalid number of digits. Please provide a single integer.")


    # elif command == "debug":
    #     debug_info = f"# body:\n```json\n{json.dumps(request.body, indent=4)}\n```\n# model_id:"
    #     yield format_sse_message(debug_info)



######################################
    else:
        response = f"Command not found.\nAvailable commands:\n```\n{USAGE.strip()}```"
        yield format_sse_message(response)
