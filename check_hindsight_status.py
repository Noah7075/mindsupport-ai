import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HINDSIGHT_API_KEY")
api_url = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io").rstrip("/")

headers = {
    "Authorization": f"Bearer {api_key}",
    "x-api-key": api_key,
    "Content-Type": "application/json"
}

print(f"Connecting to Hindsight at {api_url}...")

# 1. List or create bank
# Check bank endpoints
resp = requests.get(f"{api_url}/v1/default/banks", headers=headers)
print("GET /v1/default/banks:", resp.status_code, resp.text[:300])

# 2. Check memories for all 5 tags in customer_support_bank
tags = ["tony", "sarah", "alex", "marcus", "elena"]
for tag in tags:
    recall_resp = requests.post(
        f"{api_url}/v1/default/banks/customer_support_bank/memories/recall",
        headers=headers,
        json={"query": "tickets orders profile phone address", "tags": [tag], "limit": 10}
    )
    if recall_resp.status_code == 200:
        memories = recall_resp.json().get("memories", [])
        print(f"Tag '{tag}': {len(memories)} memories in customer_support_bank")
        for m in memories[:2]:
            print(f"   - {m.get('content', '')[:100]}...")
    else:
        print(f"Tag '{tag}' recall status: {recall_resp.status_code}")
