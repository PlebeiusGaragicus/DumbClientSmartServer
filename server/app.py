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
    for agent_class in AGENTS.values():
        agent = agent_class()
        agent_data = agent.model_dump()
        agent_schema = agent_class.model_json_schema()
        agent_list.append({
            "data": agent_data,
            "schema": agent_schema
        })
    return {"agents": agent_list}