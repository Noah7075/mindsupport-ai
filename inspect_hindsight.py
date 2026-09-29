import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
hindsight_key = os.getenv("HINDSIGHT_API_KEY")
hindsight_url = os.getenv("HINDSIGHT_API_URL").rstrip("/")

headers = {
    "Authorization": f"Bearer {hindsight_key}",
    "Content-Type": "application/json"
}

resp = requests.get(f"{hindsight_url}/openapi.json")
data = resp.json()

print("Hindsight Cloud Endpoints:")
for path in sorted(data.get("paths", {}).keys()):
    methods = list(data["paths"][path].keys())
    print(f"  {path} : {methods}")
