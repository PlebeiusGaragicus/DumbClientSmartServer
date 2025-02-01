"""Utility functions for the Streamlit frontend."""

from enum import Enum
from typing import Any, Dict, List, Tuple, Type, Union
from pydantic import create_model, Field, BaseModel
import streamlit as st

from .config import BACKEND_URL, AGENTS_ENDPOINT_CACHE_DURATION

@st.cache_data(ttl=AGENTS_ENDPOINT_CACHE_DURATION)  # Cache for 5 minutes
def get_agents() -> List[Dict[str, Any]]:
    """Fetch available agents from the backend with caching."""
    import requests
    try:
        response = requests.get(f"{BACKEND_URL}/agents")
        response.raise_for_status()
        return response.json()["agents"]
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch agents: {str(e)}")

def create_enum_from_schema(enum_values: list, enum_name: str) -> Type[Enum]:
    """Create an Enum class from a list of values."""
    # Create enum members dictionary
    members = {value.upper(): value for value in enum_values}
    
    # Create the enum class with the members
    return Enum(enum_name, members, type=str)

def resolve_schema_ref(ref: str, schema_defs: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve a schema reference to its definition."""
    # Remove the #/$defs/ prefix to get the definition name
    def_name = ref.split('/')[-1]
    return schema_defs.get("$defs", {}).get(def_name, {})

def create_field_from_schema(field_schema: Dict[str, Any], schema_defs: Dict[str, Any]) -> Tuple[Type, Any]:
    """Create a pydantic field tuple from a JSON schema field definition."""
    field_type: Type = str  # default type
    field_default: Any = ...  # required by default

    # Handle references first
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
    field_kwargs = {}
    
    # Copy over all constraints and metadata
    for key in [
        "description", "title", "minimum", "maximum", "multiple_of",
        "min_length", "max_length", "pattern", "format", "readOnly",
        "ge", "le", "gt", "lt"
    ]:
        if key in field_schema:
            field_kwargs[key] = field_schema[key]
    
    # Handle enums
    if "enum" in field_schema:
        # Create an Enum class for this property
        enum_name = field_schema.get("title", "DynamicEnum")
        enum_class = create_enum_from_schema(field_schema["enum"], enum_name)
        field_type = enum_class
        if field_default != ...:
            # Find the enum member with this value
            field_default = next(e for e in enum_class if e.value == field_default)
        field_kwargs["default"] = field_default
        return field_type, Field(**field_kwargs)

    # Return field type and configuration
    field_kwargs["default"] = field_default
    return field_type, Field(**field_kwargs)

def create_dynamic_model(
    agent_name: str,
    input_schema: Dict[str, Any],
    schema_defs: Dict[str, Any]
) -> Type[BaseModel]:
    """Create a dynamic Pydantic model from the input schema."""
    fields = {}
    enums = {}
    
    # First, create any enum types defined in $defs
    defs = input_schema.get("$defs", {})
    for def_name, def_schema in defs.items():
        if "enum" in def_schema:
            enum_class = create_enum_from_schema(def_schema["enum"], def_schema.get("title", def_name))
            enums[def_name] = enum_class
    
    # Process properties from the input schema
    properties = input_schema.get("properties", {})
    for field_name, field_schema in properties.items():
        # If this field references an enum we created from $defs, use it
        if "$ref" in field_schema:
            ref_name = field_schema["$ref"].split("/")[-1]
            if ref_name in enums:
                enum_class = enums[ref_name]
                field_default = field_schema.get("default", ...)
                if field_default != ...:
                    # Find the enum member with this value
                    field_default = next(e for e in enum_class if e.value == field_default)
                fields[field_name] = (enum_class, Field(
                    default=field_default,
                    description=field_schema.get("description", "")
                ))
                continue
        
        # Otherwise create field normally
        field_type, field_config = create_field_from_schema(field_schema, schema_defs)
        fields[field_name] = (field_type, field_config)
        
        # Store enum classes for reference
        if isinstance(field_type, type) and issubclass(field_type, Enum):
            enums[field_name] = field_type
    
    # Create the model
    model = create_model(f"{agent_name}_input", **fields)
    
    # Store created enums as class attributes
    for name, enum_class in enums.items():
        setattr(model, f"{name}_enum", enum_class)
    
    return model
