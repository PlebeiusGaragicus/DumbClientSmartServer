"""Streamlit frontend for the Agent Chat Interface."""

import os
import traceback
import streamlit as st
from streamlit_pydantic import pydantic_form
from typing import Dict, Any, Optional
import requests
import json
import logging

##############################################################################
logger = logging.getLogger("PlebChat")


from src.utils import get_agents, create_dynamic_model
from src.config import BACKEND_URL

##############################################################################
# Constants
DEFAULT_AGENT_INDEX = 0



def new_thread():
    st.session_state.message_history = []
    # st.toast("New thread!")


##############################################################################
@st.dialog("Agent Information", width="large")
def display_agent_info(info: Dict[str, Any]) -> None:
    """Display agent information in the Streamlit interface.
    
    Args:
        info (Dict[str, Any]): Agent information dictionary
    """
    with st.container(border=True):
        st.write(info['info'])

    # st.write(f"Version: {info['version']}")
    # st.caption(f":blue[**Description:**] {info['info']}")
    # st.write(f":blue[**Description:**]")
    # st.divider()
    # st.caption(f":green[**Version:**] `{info['version']}`")

@st.dialog("Agent Configuration")
def show_config_dialog(selected_agent: str, ConfigModel: Any) -> None:
    """Show the configuration dialog for the selected agent.

    Args:
        selected_agent (str): The ID of the selected agent
        ConfigModel (Any): The configuration model class
    """
    config_key = f"config_form_{selected_agent}"
    saved_config = st.session_state.get(f"config_{selected_agent}")
    
    # Convert dict to model instance if needed
    if isinstance(saved_config, dict):
        saved_config = ConfigModel(**saved_config)
    
    # Use saved config or create new instance
    model_instance = saved_config if saved_config else ConfigModel()
    
    config_data = pydantic_form(
        key=config_key,
        model=model_instance,
        submit_label=":green[Save Configuration]"
    )
    if config_data:
        st.session_state[f"config_{selected_agent}"] = config_data
        st.rerun()

