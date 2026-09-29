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

# 1. Create a brand-new dedicated memory bank: mindsupport_master_bank
new_bank_id = "mindsupport_master_bank"
print(f"Creating / ensuring memory bank '{new_bank_id}'...")

bank_payload = {
    "bank_id": new_bank_id,
    "name": "MindSupport Master Production Bank",
    "mission": "Autonomous multi-user customer support copilot with behavioral dispatch and historical ticket resolution memory."
}

res = requests.put(f"{api_url}/v1/default/banks/{new_bank_id}", headers=headers, json=bank_payload)
print("PUT bank status:", res.status_code, res.text)

# 2. Load all 5 customers
with open("data/customers.json", "r", encoding="utf-8") as f:
    customers = json.load(f)

# 3. Seed every customer's profile, phone, address, orders, and 5 past resolved tickets into mindsupport_master_bank
all_items = []
for c in customers:
    cid = c["id"]
    name = c["name"]
    phone = c["phone"]
    addr = c["address"]
    plan = c["plan"]
    orders_str = ", ".join([f"{o['item']} ({o['price']} on {o['date']})" for o in c.get("orders", [])])
    
    # Core Profile Memory
    profile_text = f"Customer Profile: {name} (ID: {cid}). Phone: {phone}. Address: {addr}. Membership: {plan}. Order History: {orders_str}."
    all_items.append({
        "content": profile_text,
        "context": "customer_profile",
        "tags": [cid, "profile"]
    })
    
    # 5 Past Resolved Tickets
    for ticket_mem in c.get("preloaded_memories", []):
        all_items.append({
            "content": f"{name} Historical Ticket: {ticket_mem}",
            "context": "resolved_ticket_archive",
            "tags": [cid, "tickets", "resolved"]
        })

print(f"\nRetaining {len(all_items)} memory units to '{new_bank_id}' in batch...")
retain_res = requests.post(
    f"{api_url}/v1/default/banks/{new_bank_id}/memories",
    headers=headers,
    json={"items": all_items}
)
print("Retain status:", retain_res.status_code)
if retain_res.status_code in [200, 201]:
    print("Retain response:", retain_res.text[:300])

# 4. Test Recall from the new bank
print("\nTesting Recall from new bank...")
for c in customers:
    cid = c["id"]
    recall_res = requests.post(
        f"{api_url}/v1/default/banks/{new_bank_id}/memories/recall",
        headers=headers,
        json={
            "query": f"{c['name']} past tickets and orders",
            "tags": [cid],
            "tags_match": "any"
        }
    )
    print(f"Recall for {c['name']} (tag: '{cid}'): status={recall_res.status_code}")
    if recall_res.status_code == 200:
        rec_data = recall_res.json()
        results = rec_data.get("results", []) or rec_data.get("memories", [])
        print(f"   -> Recalled {len(results)} items!")
        for r in results[:2]:
            print(f"      * {r.get('content') or r.get('text')}")
