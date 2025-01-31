"""Utility functions for the Streamlit frontend."""

from enum import Enum
from typing import Any, Dict, List, Tuple, Type, Union
from pydantic import create_model
from .config import BACKEND_URL

def get_agents() -> List[Dict[str, Any]]:
    """Fetch available agents from the backend.
    
    Returns:
        List[Dict[str, Any]]: List of agent configurations
    
    Raises:
        requests.RequestException: If the backend request fails
    """
    import requests
    try:
        response = requests.get(f"{BACKEND_URL}/agents")
        response.raise_for_status()
        return response.json()["agents"]
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch agents: {str(e)}")

def create_enum_from_schema(enum_values: list) -> Type[Enum]:
    """Create an Enum class from a list of valid values.
    
    Args:
        enum_values (list): List of enum values
        
    Returns:
        Type[Enum]: Generated Enum class
    """
    return Enum('DynamicEnum', {str(v).upper(): str(v) for v in enum_values})

def create_field_from_schema(field_schema: Dict[str, Any]) -> Tuple[Type, Any]:
    """Create a pydantic field tuple from a JSON schema field definition.
    
    Args:
        field_schema (Dict[str, Any]): JSON schema field definition
        
    Returns:
        Tuple[Type, Any]: Tuple of (field_type, field_default)
    """
    field_type: Type = str  # default type
    field_default: Any = ...  # required by default
    
    if field_schema.get("enum"):
        field_type = create_enum_from_schema(field_schema["enum"])
        if "default" in field_schema:
            field_default = field_type(field_schema["default"])
    elif field_schema.get("type") == "string":
        field_type = str
        if "default" in field_schema:
            field_default = field_schema["default"]
    elif field_schema.get("type") == "integer":
        field_type = int
        if "default" in field_schema:
            field_default = field_schema["default"]
    
    return (field_type, field_default)

def create_dynamic_model(
    agent_name: str,
    input_schema: Dict[str, Any],
    schema_defs: Dict[str, Any]
) -> Type:
    """Create a dynamic Pydantic model from the input schema.
    
    Args:
        agent_name (str): Name of the agent
        input_schema (Dict[str, Any]): Input schema definition
        schema_defs (Dict[str, Any]): Schema definitions
        
    Returns:
        Type: Generated Pydantic model
    """
    model_fields = {}
    for field_name, field_schema in input_schema.items():
        if "$ref" in field_schema:
            # Handle enum references
            enum_name = field_schema["$ref"].split("/")[-1]
            enum_schema = schema_defs[enum_name]
            field_schema = {**field_schema, "enum": enum_schema["enum"]}
        model_fields[field_name] = create_field_from_schema(field_schema)

    return create_model(
        f"{agent_name}Input",
        **model_fields
    )
