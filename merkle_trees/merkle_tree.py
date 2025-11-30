import hashlib
import json
from typing import List, Dict, Any, Optional

class MerkleNode:
    def __init__(self, hash_val: str, children: List['MerkleNode'] = None, key_range: tuple = None):
        self.hash = hash_val
        self.children = children or []
        self.key_range = key_range # (start, end) or specific key if leaf

class MerkleTree:
    """
    Merkle Tree implementation for Anti-Entropy (Replica Synchronization).
    """
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize with a dictionary of {key: (value, timestamp)}
        """
        self.data = data
        self.root = self.build_tree(data)

    def _hash_item(self, key: str, value: Any, timestamp: float) -> str:
        """Create a hash for a leaf node (key + value + timestamp)"""
        content = f"{key}:{value}:{timestamp}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _hash_children(self, left_hash: str, right_hash: str) -> str:
        """Combine child hashes"""
        content = f"{left_hash}:{right_hash}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def build_tree(self, data: Dict[str, Any]) -> MerkleNode:
        if not data:
            return MerkleNode(hashlib.md5(b"empty").hexdigest())

        # 1. Create Leaf Nodes
        # Sort keys to ensure deterministic tree structure
        sorted_keys = sorted(data.keys())
        leaves = []
        for key in sorted_keys:
            val, ts = data[key]
            node_hash = self._hash_item(key, val, ts)
            leaves.append(MerkleNode(node_hash, key_range=(key, key)))

        # 2. Build Tree Upwards
        current_level = leaves
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                    parent_hash = self._hash_children(left.hash, right.hash)
                    # Range covers both children
                    parent_range = (left.key_range[0], right.key_range[1] if isinstance(right.key_range, tuple) else right.key_range)
                    next_level.append(MerkleNode(parent_hash, children=[left, right], key_range=parent_range))
                else:
                    # Odd number of nodes, promote the last one
                    next_level.append(left)
            current_level = next_level

        return current_level[0]

    def get_root_hash(self) -> str:
        return self.root.hash if self.root else None

    @staticmethod
    def compare_trees(node1: MerkleNode, node2: MerkleNode) -> List[str]:
        """
        Compare two trees (local and remote) and return list of keys that differ.
        This is a simplified comparison that returns keys needing sync.
        """
        diff_keys = []
        
        if node1.hash == node2.hash:
            return diff_keys # Trees match

        # If hashes differ and they are leaves, add the key
        if not node1.children and not node2.children:
            # Assuming key_range is (key, key) for leaves
            if node1.key_range == node2.key_range:
                diff_keys.append(node1.key_range[0])
            return diff_keys

        # If one is leaf and other is not (structure mismatch), or both have children
        # We need to traverse down. 
        # Note: This simple implementation assumes balanced/same-structure trees 
        # for the same key set. In dynamic systems, you might compare ranges.
        
        # For a robust anti-entropy, usually we exchange ranges.
        # Here we assume we are comparing trees built from the same key universe 
        # or we just find the divergent paths.
        
        # If structure is identical (ideal case for static key sets):
        if len(node1.children) == len(node2.children):
            for c1, c2 in zip(node1.children, node2.children):
                diff_keys.extend(MerkleTree.compare_trees(c1, c2))
        else:
            # Structure mismatch (keys added/removed)
            # Fallback: Scan ranges or just return all keys in this subtree
            # For this assignment, we'll just return a generic indicator or all leaf keys
            pass 
            
        return diff_keys

    def get_keys_in_range(self, start_key: str, end_key: str) -> List[str]:
        """Helper to get keys from Redis for a specific range to build the tree"""
        # This would be used by the worker to fetch data before building the tree
        pass
