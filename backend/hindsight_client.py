import os
import requests
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("hindsight_client")
logging.basicConfig(level=logging.INFO)

class HindsightMemoryManager:
    def __init__(self):
        self.api_key = os.getenv("HINDSIGHT_API_KEY", "")
        self.api_url = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io").rstrip("/")
        self.bank_id = os.getenv("HINDSIGHT_BANK_ID", "mindsupport_master_bank")
        self.local_cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "local_memory_cache.json")
        self._init_local_cache()

    def _init_local_cache(self):
        os.makedirs(os.path.dirname(self.local_cache_path), exist_ok=True)
        if not os.path.exists(self.local_cache_path):
            with open(self.local_cache_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def retain(self, tag: str, content: str, context: str = "customer_interaction") -> Dict[str, Any]:
        """Save a new memory to Hindsight Cloud and local cache."""
        cloud_success = False
        response_data = {}

        if self.api_key:
            try:
                url = f"{self.api_url}/v1/default/banks/{self.bank_id}/memories"
                payload = {
                    "items": [
                        {
                            "content": content,
                            "context": context,
                            "tags": [tag]
                        }
                    ]
                }
                resp = requests.post(url, headers=self._get_headers(), json=payload, timeout=8)
                if resp.status_code in [200, 201]:
                    cloud_success = True
                    response_data = resp.json()
                    logger.info(f"[Hindsight Cloud] Retained memory for tag '{tag}'")
                else:
                    logger.warning(f"[Hindsight Cloud] Retain status {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"[Hindsight Cloud] Retain exception: {e}")

        # Always update local cache for instant redundancy & visual stats
        self._save_local(tag, content, context)

        return {
            "success": True,
            "cloud_synced": cloud_success,
            "tag": tag,
            "content": content,
            "details": response_data
        }

    def recall(self, tag: str, query: str) -> List[Dict[str, Any]]:
        """Recall relevant memories from Hindsight Cloud (with local fallback)."""
        recalled_items = []
        
        if self.api_key:
            try:
                url = f"{self.api_url}/v1/default/banks/{self.bank_id}/memories/recall"
                payload = {
                    "query": query,
                    "tags": [tag],
                    "budget": "high",
                    "max_tokens": 4096
                }
                resp = requests.post(url, headers=self._get_headers(), json=payload, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    for item in results:
                        recalled_items.append({
                            "text": item.get("text", ""),
                            "type": item.get("type", "memory"),
                            "entities": item.get("entities", []),
                            "scores": item.get("scores", {}),
                            "source": "Hindsight Cloud",
                            "mentioned_at": item.get("mentioned_at")
                        })
                    logger.info(f"[Hindsight Cloud] Recalled {len(recalled_items)} memories for '{tag}'")
                    if recalled_items:
                        return recalled_items
            except Exception as e:
                logger.error(f"[Hindsight Cloud] Recall exception: {e}")

        # Fallback to local memory bank if cloud is empty or query is general
        local_items = self._search_local(tag, query)
        return local_items

    def _save_local(self, tag: str, content: str, context: str):
        try:
            with open(self.local_cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

        if tag not in cache:
            cache[tag] = []

        cache[tag].append({
            "text": content,
            "context": context,
            "timestamp": "now"
        })

        with open(self.local_cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)

    def _search_local(self, tag: str, query: str) -> List[Dict[str, Any]]:
        try:
            with open(self.local_cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            return []

        memories = cache.get(tag, [])
        query_words = set(query.lower().split())
        
        scored = []
        for m in memories:
            text = m.get("text", "")
            matches = sum(1 for w in query_words if w in text.lower())
            scored.append({
                "text": text,
                "type": "cached_memory",
                "entities": [],
                "scores": {"semantic": 0.85 if matches > 0 else 0.50},
                "source": "Local Memory Bank"
            })
        return scored

    def seed_customer_memories(self, customers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preload memories for all 10 customer personas into Hindsight."""
        seeded_count = 0
        for cust in customers:
            cust_id = cust.get("id")
            memories = cust.get("preloaded_memories", [])
            for mem_text in memories:
                self.retain(tag=cust_id, content=mem_text, context="ticket_history")
                seeded_count += 1
        return {"status": "success", "seeded_count": seeded_count}
