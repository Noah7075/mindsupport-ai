import requests

# 1. Test GET /
r_index = requests.get("http://127.0.0.1:8000/")
print("GET / Status:", r_index.status_code, "Length:", len(r_index.text))

# 2. Test GET /api/customers
r_cust = requests.get("http://127.0.0.1:8000/api/customers")
print("GET /api/customers Status:", r_cust.status_code, "Count:", len(r_cust.json()))

# 3. Test POST /api/chat with Alex (Hindsight mode)
r_chat = requests.post("http://127.0.0.1:8000/api/chat", json={
    "customer_id": "alex_admin",
    "message": "My authentication is broken again. Same error as last week.",
    "mode": "hindsight"
})
print("POST /api/chat Status:", r_chat.status_code)
chat_data = r_chat.json()
print("Recalled facts count:", len(chat_data.get("recalled_memories", [])))
print("Action triggered:", bool(chat_data.get("action_result")))
print("Reply preview:", chat_data.get("reply", "")[:200])

# 4. Test POST /api/chat with Sarah (Stateless mode comparison)
r_stateless = requests.post("http://127.0.0.1:8000/api/chat", json={
    "customer_id": "sarah_bakery",
    "message": "Payment is failing at checkout!",
    "mode": "stateless"
})
print("\nStateless Reply preview:", r_stateless.json().get("reply", "")[:200])
