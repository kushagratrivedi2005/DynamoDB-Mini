import redis
import json
import time
import logging
import rpyc
import threading
from typing import Dict, Any, List, Tuple

class HintedHandoff:
    """
    Manages hinted handoff for failed nodes.
    Stores hints in Redis when a replica is unreachable.
    """
    def __init__(self, redis_client: redis.Redis, local_node_id: str):
        self.rds = redis_client
        self.local_node_id = local_node_id
        self.HINT_PREFIX = "hint:"
        self.logger = logging.getLogger(__name__)

    def _get_hint_key(self, target_node_id: str) -> str:
        return f"{self.HINT_PREFIX}{target_node_id}"

    def store_hint(self, target_node_id: str, key: str, value: Any, timestamp: float, original_request_id: str = None):
        """
        Stores a hint for a target node that is currently down.
        """
        hint_key = self._get_hint_key(target_node_id)
        
        hint_data = {
            "key": key,
            "value": value,
            "timestamp": timestamp,
            "original_request_id": original_request_id,
            "stored_at": time.time(),
            "handoff_node": self.local_node_id
        }
        
        try:
            # Store in a Redis List (Queue)
            # We serialize to JSON (or pickle if complex objects)
            # Using JSON for visibility, but pickle is used in worker.py for RPC
            serialized_hint = json.dumps(hint_data) 
            self.rds.rpush(hint_key, serialized_hint)
            self.logger.info(f"Stored hint for node {target_node_id}: key={key}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store hint for {target_node_id}: {e}")
            return False

    def has_hints(self, target_node_id: str) -> bool:
        """Check if we have hints for a specific node."""
        hint_key = self._get_hint_key(target_node_id)
        return self.rds.llen(hint_key) > 0

    def replay_hints(self, target_node_id: str, target_ip: str, target_port: int):
        """
        Replays stored hints to a recovered node.
        Should be called from a background thread when a node recovery is detected.
        """
        hint_key = self._get_hint_key(target_node_id)
        
        if not self.has_hints(target_node_id):
            return

        self.logger.info(f"Starting hinted handoff replay for {target_node_id} at {target_ip}:{target_port}")
        
        try:
            # Connect to the recovered node
            conn = rpyc.connect(target_ip, target_port, config={'sync_request_timeout': 5})
            
            # Process hints one by one (or in batches)
            while True:
                # Pop the oldest hint
                hint_json = self.rds.lpop(hint_key)
                if not hint_json:
                    break
                
                hint = json.loads(hint_json)
                key = hint['key']
                value = hint['value']
                timestamp = hint['timestamp']
                req_id = hint.get('original_request_id', 'handoff')
                
                try:
                    # Attempt to write to the recovered node
                    # Using exposed_replicated_put as it handles the write logic
                    # We might need a specific exposed_handoff_put if logic differs
                    res = conn.root.replicated_put(key, value, req_id, timestamp)
                    
                    if res['status'] != 0: # Assuming 0 is SUCCESS based on worker.py
                        self.logger.warning(f"Failed to replay hint for {key}, pushing back to queue.")
                        # If failed, push back to head of queue (or handle DLQ)
                        self.rds.lpush(hint_key, hint_json)
                        break # Stop replaying for now if connection seems flaky
                        
                except Exception as e:
                    self.logger.error(f"Error sending hint for {key}: {e}")
                    self.rds.lpush(hint_key, hint_json) # Return to queue
                    break

            conn.close()
            self.logger.info(f"Finished hinted handoff replay for {target_node_id}")

        except Exception as e:
            self.logger.error(f"Failed to connect to {target_node_id} for handoff: {e}")
