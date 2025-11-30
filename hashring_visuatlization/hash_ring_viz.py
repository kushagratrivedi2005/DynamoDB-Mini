#!/usr/bin/env python3
"""
Beautiful Hash Ring Visualization with Animation Support

This script creates stunning visualizations of the consistent hash ring showing:
- 3 physical machines with distinct vibrant colors
- 20 virtual nodes per machine (60 total)
- PUT/GET operations with animated transitions
- Node allocation and key distribution

Usage:
    python3 hash_ring_viz.py [--live] [--frames] [--all]
"""

import os
import re
import json
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from collections import defaultdict
from hashlib import md5
import numpy as np
from datetime import datetime
import argparse

# Beautiful color palette for the 3 physical machines
MACHINE_COLORS = {
    'localhost': '#9D4EDD',      # Vibrant Purple
    'machine2': '#06D6A0',       # Vibrant Cyan/Teal
    'machine3': '#FF6B6B',       # Vibrant Coral/Red
}

# Secondary colors for highlights
HIGHLIGHT_COLOR = '#FFD60A'      # Bright Yellow
KEY_COLOR = '#F72585'            # Hot Pink
BG_COLOR = '#0D1B2A'             # Dark Blue Background
TEXT_COLOR = '#E0E1DD'           # Light Gray Text

