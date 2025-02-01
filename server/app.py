import dotenv
dotenv.load_dotenv()

from typing import List
from pydantic import BaseModel
import json
import asyncio

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
        input_schema = agent.input_schema.model_json_schema()
        config_schema = agent.config_schema.model_json_schema()
        
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