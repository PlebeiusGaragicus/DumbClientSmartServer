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






##############################################################################
def display_agent_info(info: Dict[str, Any]) -> None:
    """Display agent information in the Streamlit interface.
    
    Args:
        info (Dict[str, Any]): Agent information dictionary
    """
    # st.write(f"Version: {info['version']}")
    # st.caption(f":blue[**Description:**] {info['info']}")
    # st.write(f":blue[**Description:**]")
    st.write(info['info'])
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
        st.session_state.show_config_dialog = False
        st.rerun()

def handle_stream_response(selected_agent: str, input_data: Dict[str, Any], config: Dict[str, Any], InputModel: Any) -> None:
    """Handle streaming response from the agent.
    
    Args:
        selected_agent (str): The ID of the selected agent
        input_data (Dict[str, Any]): The input data from the form
        config (Dict[str, Any]): The configuration for the agent
        InputModel (Any): The Pydantic model class for the input data
    """
    try:
        st.session_state.message_history.append(
            {"role": "human", "content": input_data.query}
        )

        # Create a proper InputModel with query and message history
        input_data_dict = input_data.model_dump()
        input_data_dict["messages"] = st.session_state.message_history

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
        # message_placeholder = st.empty()
        message_container = st.chat_message("assistant")
        message_placeholder = message_container.empty()
        # message_placeholder = st.chat_message("assistant").empty()
        full_response = ""

        # Process the streaming response
        try:
            for line in response.iter_lines():
                # logger.debug(line)
                # print(line)
                if line and line.startswith(b'data: '):
                    # Remove the "data: " prefix and decode
                    event_data = line[6:].decode('utf-8')
                    try:
                        event_data = json.loads(event_data)
                        # print(json.dumps(event_data, indent=4))


                        name = event_data.get("name", None)
                        event = event_data.get("event", None)
                        data = event_data.get("data", None)

                        if data:
                            chunk = data.get("chunk", None)
                            if chunk:
                                content = chunk.get("content", None)
                                # if content:

                        if name == "LangGraph" and event.endswith("_end"):
                            output = data.get("output", None)


                        if name == "__start__" or name == "_write" or name == "LangGraph" or name.startswith("_"):
                            continue

                        if not event.endswith("_stream") and not event.startswith("on_chat_model"):
                            if name and event:
                                with st.sidebar:
                                    st.header(f"`{event}` {name}")


                        if event.endswith("_stream"):
                            if content:
                                # message_placeholder.write(content)
                                full_response += content
                                message_placeholder.markdown(full_response + "▌")

                        if event.endswith("_end"):
                            with st.sidebar:
                                with st.expander("data"):
                                    st.json(data)

                        # message_placeholder.write(full_response + "|")

                    except json.JSONDecodeError as e:
                        st.error(f"Failed to parse event data: {e}")


            ### END OF STREAMING `FOR` LOOP

            if output:
                with st.sidebar.expander("🙌 Output"):
                    st.write(output)

                reply = output['messages'][-1]['content']

                st.session_state.message_history.append({"role": "assistant", "content": reply})
                
                message_placeholder.empty()
                message_container.markdown(reply)
                # st.chat_message("assistant").write(reply)

        except requests.exceptions.ChunkedEncodingError:
            st.warning("Stream ended unexpectedly.")


    except Exception as e:
        st.error(f"Error during streaming: {str(e)}")
        traceback.print_exc()



##############################################################################

def main():
    logger.info("Starting frontend")

    if st.session_state.get("DEBUG", None) is None:
        st.session_state.debug = os.getenv("DEBUG", False)

    # Initialize session state for agents if not exists
    if "agents" not in st.session_state:
        print("DEBUG --- GETTING AGENTS GETTING AGENTS GETTING AGENTS")
        st.session_state.agents = get_agents()

    with st.container(border=True):
        agent_names = [agent["data"]["name"] for agent in st.session_state.agents]
        selected_agent_name = st.segmented_control(
            "Select an Agent",
            options=agent_names,
            default=agent_names[0],
            label_visibility="collapsed"
        )
        # selected_agent_name = st.radio(
        #     "Select an Agent",
        #     options=agent_names,
        #     horizontal=True,
        #     label_visibility="collapsed"
        # )

    # Map display name back to id
    selected_agent = next(agent["data"]["id"] 
                        for agent in st.session_state.agents 
                        if agent["data"]["name"] == selected_agent_name)

    # Get the selected agent's data and schema
    agent_data = next(a for a in st.session_state.agents if a["data"]["id"] == selected_agent)

    # Get the schemas
    input_schema = agent_data["schema"]["input"]
    config_schema = agent_data["schema"]["config"]
    schema_defs = agent_data["schema"]

    # Create both input and config models
    InputModel = create_dynamic_model(
        agent_name=f"{selected_agent}_input",
        input_schema=input_schema,
        schema_defs=schema_defs
    )

    # Create a copy of the input schema without the messages field
    input_schema_without_messages = input_schema.copy()
    if "properties" in input_schema_without_messages:
        properties = input_schema_without_messages["properties"].copy()
        if "messages" in properties:
            del properties["messages"]
        input_schema_without_messages["properties"] = properties

    InputModel_withoutmessages = create_dynamic_model(
        agent_name=f"{selected_agent}_input_nomessages",
        input_schema=input_schema_without_messages,
        schema_defs=schema_defs
    )

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

    if "show_config_dialog" not in st.session_state:
        st.session_state.show_config_dialog = False

    with st.sidebar:
        st.markdown("# :rainbow[PlebChat] 🗣️🤖💬")
        if st.button("⚙️ Configure", use_container_width=True):
            show_config_dialog(selected_agent, ConfigModel)

        with st.container(border=True):
            display_agent_info(agent_data["data"])

        st.divider()

    # Initialize message history in session state if it doesn't exist
    if "message_history" not in st.session_state:
        st.session_state.message_history = []
    

    # Create the input form
    form_key = f"agent_form_{selected_agent}"
    submitted_data = pydantic_form(
        key=form_key,
        model=InputModel_withoutmessages,
        submit_label="Send",
        clear_on_submit=True
    )

    for message in st.session_state.message_history:
        st.chat_message(message["role"]).write(message["content"])

    if submitted_data:
        st.chat_message("user").write(submitted_data.query)

        with st.sidebar:
            with st.expander("Submitted to graph:"):
                st.write("Submitted data:", submitted_data)
                config = st.session_state[f"config_{selected_agent}"]
                if isinstance(config, dict):
                    # Convert dict to model instance if needed
                    config = ConfigModel(**config)
                    st.session_state[f"config_{selected_agent}"] = config
                st.write("Using configuration:", config)

        # Handle the streaming response
        handle_stream_response(selected_agent, submitted_data, config, InputModel)


    ##########################################################
    if st.session_state.debug:
        with st.sidebar:
            with st.expander("DEBUG"):
                st.write(st.session_state)
##############################################################################
