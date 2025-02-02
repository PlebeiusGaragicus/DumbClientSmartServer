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
    st.caption(f":green[**Version:**] `{info['version']}`")
    st.caption(f":blue[**Description:**] {info['info']}")

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

def handle_stream_response(selected_agent: str, input_data: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Handle streaming response from the agent."""
    try:
        # Convert input data to expected format if needed
        # if not isinstance(input_data.get("messages", []), list):
        if not isinstance(input_data.messages, list):
            input_data.messages = [{"content": input_data.messages, "type": "human"}]

        response = requests.post(
            f"{BACKEND_URL}/stream",
            json={
                "agent_id": selected_agent,
                "input_data": input_data.model_dump(),
                "config": config.model_dump()
            },
            stream=True
        )
        response.raise_for_status()
        
        # Create a placeholder for the streaming output
        message_placeholder = st.empty()
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

                        if name == "__start__" or name == "_write":
                            continue

                        if not event.endswith("_stream"):
                            if name and event:
                                with st.sidebar:
                                    st.header(f"`{event}` {name}")


                        if event.endswith("_stream"):
                            if content:
                                message_placeholder.write(content)
                                full_response += content
                        if event.endswith("_end"):
                            with st.sidebar:
                                st.json(data)


                        message_placeholder.write(full_response + "|")
                    except json.JSONDecodeError as e:
                        st.error(f"Failed to parse event data: {e}")
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
        selected_agent_name = st.radio(
            "Select an Agent",
            options=agent_names,
            horizontal=True,
            label_visibility="collapsed"
        )

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
        if st.button("⚙️ Configure", use_container_width=True):
            show_config_dialog(selected_agent, ConfigModel)

    # Display agent info
    with st.sidebar:
        with st.container(border=True):
            display_agent_info(agent_data["data"])

    # Create the input form
    form_key = f"agent_form_{selected_agent}"
    submitted_data = pydantic_form(
        key=form_key,
        model=InputModel,
        submit_label="Send",
        clear_on_submit=True
    )

    if submitted_data:
        st.write("Submitted data:", submitted_data)
        config = st.session_state[f"config_{selected_agent}"]
        if isinstance(config, dict):
            # Convert dict to model instance if needed
            config = ConfigModel(**config)
            st.session_state[f"config_{selected_agent}"] = config
        st.write("Using configuration:", config)
            
        # Handle the streaming response
        handle_stream_response(selected_agent, submitted_data, config)




    ##########################################################
    if st.session_state.debug:
        with st.sidebar:
            with st.expander("DEBUG"):
                st.write(st.session_state)
##############################################################################
