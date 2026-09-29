import json
import os
from dotenv import load_dotenv

load_dotenv()

from backend.hindsight_client import HindsightMemoryManager

hindsight = HindsightMemoryManager()

with open("data/customers.json", "r", encoding="utf-8") as f:
    users = json.load(f)

print(f"Seeding memories for all {len(users)} users into Hindsight Cloud...")

total_seeded = 0
for u in users:
    print(f" -> Seeding {u['name']} ({len(u['preloaded_memories'])} memories)...")
    for m in u['preloaded_memories']:
        hindsight.retain(tag=u['id'], content=m, context="user_history")
        total_seeded += 1

print(f"\nAll {total_seeded} memories seeded successfully!")