class HashRingVisualizer:
    def __init__(self, config_path='../config.json', log_dir='../logs'):
        self.config_path = config_path
        self.log_dir = log_dir
        self.hash_function = lambda key: int(md5(str(key).encode("utf-8")).hexdigest(), 16)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.nodes = self.config['nodes']
        self.quorum = self.config['quorum']
        
        # Node data structures
        self.virtual_nodes = {}  # hash -> (machine, vnode_id)
        self.physical_machines = {}  # machine_name -> [vnodes]
        self.keys_on_ring = {}  # key_hash -> key_name
        
        # Operation history
        self.operations = []
        
        # Output directory for frames
        self.frames_dir = 'frames'
        os.makedirs(self.frames_dir, exist_ok=True)
        
    def hash_vnode(self, machine_name, vnode_id):
        """Generate hash for a virtual node"""
        return self.hash_function(f'{machine_name}_{vnode_id}')
    
    def build_hash_ring(self):
        """Build the hash ring from configuration"""
        print("🔨 Building hash ring from configuration...")
        
        for node in self.nodes:
            machine_name = node['hostname']
            num_vnodes = node['vnodes']
            
            self.physical_machines[machine_name] = []
            
            for vnode_id in range(num_vnodes):
                vnode_hash = self.hash_vnode(machine_name, vnode_id)
                self.virtual_nodes[vnode_hash] = (machine_name, vnode_id)
                self.physical_machines[machine_name].append(vnode_hash)
        
        print(f"✓ Created {len(self.virtual_nodes)} virtual nodes across {len(self.physical_machines)} physical machines")
        for machine, vnodes in self.physical_machines.items():
            print(f"  - {machine}: {len(vnodes)} vnodes")
    
    def parse_quorum_log(self):
        """Parse quorum.log to extract operations"""
        log_path = os.path.join(self.log_dir, 'quorum.log')
        
        if not os.path.exists(log_path):
            print(f"⚠ Warning: {log_path} not found. Run operations first.")
            return
        
        print(f"📖 Parsing operations from {log_path}...")
        
        with open(log_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse PUT operations: [PUT] key=... value=... | nodes=['ip:port', ...]
                put_match = re.match(r'\[PUT\]\s+key=(\S+)\s+value=(\S+)\s+\|\s+nodes=', line)
                if put_match:
                    key, value = put_match.groups()
                    self.operations.append({
                        'type': 'PUT',
                        'key': key,
                        'value': value,
                        'timestamp': datetime.now().isoformat()
                    })
                    # Add key to ring
                    key_hash = self.hash_function(key)
                    self.keys_on_ring[key_hash] = key
                    continue
                
                # Parse GET operations: [GET] key=... | nodes=['ip:port', ...]
                get_match = re.match(r'\[GET\]\s+key=(\S+)\s+\|\s+nodes=', line)
                if get_match:
                    key = get_match.group(1)
                    self.operations.append({
                        'type': 'GET',
                        'key': key,
                        'timestamp': datetime.now().isoformat()
                    })
        
        print(f"✓ Parsed {len(self.operations)} operations ({len([op for op in self.operations if op['type'] == 'PUT'])} PUT, {len([op for op in self.operations if op['type'] == 'GET'])} GET)")
    
    def get_node_for_key(self, key_hash):
        """Find which node is responsible for a key"""
        sorted_nodes = sorted(self.virtual_nodes.keys())
        
        for node_hash in sorted_nodes:
            if key_hash <= node_hash:
                return node_hash
        
        # Wrap around to first node
        return sorted_nodes[0] if sorted_nodes else None
    
    def draw_hash_ring(self, fig, ax, current_operation=None, operation_index=0):
        """Draw beautiful hash ring visualization"""
        ax.clear()
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Set dark background
        fig.patch.set_facecolor(BG_COLOR)
        ax.set_facecolor(BG_COLOR)
        
        # Draw main ring circle
        ring_circle = plt.Circle((0, 0), 1.0, fill=False, color=TEXT_COLOR, 
                                linewidth=3, linestyle='--', alpha=0.3)
        ax.add_patch(ring_circle)
        
        # Draw title
        title = f"Distributed Hash Ring - {len(self.virtual_nodes)} Virtual Nodes"
        if current_operation:
            title += f"\nOperation {operation_index + 1}: {current_operation['type']} key={current_operation['key']}"
        ax.text(0, 1.35, title, ha='center', va='center', 
               fontsize=16, fontweight='bold', color=TEXT_COLOR)
        
        # Draw quorum info
        quorum_text = f"Quorum: N={self.quorum['N']}, R={self.quorum['R']}, W={self.quorum['W']}"
        ax.text(0, -1.35, quorum_text, ha='center', va='center',
               fontsize=11, color=TEXT_COLOR, alpha=0.7)
        
        # Sort nodes by hash for circular placement
        sorted_nodes = sorted(self.virtual_nodes.keys())
        total_nodes = len(sorted_nodes)
        
        if total_nodes == 0:
            ax.text(0, 0, "No nodes allocated", ha='center', va='center',
                   fontsize=14, color=TEXT_COLOR)
            return
        
        # Normalize hash values to angles (0 to 2π)
        max_hash = max(sorted_nodes)
        
        # Draw virtual nodes
        for i, node_hash in enumerate(sorted_nodes):
            machine_name, vnode_id = self.virtual_nodes[node_hash]
            
            # Calculate angle for this node
            angle = (node_hash / max_hash) * 2 * math.pi if max_hash > 0 else 0
            
            # Position on the ring
            x = math.cos(angle)
            y = math.sin(angle)
            
            # Get color for this machine
            color = MACHINE_COLORS.get(machine_name, '#FFFFFF')
            
            # Draw virtual node marker
            node_size = 200
            ax.scatter(x, y, s=node_size, c=color, alpha=0.8, 
                      edgecolors=TEXT_COLOR, linewidths=1.5, zorder=5)
            
            # Add vnode ID label
            label_x = x * 1.12
            label_y = y * 1.12
            ax.text(label_x, label_y, f"v{vnode_id}", ha='center', va='center',
                   fontsize=7, color=TEXT_COLOR, fontweight='bold', zorder=6)
        
        # Draw keys on the ring
        if current_operation and current_operation['type'] == 'PUT':
            key = current_operation['key']
            key_hash = self.hash_function(key)
            
            # Find responsible node
            responsible_node = self.get_node_for_key(key_hash)
            
            if responsible_node:
                # Calculate key position (slightly inside the ring)
                key_angle = (key_hash / max_hash) * 2 * math.pi if max_hash > 0 else 0
                key_x = math.cos(key_angle) * 0.85
                key_y = math.sin(key_angle) * 0.85
                
                # Draw key marker
                ax.scatter(key_x, key_y, s=300, c=KEY_COLOR, marker='*',
                          edgecolors=HIGHLIGHT_COLOR, linewidths=2, zorder=10)
                
                # Draw line from key to responsible node
                node_angle = (responsible_node / max_hash) * 2 * math.pi if max_hash > 0 else 0
                node_x = math.cos(node_angle)
                node_y = math.sin(node_angle)
                
                ax.plot([key_x, node_x], [key_y, node_y], 
                       color=HIGHLIGHT_COLOR, linewidth=2, alpha=0.6, 
                       linestyle='--', zorder=4)
                
                # Add key label
                ax.text(key_x, key_y - 0.15, key, ha='center', va='top',
                       fontsize=9, color=HIGHLIGHT_COLOR, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=BG_COLOR, 
                                edgecolor=HIGHLIGHT_COLOR, alpha=0.8), zorder=11)
        
        # Draw legend for physical machines
        legend_y = -1.15
        legend_x_start = -1.0
        spacing = 0.7
        
        for i, (machine, color) in enumerate(MACHINE_COLORS.items()):
            x_pos = legend_x_start + i * spacing
            
            # Draw colored circle
            ax.scatter(x_pos, legend_y, s=100, c=color, alpha=0.8,
                      edgecolors=TEXT_COLOR, linewidths=1)
            
            # Add machine label
            ax.text(x_pos + 0.08, legend_y, machine, ha='left', va='center',
                   fontsize=9, color=TEXT_COLOR, fontweight='bold')
    
    def generate_static_visualization(self, output_path='hash_ring.png'):
        """Generate a static visualization of the hash ring"""
        print(f"🎨 Generating static visualization...")
        
        fig, ax = plt.subplots(figsize=(14, 14), dpi=100)
        self.draw_hash_ring(fig, ax)
        
        plt.tight_layout()
        plt.savefig(output_path, facecolor=BG_COLOR, dpi=150)
        plt.close()
        
        print(f"✓ Saved to {output_path}")
    
    def generate_operation_frames(self):
        """Generate frames for each operation"""
        print(f"🎬 Generating {len(self.operations)} operation frames...")
        
        for i, operation in enumerate(self.operations):
            fig, ax = plt.subplots(figsize=(14, 14), dpi=100)
            self.draw_hash_ring(fig, ax, operation, i)
            
            frame_path = os.path.join(self.frames_dir, f'frame_{i:04d}.png')
            plt.tight_layout()
            plt.savefig(frame_path, facecolor=BG_COLOR, dpi=100)
            plt.close()
            
            if (i + 1) % 20 == 0:
                print(f"  Generated {i + 1}/{len(self.operations)} frames...")
        
        print(f"✓ All frames saved to {self.frames_dir}/")
    
    def run(self, mode='static'):
        """Run visualization based on mode"""
        self.build_hash_ring()
        
        if mode in ['frames', 'all']:
            self.parse_quorum_log()
            self.generate_operation_frames()
        
        if mode in ['static', 'all']:
            self.generate_static_visualization()
        
        print("✅ Visualization complete!")


def main():
    parser = argparse.ArgumentParser(description='Hash Ring Visualization')
    parser.add_argument('--live', action='store_true', 
                       help='Show live visualization window')
    parser.add_argument('--frames', action='store_true',
                       help='Generate frames for animation')
    parser.add_argument('--all', action='store_true',
                       help='Generate both static and frames')
    
    args = parser.parse_args()
    
    # Determine mode
    if args.all:
        mode = 'all'
    elif args.frames:
        mode = 'frames'
    else:
        mode = 'static'
    
    viz = HashRingVisualizer()
    viz.run(mode=mode)


if __name__ == '__main__':
    main()
