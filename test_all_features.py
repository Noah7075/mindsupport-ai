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

def get_json(path):
    with urllib.request.urlopen(f"{BASE_URL}{path}") as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_tests():
    print("\n--- 1. Testing GET /api/users ---")
    users = get_json("/api/users")
    print(f"Loaded {len(users.get('users', {}))} users:")
    for uid, u in users.get("users", {}).items():
        print(f"  • {u['name']} | Phone: {u['phone']} | {u['plan']} | {len(u.get('orders', []))} orders | {u.get('total_tickets', 5)} resolved tickets")

    print("\n--- 2. Testing Sarah: Voice Call Request (Behavioral Routing + Phone Confirmation) ---")
    sarah_res = post_json("/api/chat", {
        "user_id": "sarah",
        "message": "I'm stressed and frustrated about my missing package. Can someone call my phone right now?"
    })
    print("Sarah Reply:", sarah_res.get("reply")[:250], "...")
    print("Is Voice Call Request:", sarah_res.get("is_voice_call_request"))
    print("Matched Specialist:", sarah_res.get("matched_specialist", {}).get("name"))
    print("Routing Rationale:", sarah_res.get("behavioral_routing", {}).get("routing_rationale"))

    print("\n--- 3. Testing Unknown Question Fallback (Marcus Chen) ---")
    marcus_res = post_json("/api/chat", {
        "user_id": "marcus",
        "message": "What is the secret recipe for sourdough bread made by monks in 1450?"
    })
    print("Marcus Reply:", marcus_res.get("reply")[:250], "...")
    print("Recalled memories count:", len(marcus_res.get("recalled_memories", [])))

    print("\n--- 4. Testing Tony Stark: Gold Earrings Refund Issue (Log Diagnostic + Action Engine) ---")
    tony_res = post_json("/api/chat", {
        "user_id": "tony",
        "message": "Why hasn't my 18k gold earrings refund reached my account yet? I returned it last week."
    })
    print("Tony Reply:", tony_res.get("reply")[:250], "...")
    print("Action Result Status:", tony_res.get("action_result", {}).get("status"))
    print("Logs Inspected:", len(tony_res.get("logs_inspected", [])))

    print("\n=== ALL TEST CHECKS COMPLETED ===")

if __name__ == "__main__":
    time.sleep(1)
    run_tests()
