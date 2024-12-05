import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from collections import defaultdict
import time
from hashlib import md5
import bisect
import logging

class RingVisualization:
    def __init__(self, redis_client, hashmap_name):
        self.redis = redis_client
        self.hashmap = hashmap_name
        self.fig, self.ax = plt.subplots()
        self.lock = threading.Lock()
        self.node_counts = defaultdict(int)
        self.hash_function = lambda key: int(md5(str(key).encode("utf-8")).hexdigest(), 16)
        
    def update_counts(self):
        """Update the counts of keys per node"""
        with self.lock:
            # Reset counts
            self.node_counts.clear()
            
            # Get all keys from hashmap
            all_keys = self.redis.hkeys(self.hashmap)
            
            # For each key, determine which node holds it and increment counter
            for key in all_keys:
                node = self.get_responsible_node(key)  # You'll need to implement this
                self.node_counts[node] += 1
                
    def animate(self, frame):
        """Animation function for updating the pie chart"""
        self.ax.clear()
        with self.lock:
            labels = list(self.node_counts.keys())
            sizes = list(self.node_counts.values())
            
            if sizes:  # Only create pie if we have data
                self.ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                self.ax.set_title('Distribution of Keys Across Nodes')
        
    def start_visualization(self):
        """Start the visualization in a separate thread"""
        logging.log("Here in Replication")
        def update_loop():
            while True:
                self.update_counts()
                time.sleep(5)  # Update every 5 seconds
                
        # Start update thread
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        
        # Create animation
        anim = FuncAnimation(self.fig, self.animate, interval=5000)  # Update plot every 5 seconds
        logging.log("Here at end of visualisation")
        plt.show()

    def get_responsible_node(self, key):
        """
        Determine which node is responsible for a given key using consistent hashing logic
        Args:
            key: The key to find the responsible node for
        Returns:
            str: Hash of the responsible node
        """
        try:
            # Hash the key using MD5 (same as worker's hash function)
            key_hash = str(self.hash_function(key))
            
            # Get sorted list of node hashes
            nodes = sorted(self.redis.hkeys(self.hashmap))
            if not nodes:
                return None
                
            # Find the first node hash that's greater than or equal to key_hash
            idx = bisect(nodes, key_hash)
            if idx == len(nodes):
                # If key_hash is greater than all node hashes, wrap around to first node
                idx = 0
                
            # Return the responsible node's hash
            return nodes[idx]
            
        except Exception as e:
            logging.error(f"Error determining responsible node for key {key}: {e}")
            return None