import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
hindsight_key = os.getenv("HINDSIGHT_API_KEY")
hindsight_url = os.getenv("HINDSIGHT_API_URL").rstrip("/")
bank_id = os.getenv("HINDSIGHT_BANK_ID", "customer_support_bank")

headers = {
    "Authorization": f"Bearer {hindsight_key}",
    "Content-Type": "application/json"
}

# 1. Test Retain
retain_payload = {
    "items": [
        {
            "content": "Alex is an Enterprise Admin using Safari on macOS. He experienced OAuth 401 token expiration errors in Redis node 3.",
            "context": "ticket_history",
            "tags": ["alex_admin"]
        }
    ]
}

url_retain = f"{hindsight_url}/v1/default/banks/{bank_id}/memories"
resp = requests.post(url_retain, headers=headers, json=retain_payload)
print("Retain Status:", resp.status_code)
print("Retain Response:", resp.text)

# 2. Test Recall
recall_payload = {
    "query": "What errors did Alex face?",
    "tags": ["alex_admin"]
}
url_recall = f"{hindsight_url}/v1/default/banks/{bank_id}/memories/recall"
resp = requests.post(url_recall, headers=headers, json=recall_payload)
print("\nRecall Status:", resp.status_code)
print("Recall Response:", resp.text)
