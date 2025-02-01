"""Utility functions for the Streamlit frontend."""

from enum import Enum
from typing import Any, Dict, List, Tuple, Type, Union, Literal
from pydantic import create_model, Field
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

def resolve_schema_ref(ref: str, schema_defs: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve a schema reference to its definition."""
    # Remove the #/$defs/ prefix to get the definition name
    def_name = ref.split('/')[-1]
    return schema_defs.get("$defs", {}).get(def_name, {})

def create_field_from_schema(field_schema: Dict[str, Any], schema_defs: Dict[str, Any]) -> Tuple[Type, Any]:
    """Create a pydantic field tuple from a JSON schema field definition."""
    field_type: Type = str  # default type
    field_default: Any = ...  # required by default

    # Handle references
    if "$ref" in field_schema:
        ref_schema = resolve_schema_ref(field_schema["$ref"], schema_defs)
        # Merge any overrides from the field schema
        field_schema = {**ref_schema, **field_schema}

    # Handle type mapping
    type_map = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool
    }

    # Get the field type
    if "type" in field_schema:
        field_type = type_map.get(field_schema["type"], str)

    # Handle default values
    if "default" in field_schema:
        field_default = field_schema["default"]
    
    # Build field constraints
    field_metadata = {}
    
    # Copy over all constraints and metadata
    for key in [
        "description", "title", "minimum", "maximum", "multiple_of",
        "min_length", "max_length", "pattern", "format", "readOnly",
        "ge", "le", "gt", "lt"
    ]:
        if key in field_schema:
            field_metadata[key] = field_schema[key]
    
    # Handle enums
    if "enum" in field_schema:
        # Create a proper string Enum class
        enum_name = field_schema.get("title", "DynamicEnum")
        enum_values = field_schema["enum"]
        
        # Create the Enum class
        enum_type = type(
            enum_name,
            (str, Enum),
            {v: v for v in enum_values}  # Use the values directly as both key and value
        )
        
        # Convert default to enum instance if present
        if field_default != ...:
            field_default = enum_type(field_default)
        
        return enum_type, field_default

    # Return field type and configuration
    return field_type, Field(default=field_default, **field_metadata)

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
    
    # Process properties from the input schema
    properties = input_schema.get("properties", {})
    for field_name, field_schema in properties.items():
        field_type, field_config = create_field_from_schema(field_schema, schema_defs)
        model_fields[field_name] = (field_type, field_config)
    
    # Create and return the model
    return create_model(f"{agent_name}_input", **model_fields)
