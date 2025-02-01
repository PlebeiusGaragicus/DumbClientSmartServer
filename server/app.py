import dotenv
dotenv.load_dotenv()

from typing import List
from pydantic import BaseModel
import json
import asyncio
from enum import Enum

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="agent testing")

from graphs import AGENTS



# Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     # allow_origins=["*"], # USE FOR DEVELOPMENT
#     allow_origins=["http://localhost:8501"], #TODO Fix this for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/agents")
async def agents():
    agent_list = []
    for agent in AGENTS:
        # Get full schemas with enum values
        input_schema = agent.input_schema.model_json_schema(mode='serialization')
        config_schema = agent.config_schema.model_json_schema(mode='serialization')
        
        # Add enum values for any enum fields
        for schema in [input_schema, config_schema]:
            for prop in schema.get("properties", {}).values():
                if hasattr(prop.get("type", None), "__args__"):
                    enum_type = prop["type"].__args__[0]
                    if issubclass(enum_type, Enum):
                        prop["enum"] = [e.value for e in enum_type]
        
        agent_data = {
            "id": agent.id,
            "name": agent.name,
            "placeholder": agent.placeholder,
            "info": agent.info,
            "version": agent.version
        }
        
        agent_list.append({
            "data": agent_data,
            "schema": {
                "input": input_schema,
                "config": config_schema
            }
        })
    
    return {"agents": agent_list}