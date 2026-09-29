import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HINDSIGHT_API_KEY")
api_url = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io").rstrip("/")

headers = {
    "Authorization": f"Bearer {api_key}",
    "x-api-key": api_key,
    "Content-Type": "application/json"
}

resp = requests.get(f"{api_url}/openapi.json")
data = resp.json()

paths = data.get("paths", {})
for p in ["/v1/default/banks/{bank_id}/memories/recall", "/v1/default/banks/{bank_id}/memories", "/v1/default/banks", "/v1/default/banks/{bank_id}/documents"]:
    if p in paths:
        print(f"\n--- {p} ---")
        print(json.dumps(paths[p], indent=2)[:1000])
