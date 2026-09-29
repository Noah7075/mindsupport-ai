import requests
import json
import os

resp = requests.get("https://api.hindsight.vectorize.io/openapi.json")
data = resp.json()

schemas = data.get("components", {}).get("schemas", {})
print("RetainRequest:", json.dumps(schemas.get("RetainRequest", {}), indent=2))
print("\nRecallRequest:", json.dumps(schemas.get("RecallRequest", {}), indent=2))
