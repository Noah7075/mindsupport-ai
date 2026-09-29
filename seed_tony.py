import os
import json
from dotenv import load_dotenv

load_dotenv()

from backend.hindsight_client import HindsightMemoryManager

hindsight = HindsightMemoryManager()

with open("data/customers.json", "r", encoding="utf-8") as f:
    customers = json.load(f)

tony = customers[0]
print(f"Seeding memories for {tony['name']} ({len(tony['preloaded_memories'])} facts)...")

res = hindsight.seed_customer_memories([tony])
print("Seed Result:", res)

# Test recall
recalled = hindsight.recall(tag="tony", query="PlayStation controller or refund")
print(f"\nRecalled {len(recalled)} memories:")
for r in recalled:
    print(" -", r.get("text"))
