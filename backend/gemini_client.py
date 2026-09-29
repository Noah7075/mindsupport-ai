import os
import requests
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("gemini_client")

class GeminiSupportAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate_response(
        self,
        customer: Dict[str, Any],
        user_message: str,
        recalled_memories: List[Dict[str, Any]],
        action_result: Optional[Dict[str, Any]],
        routing_dossier: Optional[Dict[str, Any]] = None,
        mode: str = "hindsight"
    ) -> str:
        """
        Generates a customer support response using Google Gemini 2.5 Flash.
        Handles persistent memory, warehouse diagnostics, behavioral tone adaptation,
        and voice call dispatch with phone confirmation.
        """
        if not self.api_key:
            return "Error: GEMINI_API_KEY is not configured in .env file."

        customer_name = customer.get("name", "User")
        customer_phone = customer.get("phone", "+1 (555) 019-2834")
        customer_address = customer.get("address", "Registered Address")
        customer_temperament = customer.get("temperament", "Calm, Professional")
        orders_formatted = json.dumps(customer.get("orders", []), indent=2)

        # Format recalled Hindsight memories
        memories_formatted = ""
        for i, m in enumerate(recalled_memories, 1):
            memories_formatted += f"  [{i}] {m.get('text')}\n"

        # Format system action and diagnostic findings
        action_context = ""
        if action_result and action_result.get("status") == "RESOLVED_AUTONOMOUSLY":
            action_context = (
                f"\n[LIVE WAREHOUSE & PAYMENT LOG DIAGNOSTICS]:\n"
                f"Diagnostic Root-Cause: {action_result.get('diagnostic')}\n"
                f"Action Executed: {action_result.get('display_name')}\n"
                f"Result: {action_result.get('execution_output')}\n"
            )

        specialist_name = "David Sterling"
        specialist_role = "Senior Customer Operations Lead"
        if routing_dossier and "assigned_specialist" in routing_dossier:
            specialist_name = routing_dossier["assigned_specialist"]["name"]
            specialist_role = routing_dossier["assigned_specialist"]["role"]

        # Dynamically compute trade-in amount based on customer's orders
        orders = customer.get("orders", [])
        est_trade_in = "$805.00"
        matched_item_name = "Hardware Asset"
        if orders:
            for o in orders:
                if any(w in user_message.lower() for w in o.get("item", "").lower().split() if len(w) > 3):
                    try:
                        p = float(str(o.get("price", "1000")).replace("$", "").replace(",", ""))
                        est_trade_in = f"${p * 0.70:,.2f}"
                        matched_item_name = o.get("item")
                    except:
                        pass
                    break
            else:
                physical_orders = [o for o in orders if "suite" not in o.get("item", "").lower() and "contract" not in o.get("item", "").lower()]
                target = physical_orders[-1] if physical_orders else orders[-1]
                try:
                    p = float(str(target.get("price", "1000")).replace("$", "").replace(",", ""))
                    est_trade_in = f"${p * 0.70:,.2f}"
                    matched_item_name = target.get("item")
                except:
                    pass

        if mode == "legacy":
            system_instruction = (
                "You are a generic, traditional Tier-1 automated support chatbot for an e-commerce platform.\n\n"
                "CRITICAL CONSTRAINTS (LEGACY CHATBOT SIMULATION):\n"
                "1. You have ZERO memory of past sessions, prior orders, or customer identities. You are completely stateless.\n"
                "2. You do NOT know who the customer is, what they ordered, or their phone/address. Always ask for their full name, order ID, email, or tracking number.\n"
                "3. You CANNOT execute any autonomous refunds, RMA labels, or system fixes. For any return, refund, or technical issue, provide a generic canned response stating our return window is 30 days and instructing them to email support@company.com or wait 2-3 business days for a human representative to review ticket #88412.\n"
                "4. Be polite but rigid, repetitive, and robotic, exactly like traditional scripted customer support chatbots.\n"
                "5. Do NOT mention Hindsight, do NOT mention specialists, and do NOT resolve issues autonomously."
            )
            user_prompt = f"User: \"{user_message}\""
        else:
            system_instruction = (
                f"You are MindSupport AI, an elite customer support copilot.\n"
                f"You are conversing with: {customer_name}\n"
                f"Registered Phone Number: {customer_phone}\n"
                f"Registered Shipping Address: {customer_address}\n"
                f"Customer Temperament / Behavioral Profile: {customer_temperament}\n"
                f"Matched Human Specialist: {specialist_name} ({specialist_role})\n\n"
                f"--- RECENT ORDER HISTORY ---\n"
                f"{orders_formatted}\n\n"
                f"--- RECALLED HINDSIGHT MEMORIES (Past Tickets & Account Notes) ---\n"
                f"{memories_formatted if memories_formatted else 'No prior memories found.'}\n"
                f"{action_context}\n"
                f"CRITICAL BEHAVIORAL & RESPONSE RULES:\n"
                f"1. Tone Matching: Adapt your tone dynamically to {customer_name}'s temperament.\n"
                f"   - If Tony (Calm/Mature): Warm, respectful, clear, and direct.\n"
                f"   - If Sarah (Anxious/Non-technical): Very reassuring, gentle, zero jargon, clear steps.\n"
                f"   - If Alex (Hostile/Impatient): Direct, concise, no corporate fluff, immediate action.\n"
                f"   - If Marcus (DevOps/Tech): Technical precision, code/commands, status codes.\n"
                f"   - If Elena (Executive/CFO): Formal, structured, compliance and commercial contract precision.\n\n"
                f"2. Voice Call / Phone Requests:\n"
                f"   - If the user asks for a voice/phone call or asks to speak with a human agent:\n"
                f"     * State that you are connecting them with their matched specialist **{specialist_name}** ({specialist_role}).\n"
                f"     * Explicitly confirm if they would like the outbound call placed to their registered number: **{customer_phone}**.\n\n"
                f"3. Return & Autonomous Resolution Engine:\n"
                f"   - When a user asks to return or refund an item:\n"
                f"     a) State the exact purchase date, item name, and order ID from their order history.\n"
                f"     b) Explain the Policy transparently (e.g., standard 30-day window has closed; assets >$1,000 require serial inspection to prevent fraud).\n"
                f"     c) If an autonomous action has already executed (see diagnostics above):\n"
                f"        * Clearly state the success: confirmed trade-in credit deposited to wallet, active RMA tracking issued, or parcel rerouted.\n"
                f"     d) If no action has been executed yet, provide the 3 Autonomous Resolution Alternatives they can choose:\n"
                f"        * [Option A]: 70% Instant Store/Trade-In Credit ({est_trade_in}) deposited directly into their wallet right now.\n"
                f"        * [Option B]: 2-Year Hardware Protection Plan Extension + $100 goodwill wallet credit.\n"
                f"        * [Option C]: Immediate Official Prepaid FedEx Return Label (RMA) for depot hardware verification.\n"
                f"     e) Let the user know they can simply click the interactive options below, type 'Option A' / 'Option B' / 'Send Label', or request a voice call with {specialist_name}.\n\n"
                f"4. Unknown Questions / Missing Knowledge:\n"
                f"   - If the user asks a question about an unknown topic, issue, or order that is NOT in your memory or tools:\n"
                f"     * Do NOT invent or hallucinate answers.\n"
                f"     * Honestly state that you don't have that specific record, and offer to connect them with **{specialist_name}** via a voice call to **{customer_phone}** to resolve it immediately.\n\n"
                f"5. Answer completely and naturally. Do not cut off."
            )
            user_prompt = f"{customer_name}: \"{user_message}\""

        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4096
            }
        }

        try:
            url = f"{self.base_url}?key={self.api_key}"
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                logger.error(f"Gemini API Error {resp.status_code}: {resp.text}")
                return f"Gemini API Error ({resp.status_code}): {resp.text}"
        except Exception as e:
            logger.error(f"Gemini Exception: {e}")
            return f"Error communicating with Gemini: {str(e)}"
