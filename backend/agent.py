"""
AegisOps Intelligence Engine:
Powers Incident Triage, First-Principles Zero-Precedent Reasoning,
Memory Recall Synthesis with Hindsight, and the Side-by-Side Comparison Generator.
"""

import os
from typing import Dict, Any, List, Optional
from backend.memory_manager import MemoryManager

# Optional Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class IncidentAgent:
    def __init__(self, memory_manager: MemoryManager, gemini_api_key: Optional[str] = None):
        self.memory = memory_manager
        self.api_key = gemini_api_key or GEMINI_API_KEY
        self.gemini_model = None
        self._init_gemini()

    def _init_gemini(self):
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                print("[IncidentAgent] Connected to Google Gemini 1.5 Flash.")
            except Exception as e:
                print(f"[IncidentAgent] Gemini init error: {e}. Falling back to internal cognitive heuristics.")
                self.gemini_model = None

    def update_gemini_key(self, api_key: str):
        self.api_key = api_key
        self._init_gemini()

    def triage_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main cognitive dispatch:
        1. Recalls from Hindsight memory bank
        2. If high match -> Warm Memory Recovery Mode
        3. If low/zero match -> First-Principles Diagnostic Mode (User's feature)
        4. Generates side-by-side 'Generic LLM vs AegisOps' comparison
        5. Generates concise Jarvis spoken briefing
        """
        title = incident.get("title", "")
        error_msg = incident.get("error_message", "")
        service = incident.get("service", "")
        tags = incident.get("tags", [])

        # Search Hindsight memory bank
        query = f"{service} {title} {error_msg}"
        memory_matches = self.memory.recall(query=query, tags=tags)

        # Check top match
        top_match = memory_matches[0] if memory_matches else None
        top_score = top_match["score"] if top_match else 0.0

        if top_score >= 0.65:
            # WARM MEMORY MODE (Pattern recognized from past incident)
            mode = "WARM_MEMORY_PLAYBOOK"
            past_mem = top_match["memory"]
            
            diagnosis = {
                "mode": mode,
                "confidence_score": top_score,
                "matched_incident_id": past_mem["incident_id"],
                "matched_incident_title": past_mem["title"],
                "historical_timestamp": past_mem["timestamp"],
                "root_cause_explanation": past_mem["root_cause"],
                "recommended_action": past_mem["successful_resolution"],
                "runbook_command": past_mem["runbook_command"],
                "failed_attempts_warning": past_mem.get("failed_attempts", []),
                "vigilance_stage": past_mem.get("vigilance_stage", "PROVISIONAL"),
                "hypotheses": []
            }

            jarvis_speech = (
                f"Critical alert on {service}. Error rate matches Incident {past_mem['incident_id']} with "
                f"{int(top_score * 100)} percent confidence. The root cause is {past_mem['root_cause']}. "
                f"Do not restart the pods blindly. Runbook command is prepared on your terminal."
            )

        else:
            # FIRST-PRINCIPLES ZERO-PRECEDENT MODE (Brand new unknown outage!)
            mode = "FIRST_PRINCIPLES_DISCOVERY"
            
            # Formulate 3 ranked hypotheses based on error structure
            hypotheses = self._generate_first_principles_hypotheses(incident)
            
            diagnosis = {
                "mode": mode,
                "confidence_score": 0.0,
                "matched_incident_id": None,
                "matched_incident_title": "Zero Historical Precedent Detected",
                "historical_timestamp": None,
                "root_cause_explanation": (
                    "⚠️ No matching prior incidents in Hindsight memory. "
                    "Engaging First-Principles Diagnostic Engine to isolate root cause through iterative probes."
                ),
                "recommended_action": "Execute the ranked diagnostic probe commands below to eliminate false hypotheses.",
                "runbook_command": hypotheses[0]["probe_command"] if hypotheses else "dmesg -T | tail -n 50",
                "failed_attempts_warning": [
                    "Avoid applying unverified production mutations without running non-destructive probes first.",
                    "Do not reboot nodes without capturing slabinfo / core dump."
                ],
                "vigilance_stage": "UNEXPLORED",
                "hypotheses": hypotheses
            }

            jarvis_speech = (
                f"Attention. New unprecedented outage detected on {service}. Zero historical matches found in Hindsight. "
                f"Switching to first-principles diagnostic mode. Top hypothesis is {hypotheses[0]['title'] if hypotheses else 'resource starvation'}. "
                f"Diagnostic probe command ready on your screen."
            )

        # Generate the Side-by-Side comparison (Standard LLM vs AegisOps)
        standard_llm_output = self._generate_generic_llm_comparison(incident)

        return {
            "incident": incident,
            "diagnosis": diagnosis,
            "comparison": {
                "standard_llm": standard_llm_output,
                "aegisops_agent": {
                    "mode": mode,
                    "insight": diagnosis["root_cause_explanation"],
                    "proven_runbook": diagnosis["runbook_command"],
                    "historical_precedent": f"Matches {diagnosis['matched_incident_id']}" if diagnosis['matched_incident_id'] else "Zero Precedent (Synthesizing New Knowledge)",
                    "avoidance": diagnosis["failed_attempts_warning"]
                }
            },
            "jarvis_voice_summary": jarvis_speech
        }

    def _generate_first_principles_hypotheses(self, incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates 3 ranked, testable hypotheses for novel issues
        """
        title = incident.get("title", "").lower()
        err = incident.get("error_message", "").lower()

        if "kmem" in err or "slab" in err or "memory" in title or "ebpf" in title:
            return [
                {
                    "rank": 1,
                    "title": "Kernel Slab Allocation Leak in eBPF / CGroup",
                    "probability": "65%",
                    "rationale": "High SUnreclaim slab consumption pointing to unreleased socket buffer maps or kernel tracepoint handles.",
                    "probe_command": "cat /proc/meminfo | grep -E 'Slab|SUnreclaim'",
                    "expected_signature": "SUnreclaim > 10GB indicating kernel-level map leakage"
                },
                {
                    "rank": 2,
                    "title": "Kubelet Runtime Socket Hang & False Eviction",
                    "probability": "25%",
                    "rationale": "Containerd shim not releasing terminated pod cgroups, triggering synthetic NodeNotReady state.",
                    "probe_command": "systemctl status containerd --no-pager",
                    "expected_signature": "Active state: active (running) with high open file descriptors"
                },
                {
                    "rank": 3,
                    "title": "Hardware Memory Controller Bit-flip (ECC Error)",
                    "probability": "10%",
                    "rationale": "Hardware-level memory parity failure causing kernel memory subsystem panic.",
                    "probe_command": "dmesg -T | grep -i 'edac\\|mce'",
                    "expected_signature": "Machine Check Exception or hardware memory bus error log"
                }
            ]

        # Default multi-tier hypothesis template
        return [
            {
                "rank": 1,
                "title": "Resource Exhaustion / Deadlock in Connection Layer",
                "probability": "55%",
                "rationale": "Worker processes blocked awaiting I/O multiplexer or socket lock.",
                "probe_command": "netstat -an | grep TIME_WAIT | wc -l",
                "expected_signature": "Count > 5000 indicating socket exhaustion"
            },
            {
                "rank": 2,
                "title": "Upstream Dependency Degradation / DNS Latency",
                "probability": "30%",
                "rationale": "Slow upstream response cascading down service queue.",
                "probe_command": "curl -o /dev/null -s -w 'Total: %{time_total}s\\n' http://localhost:8080/health",
                "expected_signature": "Latency > 3.0s"
            },
            {
                "rank": 3,
                "title": "Disk I/O Saturation or Inode Depletion",
                "probability": "15%",
                "rationale": "Logging or temp directory full causing synchronous write halts.",
                "probe_command": "df -h && df -i",
                "expected_signature": "Use% = 100% or IUse% = 100%"
            }
        ]

    def _generate_generic_llm_comparison(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates what a standard, stateless LLM (ChatGPT / vanilla prompt) produces:
        Verbose, generalized, textbook advice with no contextual memory.
        """
        service = incident.get("service", "service")
        title = incident.get("title", "")

        return {
            "title": "Standard Stateless LLM (Without Hindsight)",
            "output_text": (
                f"### General Troubleshooting Guide for {title}\n"
                f"To diagnose the issue on `{service}`, consider these generic steps:\n"
                f"1. **Check System Metrics:** Inspect CPU and memory utilization using `top` or your monitoring dashboard.\n"
                f"2. **Inspect Application Logs:** Look for error traces in `/var/log` or CloudWatch.\n"
                f"3. **Network & Connectivity:** Ensure all security groups and firewalls allow inbound traffic.\n"
                f"4. **Restart the Pod/Service:** Try running `kubectl rollout restart` or rebooting the server to clear transient state.\n"
                f"5. **Scale Up Resources:** If load is high, consider increasing replicas or upgrading machine instance types."
            ),
            "critique": "Notice: The generic LLM suggests restarting the service—which in our historical incident actually exacerbated the problem by orphaning locks! It lacks organizational memory."
        }
