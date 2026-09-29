import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from backend.hindsight_client import HindsightMemoryManager
from backend.action_engine import ActionEngine
from backend.gemini_client import GeminiSupportAgent

print("Initializing components...")
hindsight = HindsightMemoryManager()
gemini = GeminiSupportAgent()
action_engine = ActionEngine()

with open("data/customers.json", "r", encoding="utf-8") as f:
    customers = json.load(f)

print(f"Loaded {len(customers)} customer profiles.")
res = hindsight.seed_customer_memories(customers)
print("Seed Result:", res)

# Test chat with Alex
alex = customers[0]
print("\n--- Testing Chat with Alex (Hindsight Mode) ---")
memories = hindsight.recall(tag=alex["id"], query="authentication failure")
print(f"Recalled {len(memories)} memories for Alex.")
action = action_engine.execute_autonomous_fix(alex, "My authentication is broken again.")
print("Action Result:", action.get("display_name") if action else "None")

reply = gemini.generate_response(alex, "My authentication is broken again.", memories, action, mode="hindsight")
print("\nGemini Response:\n", reply)
