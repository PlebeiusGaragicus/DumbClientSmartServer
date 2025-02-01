import dotenv
dotenv.load_dotenv()

from typing import List
from pydantic import BaseModel
import json
import asyncio
from enum import Enum
from functools import lru_cache

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="agent testing")

import logging
from util.logger import setup_logging
setup_logging()
logger = logging.getLogger("PlebServe")
logging.getLogger("logger").setLevel(logging.INFO)
logging.getLogger("asyncio").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("watchdog.observers.inotify_buffer").setLevel(logging.INFO)


from graphs import AGENTS



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"], # USE FOR DEVELOPMENT
    allow_origins=["http://localhost:8501"], #TODO Fix this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@lru_cache(maxsize=32)
def generate_schema_for_agent(agent):
    """Generate and cache schema for an agent."""
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
    
    return {
        "input": input_schema,
        "config": config_schema
    }

@app.get("/agents")
async def agents():
    agent_list = []
    for agent in AGENTS:
        agent_data = {
            "id": agent.id,
            "name": agent.name,
            "placeholder": agent.placeholder,
            "info": agent.info,
            "version": agent.version
        }
        
        # Use cached schema generation
        schema = generate_schema_for_agent(agent)
        
        agent_list.append({
            "data": agent_data,
            "schema": schema
        })
    
    return {"agents": agent_list}

class StreamRequest(BaseModel):
    agent_id: str
    input_data: dict = {"messages": []}  # Default to empty list of messages
    config: dict = {}

    def model_dump(self):
        data = super().model_dump()
        # Ensure messages is always a list
        if isinstance(data["input_data"].get("messages"), str):
            data["input_data"]["messages"] = [{"content": data["input_data"]["messages"], "type": "human"}]
        return data

from typing import Any
def serialize_custom_objects(obj: Any) -> Any:
    """Convert custom objects to plain dictionaries"""
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    if isinstance(obj, (set, frozenset)):
        return list(obj)
    return str(obj)

async def stream_generator(agent, input_data, config):
    # async for chunk in agent.graph.astream_events(input=input_data, config=config, version="v2"):
    #     yield json.dumps({"chunk": chunk}) + "\n"

    async for event in agent.graph.astream_events(input=input_data, config=config, version="v2"):
        try:
            serialized_event = json.dumps(
                event, 
                default=serialize_custom_objects
            ).replace('\n', '\\n')

            yield f"data: {serialized_event}\n\n"
        except Exception as e:
            print(f"Serialization error: {e}")


# KEEP THIS
# @app.post("/stream")
# async def stream(request: StreamRequest):
#     # Find the agent with the matching ID
#     agent = next((a for a in AGENTS if a.id == request.agent_id), None)
#     if not agent:
#         return {"error": f"Agent with ID {request.agent_id} not found"}
    
#     return StreamingResponse(
#         stream_generator(agent, request.input_data, request.config),
#         media_type="application/x-ndjson"
#     )

@app.post("/stream")
async def stream(request: StreamRequest):
    # Find the agent with the matching ID
    agent = next((a for a in AGENTS if a.id == request.agent_id), None)
    if not agent:
        return JSONResponse(status_code=404, content={"message": "Agent not found"})
    
    # print("STREAM: ", agent)
    logger.debug("STREAM: ", agent)
    # print(request)
    logger.debug(request)

    # Return the streaming response directly without awaiting
    return StreamingResponse(
        stream_generator(agent, request.input_data, request.config),
        media_type="text/event-stream"
    )
