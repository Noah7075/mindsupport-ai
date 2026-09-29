import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def chat(user_id, message, user_name=None, user_phone=None):
    req = urllib.request.Request(
        f"{BASE_URL}/api/chat",
        data=json.dumps({
            "user_id": user_id,
            "message": message,
            "user_name": user_name,
            "user_phone": user_phone
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("\n--- TURN 1: Brand New User Chats (Thanuj Kumar) ---")
res1 = chat(
    user_id="thanuj_kumar",
    message="Hi, I am Thanuj Kumar. My phone number is +1 (415) 888-1234. I run an AI research lab and we recently ordered a Quantum H100 GPU Cluster.",
    user_name="Thanuj Kumar",
    user_phone="+1 (415) 888-1234"
)
print("Agent Reply 1:\n", res1["reply"])
print("Recalled memories before turn:", len(res1.get("recalled_memories", [])))

time.sleep(3)

print("\n--- TURN 2: Asking the Agent to Recall from Hindsight Memory ---")
res2 = chat(
    user_id="thanuj_kumar",
    message="Can you remind me what cluster I ordered and what phone number you have on file for me?"
)
print("Agent Reply 2:\n", res2["reply"])
print("Recalled memories after turn 1:", len(res2.get("recalled_memories", [])))
print("Matched Specialist:", res2.get("matched_specialist", {}).get("name"))
