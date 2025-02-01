"""Streamlit frontend for the Agent Chat Interface."""

import traceback
import streamlit as st
from streamlit_pydantic import pydantic_form
from typing import Dict, Any, Optional

from src.utils import get_agents, create_dynamic_model
from src.config import BACKEND_URL

# Constants
DEFAULT_AGENT_INDEX = 0

def display_agent_info(info: Dict[str, Any]) -> None:
    """Display agent information in the Streamlit interface.
    
    Args:
        info (Dict[str, Any]): Agent information dictionary
    """
    st.write(f"Version: {info['version']}")
    st.write(f"Description: {info['info']}")

def main():
    # Initialize session state for agents if not exists
    if "agents" not in st.session_state:
        st.session_state.agents = get_agents()

    with st.expander("server agents"):
        st.write(st.session_state.agents)

    # Create agent selection dropdown
    agent_ids = [agent["data"]["id"] for agent in st.session_state.agents]
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
    
    # Display agent info
    with st.container(border=True):
        display_agent_info(agent_data["data"])

    # Get the schemas
    input_schema = agent_data["schema"]["input"]
    config_schema = agent_data["schema"]["config"]
    schema_defs = agent_data["schema"]
    
    if st.checkbox("Debug: Show Schema"):
        st.write("Schema:", schema_defs)
        st.write("Input Schema:", input_schema)
        st.write("Config Schema:", config_schema)

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

    # Create tabs for input and config
    input_tab, config_tab = st.tabs(["Input", "Configuration"])

    # Store config in session state to persist between reruns
    if f"config_{selected_agent}" not in st.session_state:
        st.session_state[f"config_{selected_agent}"] = None

    with input_tab:
        # Create the input form
        form_key = f"agent_form_{selected_agent}"
        submitted_data = pydantic_form(
            key=form_key,
            model=InputModel,
            submit_label="Send",
            clear_on_submit=True
        )

    with config_tab:
        # Create the config form
        config_key = f"config_form_{selected_agent}"
        config_data = pydantic_form(
            key=config_key,
            model=ConfigModel,
            submit_label="Save Configuration"
        )
        if config_data:
            st.session_state[f"config_{selected_agent}"] = config_data
            st.success("Configuration saved!")

    if submitted_data:
        st.write("Submitted data:", submitted_data)
        if st.session_state[f"config_{selected_agent}"]:
            st.write("Using configuration:", st.session_state[f"config_{selected_agent}"])        # TODO: Implement the chat endpoint call

if __name__ == "__main__":
    main()