# def handle_stream_response(selected_agent: str, input_data: Dict[str, Any], config: Dict[str, Any], InputModel: Any) -> None:
def handle_stream_response(selected_agent: str, query: str, config: Dict[str, Any]) -> None:
    """Handle streaming response from the agent.
    
    Args:
        selected_agent (str): The ID of the selected agent
        query (str): The query from the form
        config (Dict[str, Any]): The configuration for the agent
        InputModel (Any): The Pydantic model class for the input data
    """
    try:
        # st.session_state.message_history.append(
        #     {"role": "human", "content": query}
        # )

        # Create a proper InputModel with query and message history
        # input_data_dict = input_data.model_dump()
        # input_data_dict["messages"] = st.session_state.message_history

        # New simplified input data
        input_data_dict = {
            "query": query,
            "messages": st.session_state.message_history
        }

        # Prepare the request payload
        payload = {
            "agent_id": selected_agent,
            "input_data": input_data_dict,
            "config": config.model_dump() if hasattr(config, 'model_dump') else config
        }

        response = requests.post(
            f"{BACKEND_URL}/stream",
            json=payload,
            stream=True
        )
        response.raise_for_status()
        
        # Create a placeholder for the streaming output
        # message_placeholder = message_container.empty()
        # message_placeholder = st.chat_message("assistant").empty()
        # message_container = st.chat_message("assistant")

        # message_container = st.empty()
        # with message_container:
        #     message_placeholder = st.chat_message("assistant")
        message_container = st.chat_message("assistant")
        message_placeholder = message_container.empty()

        with st.sidebar:
            status = st.empty()

        full_response = ""

        # Process the streaming response
        with st.spinner("🧠 Thinking..."):
            try:
                for line in response.iter_lines():
                    # logger.debug(line)
                    # print(line)

                    if line and line.startswith(b'data: '):

                        # Remove the "data: " prefix and decode
                        event_data = line[6:].decode('utf-8')

                        try:
                            # print(json.dumps(event_data, indent=4))
                            event_data = json.loads(event_data)
                            name = event_data.get("name", None)
                            event = event_data.get("event", None)
                            data = event_data.get("data", None)
                            if data:
                                chunk = data.get("chunk", None)
                                if chunk:
                                    content = chunk.get("content", None)

                            # Gather final graph output here
                            if name == "LangGraph" and event.endswith("_end"):
                                output = data.get("output", None)

                            # Skip these events:
                            # "__start__" - beginning pseudo-node of the graph
                            # "_write" - write events to the graph state
                            # "LangGraph" - first and last events of the graph
                            # "_" - nodes that start with a '_' character can be ignored.  Can be useful to hide execution of "conditional nodes"
                            if name == "__start__" or name == "_write" or name == "LangGraph" or name.startswith("_"):
                                continue

                            # NOTE: These are events signifying the beginning of node execution
                            # Print events that aren't LLM token streams or on_chat_model LLM calls
                            # TODO: create new st.status() and set to "running"
                            # TODO: write a newline to the chat history and an st.divider
                            if not event.endswith("_stream") and not event.startswith("on_chat_model"):
                                if name and event:
                                    # Initialize or reset session state at the start of a new run
                                    if event.endswith("_start") and name == "LangGraph":
                                        if 'status_container' not in st.session_state:
                                            st.session_state.status_container = st.sidebar.container()
                                        st.session_state.status_container.empty()
                                        continue

                                    # Create the status element
                                    if not event.endswith("_end"):
                                        with st.sidebar:
                                            # Transform name: replace underscores with spaces and capitalize words
                                            Proper_node_name = ' '.join(word.capitalize() for word in name.split('_'))
                                            status = st.status(f":green[{Proper_node_name}]", expanded=True, state="running")
                                            # with status:
                                            #     st.markdown(f"**Event:** `{event}`")
                            # HOTE: These are LLM token streams
                            if event.endswith("_stream"):
                                if content:
                                    if content == "</think>":
                                        content += '\n\n---\n\n'

                                    full_response += content
                                    message_placeholder.markdown(full_response + ":red[▌]")

                            # Update status with output when execution ends
                            if event.endswith("_end"):
                                with st.sidebar:
                                    # status = st.status(f"Node: {name}", expanded=False, state="complete")
                                    with status as s:
                                        # st.markdown(f"**Event:** `{event}`")
                                        # st.markdown("**Output:**")
                                        s.update(state="complete", expanded=False)
                                        try:
                                            # st.json(data['output'])
                                            for key in data['output']:
                                                st.write(f"**{key}**")
                                                st.write(data['output'][key])

                                        except Exception as e:
                                            st.markdown(data)

                                full_response += '\n\n---\n\n'
                                message_placeholder.markdown(full_response + ":red[▌]")

                            # HOTE: These are the end of node execution events
                            # TODO: we need to ensure our st.status() is set to "done" here
                            # if event.endswith("_end"):
                            #     with st.sidebar:
                            #         with st.expander("Node output:"):
                            #             try:
                            #                 st.json(data['output'])
                            #             except Exception as e:
                            #                 st.json(data)


                            # message_placeholder.write(full_response + "|")

                        except json.JSONDecodeError as e:
                            st.error(f"Failed to parse event data: {e}")


                ### END OF STREAMING `FOR` LOOP

                if output:
                    # with st.sidebar.expander("🙌 Output"):
                    #     st.write(output)


                    #TODO: we need to ensure that we can capture any graph's arbitrary outputs
                    try:
                        reply = output['messages'][-1]['content']
                    except:
                        reply = output['running_summary']

                    st.session_state.message_history.append({"role": "assistant", "content": reply})

                    message_placeholder.empty()
                    message_container.markdown(reply)
                    # message_container.header("", divider="rainbow")

            except requests.exceptions.ChunkedEncodingError:
                st.warning("Stream ended unexpectedly.")


    except Exception as e:
        st.error(f"Error during streaming: {str(e)}")
        traceback.print_exc()



##############################################################################

