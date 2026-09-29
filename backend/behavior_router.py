import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("behavior_router")

class BehaviorRouter:
    def __init__(self):
        self.specialists_path = os.path.join(os.path.dirname(__file__), "..", "data", "specialists.json")
        self.specialists = self._load_specialists()

    def _load_specialists(self) -> List[Dict[str, Any]]:
        try:
            with open(self.specialists_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load specialists: {e}")
            return []

    def get_specialist(self, specialist_id: str) -> Optional[Dict[str, Any]]:
        return next((s for s in self.specialists if s["id"] == specialist_id), None)

    def evaluate_routing(
        self,
        customer: Dict[str, Any],
        user_message: str,
        recalled_memories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Dynamically analyzes sentiment and emotional trajectory on EVERY SINGLE TEXT.
        Evaluates real-time tone shifts: from hostility -> apology -> politeness -> technical precision.
        """
        msg_lower = (user_message or "").lower()
        base_temperament = customer.get("temperament", "Standard")
        base_volatility = customer.get("volatility_score", 25)

        # 1. LIVE SIGNAL DETECTION ON CURRENT TEXT WITH WORD BOUNDARIES
        import re

        def _has_phrase(text: str, phrases: List[str]) -> bool:
            for p in phrases:
                pattern = r"\b" + re.escape(p) + r"\b"
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            return False

        hostility_keywords = [
            "shut up", "idiot", "stupid", "fuck", "fucking", "damn you", "useless garbage", 
            "piece of garbage", "scam", "scammers", "liar", "pissed off", "what the hell", 
            "sue you", "suing", "unacceptable", "take you to court", "incompetent", "moron", "shitty", 
            "bullshit", "ridiculous service", "i hate you", "abusive", "screaming"
        ]
        has_live_hostility = _has_phrase(msg_lower, hostility_keywords)

        apology_keywords = [
            "sorry", "apologize", "apologies", "my bad", "forgive me", "excuse me", 
            "didn't mean to", "calm down", "regret", "pardon", "lost my temper"
        ]
        has_live_apology = _has_phrase(msg_lower, apology_keywords)

        polite_keywords = [
            "thank you", "thanks", "appreciate", "please", "very kind", "polite", 
            "glad", "wonderful", "great help", "grateful", "good morning", 
            "good afternoon", "understood", "makes sense", "thank u"
        ]
        has_live_politeness = _has_phrase(msg_lower, polite_keywords)

        tech_keywords = [
            "curl", "pipeline", "429", "401", "sha-256", "redis", "kubernetes", 
            "pod", "sigabrt", "plist", "kafka", "bgp", "transceiver", "sre", "cluster", "offset"
        ]
        is_technical = _has_phrase(msg_lower, tech_keywords)

        exec_keywords = [
            "soc2", "contract", "prepay", "cfo", "compliance", "procurement", 
            "invoice breakdown", "vat", "net-60", "corporate", "commercial", "enterprise",
            "audit", "remittance", "tax invoice"
        ]
        is_executive = _has_phrase(msg_lower, exec_keywords) or ("Executive" in base_temperament) or ("CFO" in customer.get("role", ""))

        anxiety_keywords = [
            "stressed", "can't buy", "bread", "don't know", "explain simply", 
            "no technical words", "worried", "panic", "lost", "nervous", "confused"
        ]
        is_anxious = _has_phrase(msg_lower, anxiety_keywords)

        # 2. CHECK HINDSIGHT HISTORICAL MEMORIES FOR CONTEXT
        memory_texts = []
        for m in (recalled_memories or []):
            if isinstance(m, dict):
                memory_texts.append(m.get("text", "").lower() + " " + m.get("content", "").lower())
            elif isinstance(m, str):
                memory_texts.append(m.lower())
        all_memories_combined = " ".join(memory_texts)

        past_hostility_markers = [
            "hostility", "abusive", "shut up", "hostile", "aggressive", 
            "screamed", "swore", "cursed", "angry", "threatens contract cancellation"
        ]
        has_past_hostility = _has_phrase(all_memories_combined, past_hostility_markers)

        # 3. RECENCY-WEIGHTED EMOTIONAL STATE RESOLUTION
        if has_live_hostility:
            # Current message is actively hostile / profane
            target_specialist_id = "rachel_deescalation"
            detected_temperament = "Hostile / High Churn Risk"
            volatility_score = 95
            volatility_index = "Critical High (95%)"
            escalation_level = "CRITICAL DE-ESCALATION"
            response_urgency = "Immediate Priority (P0)"
            routing_reason = "Active hostility or combative language detected in current text. Immediate de-escalation required."

        elif has_live_apology:
            # Customer apologized in current message
            target_specialist_id = customer.get("recommended_specialist", "emily_smb")
            detected_temperament = "De-Escalated / Apologetic & Cooperative"
            volatility_score = 20
            volatility_index = "Low (20%) - Pacified"
            escalation_level = "DE-ESCALATION RESOLVED"
            response_urgency = "Standard Courteous"
            routing_reason = "Customer expressed sincere apology and de-escalated from prior tension. Volatility normalized to Low."

        elif is_executive:
            # Executive CFO / VIP Corporate customer
            target_specialist_id = "david_enterprise"
            detected_temperament = "Executive / Commercial VIP"
            volatility_score = 15
            volatility_index = "Low (15%)"
            escalation_level = "EXECUTIVE CONCIERGE"
            response_urgency = "High Priority (SLA 1hr)"
            routing_reason = "Executive commercial contract & compliance inquiry profile matched."

        elif is_technical or ("Technical" in base_temperament) or ("DevOps" in customer.get("role", "")):
            target_specialist_id = "carlos_sre"
            detected_temperament = "Technical / Systems Architect"
            volatility_score = 35
            volatility_index = "Low-Moderate (35%)"
            escalation_level = "PRINCIPAL SRE DISPATCH"
            response_urgency = "Engineering Escalation"
            routing_reason = "Deep technical infrastructure and diagnostic profile matched."

        elif is_anxious or ("Anxious" in base_temperament):
            target_specialist_id = "emily_smb"
            detected_temperament = "Anxious / Non-Technical"
            volatility_score = 55
            volatility_index = "Moderate (55%)"
            escalation_level = "PATIENT SMB SUCCESS"
            response_urgency = "Rapid Reassurance"
            routing_reason = "Customer expresses anxiety/confusion; assigned patient SMB onboarding specialist."

        elif has_live_politeness:
            target_specialist_id = customer.get("recommended_specialist", "david_enterprise" if is_executive else "emily_smb")
            detected_temperament = "Polite / Cooperative & Respectful"
            volatility_score = 15
            volatility_index = "Low (15%) - Very Polite"
            escalation_level = "COURTEOUS ENGAGEMENT"
            response_urgency = "Standard Courteous"
            routing_reason = "Customer is communicating with high courtesy and politeness. Emotional volatility at healthy baseline (15%)."

        elif has_past_hostility and customer.get("id") == "alex":
            target_specialist_id = "rachel_deescalation"
            detected_temperament = "Cautious Neutral (Past Conflict Noted)"
            volatility_score = 35
            volatility_index = "Moderate (35%) - Monitoring"
            escalation_level = "CAUTIOUS MONITORING"
            response_urgency = "Normal"
            routing_reason = "Prior ticket friction recorded in Hindsight memory; assigned dedicated retention lead."

        else:
            target_specialist_id = customer.get("recommended_specialist", "david_enterprise" if is_executive else "emily_smb")
            detected_temperament = base_temperament or "Calm / Standard"
            volatility_score = base_volatility
            volatility_index = f"Low ({base_volatility}%)"
            escalation_level = "STANDARD SPECIALIST MATCH"
            response_urgency = "Normal"
            routing_reason = f"Standard customer interaction profile for {customer.get('name')}."

        specialist = self.get_specialist(target_specialist_id) or self.specialists[0]

        specialist_summary = {
            "id": specialist.get("id"),
            "name": specialist.get("name"),
            "role": specialist.get("role"),
            "phone": specialist.get("phone", "+1 (800) 555-0100"),
            "avatar": specialist.get("avatar"),
            "superpower": specialist.get("superpower"),
            "authority": specialist.get("goodwill_authority")
        }

        handoff_dossier = {
            "customer_name": customer.get("name"),
            "company": customer.get("company"),
            "plan": customer.get("plan"),
            "temperament": detected_temperament,
            "detected_temperament": detected_temperament,
            "volatility_score": volatility_score,
            "volatility_index": volatility_index,
            "vip_level": "Tier 1 Priority" if volatility_score >= 70 else "Standard",
            "response_urgency": response_urgency,
            "escalation_level": escalation_level,
            "routing_reason": routing_reason,
            "routing_rationale": routing_reason,
            "assigned_specialist": specialist_summary,
            "matched_specialist": specialist_summary,
            "tactical_playbook": specialist.get("handling_playbook"),
            "recommended_opener": self._generate_opener(customer, specialist, has_live_hostility)
        }

        return handoff_dossier

    def _generate_opener(self, customer: Dict[str, Any], specialist: Dict[str, Any], aggressive: bool) -> str:
        first_name = customer.get("name", "").split(" ")[0]
        spec_name = specialist.get("name", "").split(" ")[0]

        if aggressive:
            return f"\"Hello {first_name}, I'm {spec_name} with Executive Customer Relations. I see the frustration this recurring blocker has caused, and I am personally taking ownership of your account right now.\""
        elif "Carlos" in spec_name:
            return f"\"Hey {first_name}, Carlos here from Principal SRE. I reviewed your cluster logs and isolated the exact root cause. Here is the direct patch.\""
        elif "Emily" in spec_name:
            return f"\"Hi {first_name}! Emily here from Customer Success. Don't worry at all, we will walk through this together step-by-step!\""
        else:
            return f"\"Hello {first_name}, David Sterling here. I have your complete enterprise account history and compliance packet ready for review.\""
