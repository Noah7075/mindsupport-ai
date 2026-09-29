"""
Memory Manager for AegisOps:
Interfaces with Hindsight API (Vectorize) with automatic local fallback / sync
so the application is 100% functional both with cloud credits and out-of-the-box.
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from hindsight_client import Hindsight
    HINDSIGHT_AVAILABLE = True
except ImportError:
    HINDSIGHT_AVAILABLE = False


def _load_env_if_needed():
    if not os.getenv("HINDSIGHT_API_KEY"):
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        if v:
                            os.environ[k] = v

_load_env_if_needed()


class MemoryManager:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, bank_id: str = "aegisops-sre"):
        self.base_url = base_url or os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
        self.api_key = api_key or os.getenv("HINDSIGHT_API_KEY", "")
        self.bank_id = bank_id
        self.client = None
        self.local_storage_file = os.path.join(os.path.dirname(__file__), "hindsight_local_bank.json")
        self.local_memories: List[Dict[str, Any]] = self._load_local_memories()

        self._init_client()

    def _init_client(self):
        if HINDSIGHT_AVAILABLE and self.api_key:
            try:
                self.client = Hindsight(base_url=self.base_url, api_key=self.api_key)
                print(f"[MemoryManager] Connected to Hindsight at {self.base_url}")
            except Exception as e:
                print(f"[MemoryManager] Could not initialize Hindsight cloud client: {e}. Using local persistent store.")
                self.client = None
        else:
            print("[MemoryManager] Operating in Hybrid/Local persistent mode for Hindsight memory.")

    def update_credentials(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self._init_client()

    def _load_local_memories(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.local_storage_file):
            try:
                with open(self.local_storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data and len(data) > 0:
                        return data
            except Exception:
                pass
        
        # Pre-seed realistic historical memories so the demo is immediately rich!
        seed_data = [
            {
                "id": "mem-104",
                "incident_id": "INC-104",
                "title": "PostgreSQL Connection Pool Exhaustion on Checkout Service",
                "timestamp": "2026-09-14T03:15:00Z",
                "symptoms": "504 Gateway Timeout, connection pool latency > 5000ms, DB connection count at 150/150",
                "root_cause": "Orphaned distributed lock in Redis during unhandled Stripe webhook retry, blocking checkout threads from releasing DB connections",
                "successful_resolution": "Flushed orphaned lock via `redis-cli DEL lock:checkout_sync` and recycled idle connections with `scripts/recycle_pool.sh`",
                "failed_attempts": ["Blind pod restart failed because locks persisted in Redis", "Increasing max_connections crashed DB buffer cache"],
                "runbook_command": "redis-cli DEL lock:checkout_sync && ./scripts/recycle_pool.sh checkout-svc",
                "vigilance_stage": "BATTLE_TESTED",
                "verification_score": 0.98,
                "created_at": "2026-09-14T03:45:00Z",
                "tags": ["database", "redis", "checkout", "pool-exhaustion", "504"]
            },
            {
                "id": "mem-089",
                "incident_id": "INC-089",
                "title": "Kafka Consumer Group Rebalance Storm on Order Processing",
                "timestamp": "2026-08-28T14:22:00Z",
                "symptoms": "Message lag jumping 100k/sec, heartbeat timeouts, consumer rebalance loops",
                "root_cause": "`max.poll.interval.ms` set too low (30000ms) for heavy image-processing payloads",
                "successful_resolution": "Bumped `max.poll.interval.ms` to 300000ms in consumer config and executed rolling restart",
                "failed_attempts": ["Scaling up consumer replicas caused worse partition rebalancing thrash"],
                "runbook_command": "kubectl patch configmap order-consumer-cfg -p '{\"data\":{\"POLL_INTERVAL_MS\":\"300000\"}}'",
                "vigilance_stage": "BATTLE_TESTED",
                "verification_score": 0.95,
                "created_at": "2026-08-28T15:10:00Z",
                "tags": ["kafka", "streaming", "consumer-lag", "rebalance"]
            }
        ]
        self._save_local_memories(seed_data)
        return seed_data

    def _save_local_memories(self, memories: List[Dict[str, Any]]):
        try:
            with open(self.local_storage_file, "w", encoding="utf-8") as f:
                json.dump(memories, f, indent=2)
        except Exception as e:
            print(f"[MemoryManager] Error saving local memories: {e}")

    def retain(self, 
               incident_id: str, 
               title: str, 
               symptoms: str, 
               root_cause: str, 
               successful_resolution: str, 
               failed_attempts: List[str],
               runbook_command: str,
               vigilance_stage: str = "PROVISIONAL",
               tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Store a structured lesson into Hindsight memory.
        """
        timestamp_str = datetime.utcnow().isoformat() + "Z"
        memory_item = {
            "id": f"mem-{int(time.time())}",
            "incident_id": incident_id,
            "title": title,
            "timestamp": timestamp_str,
            "symptoms": symptoms,
            "root_cause": root_cause,
            "successful_resolution": successful_resolution,
            "failed_attempts": failed_attempts,
            "runbook_command": runbook_command,
            "vigilance_stage": vigilance_stage,  # PROVISIONAL -> OBSERVATION -> BATTLE_TESTED
            "verification_score": 0.65 if vigilance_stage == "PROVISIONAL" else 0.95,
            "created_at": timestamp_str,
            "tags": tags or ["incident", "production"]
        }

        # Formulate Hindsight natural language memory unit
        content_for_hindsight = (
            f"Incident {incident_id}: {title}.\n"
            f"Symptoms: {symptoms}.\n"
            f"Root Cause: {root_cause}.\n"
            f"Proven Resolution: {successful_resolution}.\n"
            f"Failed Attempts / Anti-patterns: {', '.join(failed_attempts) if failed_attempts else 'None'}.\n"
            f"Runbook: {runbook_command}.\n"
            f"Vigilance State: {vigilance_stage}."
        )

        # Call cloud Hindsight if connected
        if self.client:
            try:
                self.client.retain(
                    bank_id=self.bank_id,
                    content=content_for_hindsight,
                    tags=memory_item["tags"],
                    metadata={"incident_id": incident_id, "stage": vigilance_stage}
                )
                print(f"[MemoryManager] Successfully retained {incident_id} in Hindsight Cloud.")
            except Exception as e:
                print(f"[MemoryManager] Cloud retain failed: {e}. Retained in local store.")

        # Always persist locally for instant speed and offline demo resilience
        self.local_memories.insert(0, memory_item)
        self._save_local_memories(self.local_memories)
        return memory_item

    def recall(self, query: str, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Query Hindsight memory for matching incident experiences.
        """
        cloud_results = []
        if self.client:
            try:
                resp = self.client.recall(bank_id=self.bank_id, query=query, tags=tags)
                # Parse cloud response
                if hasattr(resp, 'results') and resp.results:
                    for r in resp.results:
                        cloud_results.append({
                            "content": getattr(r, 'content', str(r)),
                            "score": getattr(r, 'score', 0.85)
                        })
            except Exception as e:
                print(f"[MemoryManager] Cloud recall fallback: {e}")

        # Local semantic-style matching with keyword + tag boosting
        stopwords = {"the", "and", "for", "with", "this", "that", "from", "when", "used", "error", "traceback", "line", "file", "most", "recent", "call", "last"}
        query_words = [w for w in query.lower().replace("-", " ").replace("_", " ").replace(":", " ").replace(".", " ").split() if len(w) > 2 and w not in stopwords]
        scored = []
        for mem in self.local_memories:
            text = f"{mem['title']} {mem['symptoms']} {mem['root_cause']} {' '.join(mem['tags'])} {mem.get('runbook_command', '')}".lower()
            overlap_count = sum(1 for w in query_words if w in text)
            
            # Need at least 2 distinct domain keywords to match
            score = 0.0
            if overlap_count >= 2 and query_words:
                ratio = overlap_count / len(query_words)
                score = round(min(0.98, ratio * 1.1), 2)
                if score >= 0.80 and mem.get("vigilance_stage") == "BATTLE_TESTED":
                    score = min(0.98, score + 0.05)
                
            if score >= 0.70:
                scored.append({"memory": mem, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def update_vigilance(self, memory_id: str, new_stage: str) -> Optional[Dict[str, Any]]:
        """
        Upgrade or downgrade memory vigilance stage (e.g. from PROVISIONAL to OBSERVATION to BATTLE_TESTED)
        """
        for mem in self.local_memories:
            if mem["id"] == memory_id or mem["incident_id"] == memory_id:
                mem["vigilance_stage"] = new_stage
                if new_stage == "BATTLE_TESTED":
                    mem["verification_score"] = 0.99
                elif new_stage == "OBSERVATION":
                    mem["verification_score"] = 0.85
                elif new_stage == "RECURRENT_FAILURE":
                    mem["verification_score"] = 0.35
                self._save_local_memories(self.local_memories)
                return mem
        return None

    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by id or incident_id
        """
        initial_len = len(self.local_memories)
        self.local_memories = [m for m in self.local_memories if m.get("id") != memory_id and m.get("incident_id") != memory_id]
        if len(self.local_memories) < initial_len:
            self._save_local_memories(self.local_memories)
            return True
        return False

    def clear_all(self):
        """
        Clear all memories from the bank
        """
        self.local_memories = []
        self._save_local_memories(self.local_memories)
        return True

    def get_all(self) -> List[Dict[str, Any]]:
        return self.local_memories
