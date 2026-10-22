"""Consistent Hash Ring Router.
100% Python Standard Library.
"""
import bisect
import hashlib
import math
from typing import Dict, Any, List, Optional, Set

class ConsistentHashRingRouter:
    """Consistent hashing ring with virtual nodes for distributed LLM cache and agent partitioning."""
    def __init__(self, virtual_node_factor: int = 100):
        self.virtual_node_factor = virtual_node_factor
        self.ring: List[int] = []
        self.hash_to_node: Dict[int, str] = {}
        self.physical_nodes: Set[str] = set()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)

    def add_nodes(self, nodes: List[str]) -> Dict[str, Any]:
        for node in nodes:
            if node in self.physical_nodes:
                continue
            self.physical_nodes.add(node)
            for v in range(self.virtual_node_factor):
                v_key = f"{node}#vn_{v}"
                h = self._hash(v_key)
                bisect.insort(self.ring, h)
                self.hash_to_node[h] = node
        return {
            "physical_nodes": sorted(list(self.physical_nodes)),
            "total_virtual_nodes": len(self.ring)
        }

    def remove_node(self, node: str) -> Dict[str, Any]:
        if node not in self.physical_nodes:
            return {"removed": False, "node": node}
        self.physical_nodes.remove(node)
        new_ring = []
        for h in self.ring:
            if self.hash_to_node[h] == node:
                del self.hash_to_node[h]
            else:
                new_ring.append(h)
        self.ring = new_ring
        return {
            "removed": True,
            "node": node,
            "remaining_nodes": sorted(list(self.physical_nodes)),
            "total_virtual_nodes": len(self.ring)
        }

    def get_node_for_key(self, key: str) -> Optional[str]:
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.ring, h)
        if idx == len(self.ring):
            idx = 0
        target_hash = self.ring[idx]
        return self.hash_to_node[target_hash]

    def get_distribution_stats(self, sample_keys: List[str]) -> Dict[str, Any]:
        if not self.physical_nodes or not sample_keys:
            return {"error": "Ring empty or no sample keys"}
        counts = {n: 0 for n in self.physical_nodes}
        for k in sample_keys:
            assigned = self.get_node_for_key(k)
            if assigned:
                counts[assigned] += 1

        total = len(sample_keys)
        mean = total / len(self.physical_nodes)
        variance = sum((c - mean) ** 2 for c in counts.values()) / len(counts)
        std_dev = math.sqrt(variance)

        distribution = {n: {"count": c, "percentage": round((c / total) * 100, 2)} for n, c in counts.items()}
        return {
            "total_keys": total,
            "node_count": len(self.physical_nodes),
            "mean_keys_per_node": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "distribution": distribution
        }
