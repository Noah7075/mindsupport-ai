import requests

resp = requests.post("http://127.0.0.1:8000/api/chat", json={
    "message": "Hi, I returned the Diamond Hoop Earrings last week and tracking shows the warehouse received them 3 days ago, but my refund hasn't arrived yet. Could you check what happened?",
    "user_id": "tony"
})

print("Status:", resp.status_code)
data = resp.json()
print("\nAgent Response to Tony:\n", data.get("reply"))
print("\nRecalled Memories Count:", len(data.get("recalled_memories", [])))
print("Logs Inspected Count:", len(data.get("logs_inspected", [])))
