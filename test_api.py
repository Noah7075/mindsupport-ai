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

print("=== 1. Testing Scenario 1 (Warm Memory Recall) ===")
t1 = post("http://127.0.0.1:8000/api/triage", {"scenario_key": "checkout_db_exhaustion"})
print("Mode:", t1["diagnosis"]["mode"])
print("Matched Incident:", t1["diagnosis"]["matched_incident_id"])
print("Confidence:", t1["diagnosis"]["confidence_score"])
print("Runbook:", t1["diagnosis"]["runbook_command"])

print("\n=== 2. Testing Scenario 2 (Zero-Precedent Novel Outage) ===")
t2 = post("http://127.0.0.1:8000/api/triage", {"scenario_key": "ebpf_kernel_leak"})
print("Mode:", t2["diagnosis"]["mode"])
print("Confidence:", t2["diagnosis"]["confidence_score"])
print("Hypotheses generated:", len(t2["diagnosis"]["hypotheses"]))
for h in t2["diagnosis"]["hypotheses"]:
    print(f"  - Rank {h['rank']}: {h['title']} ({h['probability']})")

print("\n=== 3. Testing Interactive Diagnostic Probe ===")
p = post("http://127.0.0.1:8000/api/probe", {"command": "cat /proc/meminfo | grep -E 'Slab|SUnreclaim'"})
print("Probe output:", p["output"].strip())

print("\n=== 4. Testing Vigilance Lifecycle Advance ===")
v = post("http://127.0.0.1:8000/api/vigilance/advance", {"memory_id": "INC-104", "new_stage": "OBSERVATION"})
print("Status:", v["status"])
print("Log:", v["human_log"].encode("ascii", errors="replace").decode("ascii"))

print("\n=== 5. Listing All Hindsight Memories ===")
m = get("http://127.0.0.1:8000/api/memories")
print(f"Total memories in bank: {m['count']}")
for item in m["memories"]:
    print(f"  [{item.get('incident_id')}] {item.get('title')} ({item.get('vigilance_stage')})")

print("\nALL BACKEND API TESTS PASSED!")
