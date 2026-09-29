import os
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from backend.hindsight_client import HindsightMemoryManager
from backend.gemini_client import GeminiSupportAgent
from backend.action_engine import ActionEngine
from backend.behavior_router import BehaviorRouter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main_server")

app = FastAPI(title="MindSupport AI - Multi-User Behavioral Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hindsight = HindsightMemoryManager()
gemini = GeminiSupportAgent()
action_engine = ActionEngine()
behavior_router = BehaviorRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

def load_all_users() -> List[Dict[str, Any]]:
    customers_file = os.path.join(DATA_DIR, "customers.json")
    with open(customers_file, "r", encoding="utf-8") as f:
        return json.load(f)

dynamic_users: Dict[str, Dict[str, Any]] = {}

def get_user_by_id(user_id: str, name: Optional[str] = None, phone: Optional[str] = None, address: Optional[str] = None) -> Dict[str, Any]:
    users = load_all_users()
    matched = next((u for u in users if u["id"].lower() == user_id.lower()), None)
    if matched:
        return matched

    if user_id in dynamic_users:
        if name: dynamic_users[user_id]["name"] = name
        if phone: dynamic_users[user_id]["phone"] = phone
        if address: dynamic_users[user_id]["address"] = address
        return dynamic_users[user_id]

    formatted_name = name or user_id.replace("_", " ").title()
    new_user = {
        "id": user_id,
        "name": formatted_name,
        "phone": phone or "+1 (555) 019-9000",
        "address": address if address else "Not provided yet",
        "role": "New Customer",
        "plan": "Standard Customer Account",
        "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_id}",
        "sentiment": "Neutral",
        "temperament": "Curious, Open",
        "volatility_score": 30,
        "recommended_specialist": "emily_smb",
        "orders": [],
        "preloaded_memories": [
            f"New customer registered: {formatted_name}. Contact Phone: {phone or '+1 (555) 019-9000'}."
        ]
    }
    dynamic_users[user_id] = new_user
    hindsight.retain(
        tag=user_id,
        content=f"Customer Profile Registered: {formatted_name} (ID: {user_id}). Phone: {new_user['phone']}. Address: {new_user['address']}.",
        context="customer_profile"
    )
    return new_user

class ChatRequest(BaseModel):
    message: str
    user_id: str = "tony"
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    user_address: Optional[str] = None
    mode: Optional[str] = "hindsight"

class ClearMemoryRequest(BaseModel):
    user_id: str = "tony"

@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "gemini_model": gemini.model,
        "gemini_connected": bool(gemini.api_key),
        "hindsight_bank": hindsight.bank_id,
        "hindsight_connected": bool(hindsight.api_key)
    }

class CreateUserRequest(BaseModel):
    name: str
    phone: Optional[str] = "+1 (555) 019-9000"
    address: Optional[str] = None
    plan: Optional[str] = "Standard Customer Account"

@app.get("/api/users")
def get_users():
    users = load_all_users()
    return {
        "users": {u["id"]: u for u in users},
        "list": users
    }

