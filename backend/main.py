"""
Aegis SRE Guardian - FastAPI Application
Provides REST endpoints for incident monitoring,
overnight autonomy simulation, conversational chat, and Hindsight Cloud memory banking.
"""

import os

# Load .env file automatically
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    if v:
                        os.environ[k] = v

load_env()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.memory_manager import MemoryManager
from backend.guardian_agent import GuardianAgent

app = FastAPI(title="Aegis SRE Guardian API", description="Autonomous SRE Assistant Powered by Hindsight Cloud")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bank_id = os.getenv("HINDSIGHT_BANK_ID", "production-app")
api_key = os.getenv("HINDSIGHT_API_KEY", "")
base_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")

memory_mgr = MemoryManager(base_url=base_url, api_key=api_key, bank_id=bank_id)
agent = GuardianAgent(memory_manager=memory_mgr)

class OvernightRequest(BaseModel):
    scenario_type: str = "known_issue"  # "known_issue" or "novel_issue"

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

class TeachRequest(BaseModel):
    rule_text: str
    category: Optional[str] = "System Policy"

class ConfigRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    hindsight_base_url: Optional[str] = None
    hindsight_api_key: Optional[str] = None


@app.get("/api/status")
def get_service_status():
    return {
        "service_name": "Production Application Gateway",
        "monitoring_target": "https://api.production.app/health",
        "hindsight_backend": "Hindsight Cloud (Connected)",
        "memory_bank": bank_id,
        "status": "HEALTHY",
        "uptime": "99.98%",
        "current_latency": "38ms",
        "active_rules_in_memory": len(memory_mgr.get_all())
    }


@app.post("/api/overnight")
def run_overnight_simulation(req: OvernightRequest):
    return agent.process_overnight_event(scenario_type=req.scenario_type)


@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return agent.chat(user_message=req.message, chat_history=req.history)


@app.get("/api/memories")
def get_memories():
    return {
        "count": len(memory_mgr.get_all()),
        "memories": memory_mgr.get_all(),
        "hindsight_cloud": bool(memory_mgr.client)
    }


@app.post("/api/teach")
def teach_rule(req: TeachRequest):
    new_mem = memory_mgr.retain(
        incident_id=f"POLICY-{int(memory_mgr.local_memories.__len__() + 1):03d}",
        title=f"Policy: {req.category}",
        symptoms="Developer configured architectural guardrail",
        root_cause=req.rule_text,
        successful_resolution=req.rule_text,
        failed_attempts=[],
        runbook_command="Active Operational Policy",
        vigilance_stage="BATTLE_TESTED",
        tags=["policy", "developer-rule"]
    )
    return {
        "status": "SAVED",
        "message": f"Saved rule to Hindsight Cloud memory: '{req.rule_text}'",
        "memory": new_mem
    }


@app.post("/api/config")
def update_config(req: ConfigRequest):
    if req.gemini_api_key:
        agent.update_key(req.gemini_api_key)
    if req.hindsight_api_key or req.hindsight_base_url:
        memory_mgr.update_credentials(
            base_url=req.hindsight_base_url or memory_mgr.base_url,
            api_key=req.hindsight_api_key or memory_mgr.api_key
        )
    return {"status": "CONFIG_UPDATED"}


# Static asset mounting
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
