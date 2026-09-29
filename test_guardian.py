import urllib.request
import json

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("=== 1. Testing Overnight Simulation (Known Issue: Auto-Fix) ===")
o1 = post("http://127.0.0.1:8000/api/overnight", {"scenario_type": "known_issue"})
print("Decision:", o1["autonomy_decision"])
print("Confidence:", o1["confidence_score"])
print("Matched Memory:", o1["matched_memory_id"])
print("Summary:", o1["developer_summary"][:80], "...")

print("\n=== 2. Testing Overnight Simulation (Novel Issue: Containment) ===")
o2 = post("http://127.0.0.1:8000/api/overnight", {"scenario_type": "novel_issue"})
print("Decision:", o2["autonomy_decision"])
print("Confidence:", o2["confidence_score"])
print("Summary:", o2["developer_summary"][:80], "...")

print("\n=== 3. Testing Interactive Chat ===")
c1 = post("http://127.0.0.1:8000/api/chat", {"message": "Why shouldn't I restart checkout pods?"})
print("Chat Reply:", c1["reply"])

print("\n=== 4. Testing Teaching New Rule to Hindsight ===")
t1 = post("http://127.0.0.1:8000/api/teach", {
    "rule_text": "Never drop database tables during migrations without taking a snapshot.",
    "category": "Database Policy"
})
print("Teach Status:", t1["status"])
print("Saved Message:", t1["message"])

print("\n=== 5. Verifying Memories in Bank ===")
m = get("http://127.0.0.1:8000/api/memories")
print(f"Total memories in Hindsight: {m['count']}")
for item in m["memories"]:
    print(f"  [{item.get('incident_id')}] {item.get('title')}")

print("\nALL GUARDIAN ENDPOINTS WORKING FLAWLESSLY!")