@app.post("/api/users")
def create_user(req: CreateUserRequest):
    users = load_all_users()
    uid = req.name.strip().lower().replace(" ", "_")
    existing = next((u for u in users if u["id"] == uid), None)
    if existing:
        return {"status": "exists", "user": existing, "users": {u["id"]: u for u in users}}

    addr = req.address.strip() if req.address and req.address.strip() else "Not provided yet"
    new_user = {
        "id": uid,
        "name": req.name.strip(),
        "phone": req.phone.strip() if req.phone else "+1 (555) 019-9000",
        "address": addr,
        "role": "New Customer",
        "plan": req.plan or "Standard Customer Account",
        "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={uid}",
        "sentiment": "Neutral",
        "temperament": "Curious, Open",
        "volatility_score": 25,
        "recommended_specialist": "emily_smb",
        "orders": [],
        "total_tickets": 0,
        "preloaded_memories": [
            f"New customer registered: {req.name}. Phone: {req.phone}."
        ]
    }
    users.append(new_user)
    customers_file = os.path.join(DATA_DIR, "customers.json")
    with open(customers_file, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

    hindsight.retain(
        tag=uid,
        content=f"Customer Profile Registered: {new_user['name']} (ID: {uid}). Phone: {new_user['phone']}. Address: {new_user['address']}.",
        context="customer_profile"
    )
    return {"status": "created", "user": new_user, "users": {u["id"]: u for u in users}}

@app.get("/api/users/{user_id}")
def get_user_profile(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    telemetry = action_engine.get_telemetry(user_id)
    return {
        "user": user,
        "telemetry": telemetry
    }

def get_customer_return_order(customer: Dict[str, Any], user_msg: str = "") -> Dict[str, Any]:
    orders = customer.get("orders", [])
    if not orders:
        return {"id": "ORD-1180", "item": "High-Value Asset", "price": 1000.00}
    
    msg_l = (user_msg or "").lower()
    for o in orders:
        item_words = o.get("item", "").lower().split()
        if any(w in msg_l for w in item_words if len(w) > 3):
            raw_p = str(o.get("price", "1000")).replace("$", "").replace(",", "")
            try:
                p_val = float(raw_p)
            except Exception:
                p_val = 1000.0
            return {"id": o.get("id"), "item": o.get("item"), "price": p_val}

    def _get_price(o):
        try:
            return float(str(o.get("price", "0")).replace("$", "").replace(",", ""))
        except:
            return 0.0

    physical_orders = [o for o in orders if "suite" not in o.get("item", "").lower() and "contract" not in o.get("item", "").lower()]
    pool = physical_orders if physical_orders else orders
    target = max(pool, key=_get_price)
    raw_p = str(target.get("price", "1000")).replace("$", "").replace(",", "")
    try:
        p_val = float(raw_p)
    except Exception:
        p_val = 1000.0
    return {"id": target.get("id"), "item": target.get("item"), "price": p_val}

class ActionExecutionRequest(BaseModel):
    user_id: str
    action_type: str
    order_id: Optional[str] = None
    item_name: Optional[str] = None
    offer_choice: Optional[str] = "option_a"
    tracking_id: Optional[str] = "TRK-FDX-99420"

@app.post("/api/action/execute")
def execute_direct_action(req: ActionExecutionRequest):
    customer = get_user_by_id(req.user_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    action_type = req.action_type.upper()
    result = None

    return_order = get_customer_return_order(customer, req.item_name or "")
    order_id = req.order_id if (req.order_id and req.order_id != "ORD-1180") else return_order["id"]
    item_name = req.item_name if (req.item_name and "MacBook" not in req.item_name) else return_order["item"]
    item_price = return_order["price"]

    if "RMA" in action_type or "LABEL" in action_type:
        result = action_engine.generate_rma_label(
            customer=customer,
            order_id=order_id,
            item_name=item_name
        )
    elif "COUNTER_OFFER" in action_type or "TRADE_IN" in action_type or "CREDIT" in action_type:
        result = action_engine.execute_counter_offer(
            customer=customer,
            order_id=order_id,
            offer_choice=req.offer_choice or "option_a",
            base_item_price=item_price
        )
    elif "REROUTE" in action_type or "LOCKER" in action_type:
        result = action_engine.reroute_carrier_shipment(
            customer=customer,
            tracking_id=req.tracking_id or "TRK-FDX-99420",
            destination_choice="secure_locker"
        )
    elif "DEVOPS" in action_type or "HEAL" in action_type or "KAFKA" in action_type:
        result = action_engine.execute_devops_self_heal(
            customer=customer,
            component="kafka_queue"
        )

    ticket = None
    if result:
        ticket = action_engine.generate_crm_ticket(
            customer=customer,
            user_message=f"Action: {result.get('display_name')}",
            action_result=result,
            routing_dossier={"assigned_specialist": {"name": "David Sterling" if "Executive" in customer.get("temperament", "") else "Autonomous Action Engine"}}
        )
        hindsight.retain(
            tag=req.user_id,
            content=f"PAST TICKET #{ticket['ticket_id']} ({ticket['status_label']}): {ticket['resolution_summary']}",
            context="ticket_lifecycle"
        )

    return {
        "status": "success",
        "action_result": result,
        "wallet_balance": action_engine.get_customer_wallet(req.user_id),
        "ticket": ticket,
        "total_tickets": ticket.get("total_tickets", 5) if ticket else 5
    }

@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    user_id = req.user_id or "tony"
    customer = get_user_by_id(user_id, name=req.user_name, phone=req.user_phone, address=req.user_address)
    mode = (req.mode or "hindsight").lower()

    if mode == "legacy":
        # Standard Chatbot Mode: zero memory recall, no routing, no actions
        reply_text = gemini.generate_response(
            customer=customer,
            user_message=user_msg,
            recalled_memories=[],
            action_result=None,
            routing_dossier=None,
            mode="legacy"
        )
        return {
            "reply": reply_text,
            "recalled_memories": [],
            "action_result": None,
            "routing_dossier": None,
            "behavioral_routing": None,
            "matched_specialist": None,
            "is_voice_call_request": False,
            "user_phone": customer.get("phone"),
            "user_name": customer.get("name"),
            "wallet_balance": action_engine.get_customer_wallet(user_id),
            "logs_inspected": [],
            "user_query": user_msg,
            "mode": "legacy"
        }

    # 1. Recall existing memories from Hindsight Cloud
    recalled_memories = hindsight.recall(tag=user_id, query=user_msg)

    # 2. Behavioral routing & specialist evaluation
    routing_dossier = behavior_router.evaluate_routing(customer, user_msg, recalled_memories)

    # 3. Check for Autonomous Interactive Actions
    action_result = None
    msg_l = user_msg.lower()

    return_order = get_customer_return_order(customer, user_msg)
    order_id = return_order["id"]
    item_name = return_order["item"]
    item_price = return_order["price"]

    if any(k in msg_l for k in ["option a", "option 1", "70%", "trade in", "accept trade", "take credit"]):
        action_result = action_engine.execute_counter_offer(customer, order_id, "option_a", item_price)
    elif any(k in msg_l for k in ["option b", "option 2", "warranty extension", "keep item", "care plan"]):
        action_result = action_engine.execute_counter_offer(customer, order_id, "option_b", item_price)
    elif any(k in msg_l for k in ["give me label", "send label", "generate rma", "print label", "rma label", "ship it back", "option c"]):
        action_result = action_engine.generate_rma_label(customer, order_id, item_name)
    elif any(k in msg_l for k in ["reroute", "deliver to locker", "secure locker", "pickup locker"]):
        action_result = action_engine.reroute_carrier_shipment(customer, "TRK-FDX-882190", "secure_locker")
    elif any(k in msg_l for k in ["flush redis", "reset kafka", "heal cluster", "fix 500 loop"]):
        action_result = action_engine.execute_devops_self_heal(customer, "kafka_queue")
    else:
        # Fallback to existing Bay 4 return scan action (Tony)
        action_result = action_engine.execute_autonomous_fix(customer, user_msg)

    if action_result and action_result.get("status") in ["RESOLVED_AUTONOMOUSLY", "COMPLETED"]:
        resolution_record = (
            f"Autonomously executed {action_result.get('display_name')} for {customer.get('name')}: "
            f"{action_result.get('execution_output')}"
        )
        hindsight.retain(
            tag=user_id,
            content=resolution_record,
            context="autonomous_resolution"
        )

    # 4. Check if user asked for a voice call
    voice_call_keywords = ["call", "phone", "voice", "speak to human", "talk to someone", "human agent", "talk to human", "agent call", "ring"]
    is_voice_call = any(kw in user_msg.lower() for kw in voice_call_keywords)

    # 5. Generate response with Gemini 2.5 Flash
    reply_text = gemini.generate_response(
        customer=customer,
        user_message=user_msg,
        recalled_memories=recalled_memories,
        action_result=action_result,
        routing_dossier=routing_dossier,
        mode="hindsight"
    )

    # 6. Retain user's message in Hindsight
    hindsight.retain(
        tag=user_id,
        content=f"{customer.get('name')} said: {user_msg}",
        context="conversation_history"
    )

    # 7. Official CRM Ticket Generation & Hindsight Audit
    crm_ticket = action_engine.generate_crm_ticket(
        customer=customer,
        user_message=user_msg,
        action_result=action_result,
        routing_dossier=routing_dossier
    )

    ticket_record_memory = (
        f"PAST TICKET #{crm_ticket['ticket_id']} ({crm_ticket['status_label']}): "
        f"{crm_ticket['resolution_summary']} [Matched Specialist: {crm_ticket['assigned_specialist']}]"
    )
    hindsight.retain(
        tag=user_id,
        content=ticket_record_memory,
        context="ticket_lifecycle"
    )

    wallet_bal = action_engine.get_customer_wallet(user_id)

    return {
        "reply": reply_text,
        "recalled_memories": recalled_memories,
        "action_result": action_result,
        "routing_dossier": routing_dossier,
        "behavioral_routing": routing_dossier,
        "matched_specialist": routing_dossier.get("matched_specialist"),
        "is_voice_call_request": is_voice_call,
        "user_phone": customer.get("phone"),
        "user_name": customer.get("name"),
        "wallet_balance": wallet_bal,
        "ticket": crm_ticket,
        "total_tickets": crm_ticket.get("total_tickets", 5),
        "logs_inspected": action_result.get("logs_inspected") if action_result else (action_engine.get_telemetry(user_id) or {}).get("logs", []),
        "user_query": user_msg
    }

@app.post("/api/clear_memory")
def clear_memory(req: ClearMemoryRequest):
    user = get_user_by_id(req.user_id)
    if user:
        action_engine.clear_user_history(req.user_id)
        hindsight.seed_customer_memories([user])
    return {"status": "success", "message": f"Memory refreshed for {user.get('name')}."}

# Serve static frontend files
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
