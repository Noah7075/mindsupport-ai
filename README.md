# WorkEase Guardian — Night-Shift SRE Co-Pilot Powered by Hindsight

> Built for the **"AI Agents That Learn Using Hindsight"** Hackathon.  
> Solving the solo developer's nightmare: *Production crashes while you sleep, but letting an AI blindly run scripts is too risky.*

---

## 💡 The Human Problem We Are Solving

As a solo developer or small startup founder building **WorkEase**:
1. **You Can't Stay Awake 24/7:** When WorkEase crashes at 2:00 AM, you only find out when you wake up to angry user emails.
2. **The "Big Risk" of Autonomous AI:** Giving an AI full permission to run arbitrary scripts on production is dangerous. A naive chatbot might run dangerous commands, drop databases, or make cascading outages worse.
3. **Stateless AI Fails:** Standard chatbots have total amnesia—they forget past outages and make the exact same mistakes over and over.

---

## 🛡️ The Solution: Memory-Gated Autonomy

WorkEase Guardian uses **Hindsight persistent memory** as a literal **Autonomy Safety Gate**:

| Scenario | Hindsight Memory Confidence | Action Taken While You Sleep |
| :--- | :---: | :--- |
| **Known Bug** (e.g. Stripe checkout lock deadlock) | **High (90%+)** | **Safe Autonomous Fix:** Applies the verified, non-destructive playbook in 20 seconds, confirms recovery, and writes an overnight briefing for your morning coffee. |
| **Novel / Brand New Bug** (e.g. unknown schema deadlock) | **0% (Zero Precedent)** | **Safe Containment Only:** Blocks unverified mutations to protect your database. Isolates failing queues, keeps the user portal alive, and alerts you. |

---

## 🚀 Key Features

1. **Morning Debrief Stream (The Natural Chat Interface):**
   - Wake up and see a clean, clear timeline of what happened overnight while you slept.
   - Interactive chat where you can ask questions: *"Why didn't you restart the pods?", "What are our safe playbooks?"*
2. **"Why a Dumb AI Would Fail" Comparison:**
   - Highlights why a stateless LLM (which suggests blind server reboots) would have made the outage worse.
3. **Hindsight Memory Bank Sidebar:**
   - **Verified Safe Playbooks:** Runbooks allowed to run autonomously.
   - **Mistakes to Avoid (Negative Memory):** Past anti-patterns (e.g., *"Never blind-restart checkout pods: leaves orphaned locks in Redis"*).
   - **System Policies:** Active architectural rules configured by the developer.
4. **Interactive Rule Learning:**
   - Click `+ Teach Rule` or type `remember: [rule]` in chat to dynamically inject new institutional knowledge into Hindsight.

---

## ⚡ 60-Second Demo Story for Judges

1. Open **`http://127.0.0.1:8000/`**.
2. **Step 1 — Show the Overnight Safe Auto-Fix:**
   - Click **`2:14 AM Crash (Known Bug - Safe Auto-Fix)`**.
   - Show the clean debrief card: Hindsight matched INC-104 with 94% confidence, safely flushed the Redis lock, and restored WorkEase in 18 seconds while you slept.
3. **Step 2 — Show the "Big Risk" Solved (Safe Containment):**
   - Click **`3:30 AM Crash (Novel Bug - Safe Containment)`**.
   - Show how the agent detects **0% historical precedent**, refuses to guess or corrupt the database, and safely isolates the issue.
4. **Step 3 — Interactive Chat & Memory Recall:**
   - Click the prompt chip: **`Why not restart pods?`**.
   - Watch the agent answer using its memory: citing that pod restarts caused orphaned locks in past incidents.
5. **Step 4 — Teach the Agent Live:**
   - Click **`+ Teach Rule`** and add a rule like: *"Always cap DB pool to 100"*.
   - Watch it instantly appear in the Hindsight Memory Bank sidebar!
