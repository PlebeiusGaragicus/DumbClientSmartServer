"""Streamlit frontend for the Agent Chat Interface."""

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
    if info.get('author'):
        st.write(f"Author: {info['author']}")
    st.write(f"Description: {info['description']}")

def main():

    try:
        # Initialize session state for agents if not exists
        if "agents" not in st.session_state:
            st.session_state.agents = get_agents()
        
        # Create agent selection dropdown
        agent_ids = [agent["data"]["info"]["id"] for agent in st.session_state.agents]
        agent_names = [agent["data"]["info"]["display_name"] for agent in st.session_state.agents]
        
        selected_agent_name = st.radio(
            "Select an Agent",
            options=agent_names,
            horizontal=True,
            label_visibility="collapsed"
        )

        # Map display name back to id
        selected_agent = next(agent["data"]["info"]["id"] 
                            for agent in st.session_state.agents 
                            if agent["data"]["info"]["display_name"] == selected_agent_name)

        # Get the selected agent's data and schema
        agent_data = next(a for a in st.session_state.agents if a["data"]["info"]["id"] == selected_agent)
        
        # Display agent info
        with st.container(border=True):
            # st.subheader("Agent Information")
            display_agent_info(agent_data["data"]["info"])

        # Create and display the dynamic form
        schema_defs = agent_data["schema"]["$defs"]
        input_schema = schema_defs["InputSchema"]["properties"]
        
        DynamicModel = create_dynamic_model(
            agent_name=selected_agent,
            input_schema=input_schema,
            schema_defs=schema_defs
        )

        # Create the form using streamlit_pydantic
        form_key = f"agent_form_{selected_agent}"
        submitted_data = pydantic_form(
            key=form_key,
            model=DynamicModel,
            submit_label="Send",
            clear_on_submit=True
        )

        if submitted_data:
            st.write("Submitted data:", submitted_data)
            # TODO: Implement the chat endpoint call
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
