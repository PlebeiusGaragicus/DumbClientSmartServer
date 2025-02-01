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

@st.dialog("Agent Configuration")
def show_config_dialog(selected_agent: str, ConfigModel: Any) -> None:
    """Show the configuration dialog for the selected agent.
    
    Args:
        selected_agent (str): The ID of the selected agent
        ConfigModel (Any): The configuration model class
    """
    config_key = f"config_form_{selected_agent}"
    saved_config = st.session_state.get(f"config_{selected_agent}")
    
    # Debug output
    st.write("### Config Dialog Debug")
    st.write("ConfigModel:", ConfigModel)
    st.write("ConfigModel fields:", ConfigModel.model_fields)
    st.write("Saved config:", saved_config)
    if saved_config:
        st.write("Saved config type:", type(saved_config))
        if hasattr(saved_config, "model_dump"):
            st.write("Saved config dump:", saved_config.model_dump())
    
    # Convert dict to model instance if needed
    if isinstance(saved_config, dict):
        saved_config = ConfigModel(**saved_config)
        st.write("Converted config:", saved_config)
        st.write("Converted config type:", type(saved_config))
    
    # Use saved config or create new instance
    model_instance = saved_config if saved_config else ConfigModel()
    st.write("Model instance:", model_instance)
    st.write("Model instance type:", type(model_instance))
    
    config_data = pydantic_form(
        key=config_key,
        model=model_instance,
        submit_label="Save Configuration"
    )
    if config_data:
        st.session_state[f"config_{selected_agent}"] = config_data
        st.session_state.show_config_dialog = False
        st.rerun()

def main():
    # Initialize session state for agents if not exists
    if "agents" not in st.session_state:
        st.session_state.agents = get_agents()

    with st.expander("server agents"):
        st.write(st.session_state.agents)

    # Create agent selection dropdown
    agent_ids = [agent["data"]["id"] for agent in st.session_state.agents]
    agent_names = [agent["data"]["name"] for agent in st.session_state.agents]
    
    col1, col2 = st.columns([4, 1])
    with col1:
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

    # Debug output
    st.write("### Config Model Details")
    st.write("Model schema:", ConfigModel.model_json_schema())
    st.write("Model fields:", ConfigModel.model_fields)
    st.write("Model attributes:", [attr for attr in dir(ConfigModel) if not attr.startswith('_')])

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

    # Add configuration button in the second column
    with col2:
        if st.button("⚙️ Configure"):
            show_config_dialog(selected_agent, ConfigModel)

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
        # TODO: Implement the chat endpoint call

if __name__ == "__main__":
    main()

    with st.sidebar:
        st.write(st.session_state)
