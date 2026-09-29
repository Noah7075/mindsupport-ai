import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HINDSIGHT_API_KEY")
api_url = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io").rstrip("/")

resp = requests.get(f"{api_url}/openapi.json")
data = resp.json()

recall_op = data["paths"]["/v1/default/banks/{bank_id}/memories/recall"]["post"]
print("Recall requestBody:", json.dumps(recall_op.get("requestBody"), indent=2))
components = data.get("components", {}).get("schemas", {})
print("\nRecallRequest schema:", json.dumps(components.get("RecallRequest"), indent=2))
