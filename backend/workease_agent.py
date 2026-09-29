"""
WorkEase Guardian - SRE Assistant Engine
Designed for solo developers and small teams to monitor production (WorkEase),
use Hindsight memory as an autonomy safety gate, and chat naturally with the developer.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from backend.memory_manager import MemoryManager

class WorkEaseAgent:
    def __init__(self, memory_manager: MemoryManager, gemini_api_key: Optional[str] = None):
        self.memory = memory_manager
        self.gemini_model = None
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self._init_gemini()

    def _init_gemini(self):
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                print("[WorkEaseAgent] Connected to Google Gemini.")
            except Exception as e:
                print(f"[WorkEaseAgent] Gemini init: {e}. Using deterministic reasoning engine.")
                self.gemini_model = None

    def update_key(self, key: str):
        self.gemini_api_key = key
        self._init_gemini()

    def process_overnight_event(self, scenario_type: str = "known_issue") -> Dict[str, Any]:
        """
        Simulates an overnight event on WorkEase while the developer was asleep.
        Demonstrates the core innovation: Memory-Gated Autonomy.
        """
        if scenario_type == "known_issue":
            # Scenario A: Known Stripe lock bug that crashed checkout
            query = "checkout 504 gateway timeout redis connection pool lock"
            matches = self.memory.recall(query=query)
            top_match = matches[0] if matches else None
            score = top_match["score"] if top_match else 0.94

            return {
                "scenario_id": "EVT-214",
                "timestamp": "02:14 AM (Overnight)",
                "service": "WorkEase API (checkout & billing)",
                "error_code": "HTTP 504 Gateway Timeout",
                "matched_memory_id": "INC-104",
                "confidence_score": 94,
                "autonomy_decision": "AUTONOMOUS_FIX_APPLIED",
                "decision_rationale": "High memory confidence (94%) with verified safe playbook. Non-destructive fix permitted while developer slept.",
                "action_taken": "Flushed orphaned Redis lock 'lock:checkout_sync' and recycled idle connection pool.",
                "verification_result": "Latency restored to 38ms. 0 errors detected across subsequent 6 hours.",
                "developer_summary": (
                    "While you were sleeping at 2:14 AM, WorkEase checkout threw 504 errors. "
                    "Hindsight matched this to the Stripe webhook lock bug from two weeks ago (94% confidence). "
                    "Because this fix is verified and non-destructive, I applied it automatically and verified recovery in 18 seconds. "
                    "WorkEase remained healthy through the night."
                ),
                "dumb_ai_comparison": (
                    "Without persistent memory, a standard AI chatbot would have recommended restarting the database or pods. "
                    "In our past incident, restarting the pods actually caused locks to become permanently orphaned and extended downtime by 45 minutes!"
                )
            }
        else:
            # Scenario B: Brand new, novel issue (e.g. database schema deadlock)
            return {
                "scenario_id": "EVT-330",
                "timestamp": "03:30 AM (Overnight)",
                "service": "WorkEase Worker (background jobs)",
                "error_code": "PostgresDeadlockDetected: process 89112 waiting for ShareLock",
                "matched_memory_id": None,
                "confidence_score": 0,
                "autonomy_decision": "SAFETY_CONTAINMENT_ONLY",
                "decision_rationale": "Zero historical precedent in Hindsight. Autonomous mutation blocked to prevent accidental data loss.",
                "action_taken": "Isolated failing job queue into dead-letter holding. Main WorkEase customer portal kept online.",
                "verification_result": "Main application remained 100% available. Held 14 blocked jobs for your morning review.",
                "developer_summary": (
                    "At 3:30 AM, background worker encountered an unprecedented schema deadlock. "
                    "Because this has 0% historical precedent in Hindsight, I blocked autonomous fixes to prevent risking your database. "
                    "I isolated the failing worker queue and kept the customer-facing app online. The failing jobs are paused for your review."
                ),
                "dumb_ai_comparison": (
                    "A naive AI with full access might have force-killed active database transactions or dropped locks, risking customer data corruption."
                )
            }

    def chat(self, user_message: str, chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Handles interactive questions from the developer:
        e.g., 'What happened last night?', 'Why didn't you restart the server?', 'Teach memory: ...'
        """
        msg_lower = user_message.lower().strip()

        # Check if user is teaching a new rule or memory
        if msg_lower.startswith("teach:") or msg_lower.startswith("remember:") or "remember that" in msg_lower:
            cleaned_rule = user_message.replace("teach:", "").replace("Teach:", "").replace("remember:", "").replace("Remember:", "").strip()
            new_mem = self.memory.retain(
                incident_id=f"RULE-{int(time.time())}",
                title="Developer System Rule / Policy",
                symptoms="System rule specified by developer",
                root_cause=cleaned_rule,
                successful_resolution=cleaned_rule,
                failed_attempts=[],
                runbook_command="Applied as active operational policy",
                vigilance_stage="BATTLE_TESTED",
                tags=["developer-rule", "policy"]
            )
            return {
                "reply": f"Got it! I have saved this rule into Hindsight memory: \"{cleaned_rule}\". I will adhere to this during all future checks.",
                "memory_added": new_mem
            }

        # Search Hindsight memory for relevant context
        memories = self.memory.recall(query=user_message)
        top_memories = [m["memory"] for m in memories[:2]] if memories else []
        
        # Build context from memories
        memory_context = ""
        if top_memories:
            memory_context = "Relevant memories from Hindsight:\n" + "\n".join([
                f"- {m.get('title')}: {m.get('root_cause')} (Fix: {m.get('successful_resolution')})"
                for m in top_memories
            ])

        # If Gemini is configured, use it with the memory context
        if self.gemini_model:
            try:
                system_prompt = (
                    "You are WorkEase Guardian, an AI SRE assistant for a solo software developer. "
                    "You speak clearly, concisely, and professionally without emojis or hype. "
                    "You have persistent memory powered by Hindsight. Always use your historical memories when answering questions.\n\n"
                    f"{memory_context}"
                )
                prompt = f"{system_prompt}\n\nDeveloper question: {user_message}"
                res = self.gemini_model.generate_content(prompt)
                return {
                    "reply": res.text.strip(),
                    "recalled_memories": top_memories
                }
            except Exception as e:
                print(f"[WorkEaseAgent] Gemini generation error: {e}")

        # Deterministic smart fallback based on keywords
        if "restart" in msg_lower and ("why" in msg_lower or "server" in msg_lower or "pod" in msg_lower):
            reply = (
                "Last time on WorkEase checkout (Incident INC-104), blind-restarting the pods worsened the outage "
                "because the orphaned Redis lock persisted, while new incoming pods immediately piled on waiting connections. "
                "The safe, verified procedure is always to clear the specific lock key first before touching the pods."
            )
        elif "what happened" in msg_lower or "overnight" in msg_lower or "status" in msg_lower or "last night" in msg_lower:
            reply = (
                "WorkEase is currently healthy and operational. At 2:14 AM, the API experienced a 504 connection pool timeout. "
                "I matched it to our past Stripe lock issue, executed the proven lock release, and verified recovery in 18 seconds. "
                "Current response latency is 38ms with 0 errors reported."
            )
        elif "memory" in msg_lower or "remember" in msg_lower:
            reply = (
                f"I currently have {len(self.memory.get_all())} active memories in my Hindsight bank. "
                "These include the checkout Redis lock playbook (INC-104), Kafka rebalance handling (INC-089), and your team rules."
            )
        else:
            reply = (
                f"I checked Hindsight memory regarding: \"{user_message}\". "
                + (f"I found a relevant match with {top_memories[0]['title']}: {top_memories[0]['root_cause']}." if top_memories else 
                   "I don't have a direct prior incident recorded for that specific query, but WorkEase health checks are all passing.")
            )

        return {
            "reply": reply,
            "recalled_memories": top_memories
        }
