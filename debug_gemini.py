import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

from backend.hindsight_client import HindsightMemoryManager
from backend.action_engine import ActionEngine
from backend.gemini_client import GeminiSupportAgent

hindsight = HindsightMemoryManager()
gemini = GeminiSupportAgent()
action_engine = ActionEngine()

with open("data/customers.json", "r", encoding="utf-8") as f:
    customers = json.load(f)

customer = customers[0]
user_msg = "Hi, I returned the Diamond Hoop Earrings last week and tracking shows the warehouse received them 3 days ago, but my refund hasn't arrived yet. Could you check what happened?"

recalled_memories = hindsight.recall(tag="tony", query=user_msg)
action_result = action_engine.execute_autonomous_fix(customer, user_msg)

# Call Gemini with verbose response printing
customer_name = "Tony"
memories_formatted = ""
for i, m in enumerate(recalled_memories, 1):
    memories_formatted += f"  [{i}] {m.get('text')}\n"

action_context = ""
if action_result:
    action_context = (
        f"\n[LIVE SYSTEM LOGS & ACTIONS INSPECTED BY AGENT]:\n"
        f"Diagnostic Root-Cause: {action_result.get('diagnostic')}\n"
        f"Action Executed: {action_result.get('display_name')}\n"
        f"Result: {action_result.get('execution_output')}\n"
        f"Status: Refund issue autonomously fixed.\n"
    )

system_instruction = (
    f"You are MindSupport AI, an intelligent customer support copilot for a premium retail store.\n"
    f"You are speaking with {customer_name}, a valued, mature, calm, and loyal customer.\n\n"
    f"--- RECALLED HINDSIGHT MEMORIES (Past Tickets & Profile) ---\n"
    f"{memories_formatted if memories_formatted else 'No prior memories found.'}\n"
    f"{action_context}\n"
    f"GUIDELINES:\n"
    f"1. Greet Tony in a warm, mature, calm, and respectful tone.\n"
    f"2. If Tony is asking about his return or refund (Diamond Hoop Earrings, Order #ORD-77492, Tracking TRK-882190):\n"
    f"   - Confirm the warehouse received the return at Bay 4 and approved the condition.\n"
    f"   - Explain transparently that the automated refund stalled because the original purchase card (Visa *4102) expired.\n"
    f"   - State clearly that you have autonomously bypassed the bottleneck and re-routed the full $240.00 refund to his active Mastercard (*8891) (Reference: RF-99420-STRIPE).\n"
    f"   - Provide the timeline for the bank credit (typically 1-2 business days).\n"
    f"3. If Tony asks about past tickets (like the PS5 missing controller in Ticket #101), reference the exact historical resolution from memory accurately.\n"
    f"4. Keep the response articulate, transparent, helpful, and complete. Avoid robotic corporate jargon."
)

payload = {
    "system_instruction": {
        "parts": [{"text": system_instruction}]
    },
    "contents": [
        {
            "role": "user",
            "parts": [{"text": f"Tony: \"{user_msg}\""}]
        }
    ],
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 2048
    }
}

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini.api_key}"
resp = requests.post(url, json=payload, timeout=20)
print("Status:", resp.status_code)
data = resp.json()
print(json.dumps(data, indent=2))
