import os
import requests
from dotenv import load_dotenv

load_dotenv()

hindsight_key = os.getenv("HINDSIGHT_API_KEY")
hindsight_url = os.getenv("HINDSIGHT_API_URL").rstrip("/")

headers = {
    "Authorization": f"Bearer {hindsight_key}",
    "x-api-key": hindsight_key,
    "Content-Type": "application/json"
}

bank_id = "customer_support_bank"

# Test POST and GET without /v1
routes = [
    ("GET", "/banks"),
    ("POST", f"/banks/{bank_id}"),
    ("POST", f"/banks/{bank_id}/memories"),
    ("POST", f"/banks/{bank_id}/retain"),
    ("POST", f"/banks/{bank_id}/recall"),
    ("POST", f"/banks/{bank_id}/reflect"),
    ("GET", f"/banks/{bank_id}/memories"),
    ("GET", "/docs"),
    ("GET", "/openapi.json")
]

for method, path in routes:
    try:
        url = f"{hindsight_url}{path}"
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=5)
        else:
            resp = requests.post(url, headers=headers, json={"contents": "test", "query": "test"}, timeout=5)
        print(f"{method} {path}: {resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        print(f"{method} {path} Exception:", e)