def main():
    logger.info("Starting frontend")

    st.set_page_config(
        page_title="DumbClientSmartServer",
        layout="wide"
    )

    if st.session_state.get("DEBUG", None) is None:
        st.session_state.debug = os.getenv("DEBUG", False)

    # Initialize session state for agents if not exists
    if "agents" not in st.session_state:
        print("DEBUG --- GETTING AGENTS GETTING AGENTS GETTING AGENTS")
        st.session_state.agents = get_agents()

    st.markdown("# :rainbow[PlebChat] 🗣️🤖💬")

    # with st.container(border=True):
    agent_names = [agent["data"]["name"] for agent in st.session_state.agents]
    selected_agent_name = st.segmented_control(
        "Select an Agent",
        options=agent_names,
        default=agent_names[0],
        label_visibility="collapsed",
        on_change=new_thread
    )

    if not selected_agent_name:
        #TODO: perhaps we should have this be the default view when the user visits the site
        st.success("Select an agent.", icon="👆")
        with st.sidebar:
            st.write("") # this ensures the sidebar stays visible
        st.stop()


    # Map display name back to id
    selected_agent = next(agent["data"]["id"] 
                        for agent in st.session_state.agents 
                        if agent["data"]["name"] == selected_agent_name)

    # Get the selected agent's data and schema
    agent_data = next(a for a in st.session_state.agents if a["data"]["id"] == selected_agent)
    # if not len(st.session_state.message_history):
    with st.container(border=True):
        st.write(agent_data["data"]["info"])

    # Initialize message history in session state if it doesn't exist
    if "message_history" not in st.session_state:
        st.session_state.message_history = []

    for message in st.session_state.message_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    # Get the schemas
    config_schema = agent_data["schema"]["config"]
    schema_defs = agent_data["schema"]

    ConfigModel = create_dynamic_model(
        agent_name=f"{selected_agent}_config",
        input_schema=config_schema,
        schema_defs=schema_defs
    )

    # Store config in session state to persist between reruns
    if f"config_{selected_agent}" not in st.session_state:
        # Get default values from schema
        defaults = {}
        for field, schema in config_schema.get("properties", {}).items():
            if "$ref" in schema:
                # Get the referenced definition
                ref_name = schema["$ref"].split("/")[-1]
                ref_schema = schema_defs.get("$defs", {}).get(ref_name, {})
                if "default" in schema:
                    defaults[field] = schema["default"]
            elif "default" in schema:
                defaults[field] = schema["default"]
        
        # Initialize with default config
        st.session_state[f"config_{selected_agent}"] = ConfigModel(**defaults)

    with st.sidebar:
        # st.markdown("# :rainbow[PlebChat] 🗣️🤖💬")

        # if st.button("📖 Agent Info", use_container_width=True):
        #     display_agent_info(agent_data["data"])

        if len(st.session_state.message_history):
            if st.button("🌱 :green[New Thread]", use_container_width=True):
                new_thread()

        if st.button("⚙️ :blue[Configure]", use_container_width=True):
            show_config_dialog(selected_agent, ConfigModel)


    selected_agent_stuff = next(agent for agent in st.session_state.agents if agent["data"]["name"] == selected_agent_name)
    agent_placeholder = selected_agent_stuff["data"]["placeholder"]

    if prompt := st.chat_input(placeholder=agent_placeholder, key="query"):
        st.session_state.message_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.sidebar:
            st.header(":red[Execution Trace:]", divider="rainbow")
            with st.expander("Submitted to graph:"):
                # st.write("Submitted data:", submitted_data)
                st.write(f"`query:` {prompt}")
                st.write(f"`Messages:`", st.session_state.message_history)
                config = st.session_state[f"config_{selected_agent}"]
                if isinstance(config, dict):
                    # Convert dict to model instance if needed
                    config = ConfigModel(**config)
                    st.session_state[f"config_{selected_agent}"] = config
                st.write("`configuration:`", config)

        # Handle the streaming response
        # with st.spinner("🧠 Thinking..."):
        handle_stream_response(selected_agent, prompt, config)

    if len(st.session_state.message_history):
        if st.button(":grey[:material/undo: Undo last message]", type="tertiary"):
            st.session_state.message_history = st.session_state.message_history[:-2]
            st.rerun()

    ##########################################################
    @st.dialog("session_state", width="large")
    def debug_dialog():
        st.write(st.session_state)
    with st.sidebar:
        st.divider()

        if st.button("🪲 :orange[Debug]", use_container_width=True):
            debug_dialog()
##############################################################################
