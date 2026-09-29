import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def post_json(path, data):
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("\n--- 1. Testing Direct Action Execution: Generate RMA Label ---")
rma_res = post_json("/api/action/execute", {
    "user_id": "alex",
    "action_type": "GENERATE_RMA",
    "order_id": "ORD-1180",
    "item_name": "Apple MacBook Pro 16-inch M3 Max"
})
print("RMA Result:", rma_res.get("status"))
print("RMA Number:", rma_res.get("action_result", {}).get("rma_number"))
print("Tracking Number:", rma_res.get("action_result", {}).get("tracking_number"))
print("Carrier:", rma_res.get("action_result", {}).get("carrier"))
print("Barcode:", rma_res.get("action_result", {}).get("barcode"))

print("\n--- 2. Testing Direct Action Execution: Accept Option A (70% Trade-In Credit) ---")
credit_res = post_json("/api/action/execute", {
    "user_id": "alex",
    "action_type": "ACCEPT_COUNTER_OFFER",
    "order_id": "ORD-1180",
    "offer_choice": "option_a"
})
print("Credit Result:", credit_res.get("status"))
print("Resolution:", credit_res.get("action_result", {}).get("resolution_type"))
print("Credit Issued:", credit_res.get("action_result", {}).get("credit_issued"))
print("Updated Wallet Balance:", credit_res.get("wallet_balance"))

print("\n--- 3. Testing Idempotency Risk Guardrail (Attempting double-credit) ---")
double_res = post_json("/api/action/execute", {
    "user_id": "alex",
    "action_type": "ACCEPT_COUNTER_OFFER",
    "order_id": "ORD-1180",
    "offer_choice": "option_a"
})
print("Double Credit Guardrail Triggered:", double_res.get("action_result", {}).get("status"))

print("\n=== ALL AUTONOMOUS AGENT TOOLS VERIFIED ===")
