"""
Realistic SRE Telemetry & Outage Scenarios for AegisOps
Provides rich, production-grade synthetic alerts, telemetry, and terminal probe outputs.
"""

from typing import Dict, Any, List

SCENARIOS = {
    "checkout_db_exhaustion": {
        "id": "INC-201",
        "service": "checkout-api-gateway",
        "severity": "P1-CRITICAL",
        "title": "504 Gateway Timeout on /v2/checkout/complete",
        "error_message": "HTTP 504: Upstream DB connection pool exhausted. Active: 150/150, Waiting threads: 842. Connection acquisition timeout after 15000ms.",
        "stack_trace": """Traceback (most recent call last):
  File "/app/routes/checkout.py", line 142, in process_payment
    async with db.pool.acquire(timeout=15.0) as conn:
  File "asyncpg/pool.py", line 421, in acquire
    raise exceptions.PoolTimeoutError('connection acquisition timeout')
asyncpg.exceptions.PoolTimeoutError: connection acquisition timeout: pool exhausted""",
        "tags": ["checkout", "504", "pool-exhaustion", "database", "redis"],
        "expected_match_id": "INC-104"
    },
    
    "ebpf_kernel_leak": {
        "id": "INC-305",
        "service": "k8s-worker-pool-fra1",
        "severity": "P0-FATAL",
        "title": "Kernel Slab Memory Leak & Pod Eviction Cascades",
        "error_message": "NodeNotReady: cgroup memory limit exceeded in kmem. Kmem leak triggered OOMKiller on critical ingress-router pods.",
        "stack_trace": """[41982.112] kernel: [oom-killer] kmem slab unreclaimable: 14201MB / 16384MB
[41982.115] kernel: memory cgroup out of memory: Kill process 94812 (envoy) score 912 or sacrifice child
[41982.120] kubelet: Node node-fra1-w04 status is now: NodeNotReady (MemoryPressure)""",
        "tags": ["kernel", "ebpf", "memory-pressure", "kmem", "node-down"],
        "expected_match_id": None  # ZERO HISTORICAL PRECEDENT! Triggers First-Principles mode!
    },

    "kafka_rebalance_storm": {
        "id": "INC-409",
        "service": "order-stream-pipeline",
        "severity": "P2-HIGH",
        "title": "Consumer Group 'order-processors' Flapping & Commit Failures",
        "error_message": "CommitFailedException: Consumer group 'order-processors' rebalance in progress. Max poll interval (30000ms) exceeded.",
        "stack_trace": """org.apache.kafka.clients.consumer.CommitFailedException: Commit cannot be completed since the group has already rebalanced and assigned the partitions to another member. This means that the time between subsequent calls to poll() was longer than the configured max.poll.interval.ms
  at org.apache.kafka.clients.consumer.internals.ConsumerCoordinator.sendOffsetCommitRequest(ConsumerCoordinator.java:1204)""",
        "tags": ["kafka", "streaming", "consumer-lag", "rebalance"],
        "expected_match_id": "INC-089"
    }
}

PROBE_COMMAND_OUTPUTS = {
    "redis-cli keys 'lock:*'": """1) "lock:checkout_sync:usr_8921"
2) "lock:checkout_sync:usr_9912"
3) "lock:checkout_sync:usr_0023"
(3 orphaned keys found with TTL = -1 [NO EXPIRATION])""",

    "kubectl get pods -n prod -l app=checkout-api": """NAME                            READY   STATUS    RESTARTS   AGE
checkout-api-7b89f8d9b4-2vpl9   1/1     Running   3 (12m ago) 2d
checkout-api-7b89f8d9b4-8xk21   1/1     Running   4 (9m ago)  2d
checkout-api-7b89f8d9b4-w91mn   1/1     Running   2 (15m ago) 2d""",

    "cat /proc/meminfo | grep -E 'Slab|SUnreclaim'": """Slab:           14820120 kB
SReclaimable:     412092 kB
SUnreclaim:     14408028 kB   <-- [CRITICAL: 14.4GB unreclaimable kernel slab]""",

    "uname -r && bpftool prog list": """Linux 6.8.0-45-generic
14: cgroup_skb  tag 8f9a2b1c4d  gpl
18: tracepoint  name trace_tcp_drop  gpl (active leak trace: unreleased maps)""",

    "kafka-consumer-groups.sh --describe --group order-processors": """GROUP            TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID
order-processors orders-v1       0          1489210         1598200         108990          order-proc-1
order-processors orders-v1       1          1481020         1601000         119980          order-proc-2
[STATUS: REBALANCING - Heartbeat deadline expired]"""
}

def get_probe_result(cmd: str) -> str:
    cleaned = cmd.strip().lower()
    for key, output in PROBE_COMMAND_OUTPUTS.items():
        if key in cleaned or cleaned in key:
            return output
    # Substring / keyword fallbacks
    if "meminfo" in cleaned or "slab" in cleaned:
        return PROBE_COMMAND_OUTPUTS["cat /proc/meminfo | grep -E 'Slab|SUnreclaim'"]
    if "redis" in cleaned or "lock" in cleaned:
        return PROBE_COMMAND_OUTPUTS["redis-cli keys 'lock:*'"]
    if "bpf" in cleaned or "uname" in cleaned:
        return PROBE_COMMAND_OUTPUTS["uname -r && bpftool prog list"]
    if "pod" in cleaned or "kubectl" in cleaned:
        return PROBE_COMMAND_OUTPUTS["kubectl get pods -n prod -l app=checkout-api"]
    if "kafka" in cleaned or "lag" in cleaned:
        return PROBE_COMMAND_OUTPUTS["kafka-consumer-groups.sh --describe --group order-processors"]

    return f"[Probe Execution]: Command '{cmd}' executed with exit code 0. System output recorded: All thread buffers within nominal bounds."
