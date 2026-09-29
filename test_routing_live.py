import requests

# Test hostile message with Alex Vance
resp = requests.post("http://127.0.0.1:8000/api/chat", json={
    "customer_id": "alex_admin",
    "message": "Your system is completely broken again! Fix this right now or I am canceling our $60k contract!",
    "mode": "hindsight"
})

print("Alex Status:", resp.status_code)
data = resp.json()
print("Escalation Level:", data.get("routing_dossier", {}).get("escalation_level"))
print("Assigned Specialist:", data.get("routing_dossier", {}).get("assigned_specialist", {}).get("name"))
print("Reply Preview:\n", data.get("reply", "")[:250])
