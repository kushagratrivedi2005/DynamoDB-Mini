#!/usr/bin/env python3
"""
Hash Ring Node Join/Leave Simulation

Simulates machines joining and leaving a consistent hash ring at different scales.
Creates beautiful animated visualizations without needing to run the actual system.

Scales:
- 10 nodes per machine
- 100 nodes per machine  
- 1000 nodes per machine
- 10000 nodes per machine

Usage:
    python3 simulate_ring_dynamics.py --nodes 10 --duration 10
"""

import os
import math
import random
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from hashlib import md5
from collections import defaultdict

# Beautiful color palette for machines
MACHINE_COLORS = [
    '#9D4EDD',  # Vibrant Purple
    '#06D6A0',  # Vibrant Cyan/Teal
    '#FF6B6B',  # Vibrant Coral/Red
    '#FFD60A',  # Bright Yellow
    '#F72585',  # Hot Pink
    '#4CC9F0',  # Sky Blue
    '#7209B7',  # Deep Purple
    '#06FFA5',  # Mint Green
]

BG_COLOR = '#0D1B2A'      # Dark Blue Background
TEXT_COLOR = '#E0E1DD'    # Light Gray Text
RING_COLOR = '#E0E1DD'    # Ring outline

class HashRingSimulator:
    def __init__(self, nodes_per_machine=10, max_machines=3):
        self.nodes_per_machine = nodes_per_machine
        self.max_machines = max_machines
        self.hash_function = lambda key: int(md5(str(key).encode("utf-8")).hexdigest(), 16)
        
        # Ring state
        self.machines = {}  # machine_id -> {color, vnodes: {hash -> vnode_id}}
        self.next_machine_id = 0
        
        # Event log
        self.events = []
        
    def add_machine(self):
        """Add a new machine to the ring"""
        if len(self.machines) >= self.max_machines:
            return None
            
        machine_id = self.next_machine_id
        self.next_machine_id += 1
        
        color = MACHINE_COLORS[machine_id % len(MACHINE_COLORS)]
        vnodes = {}
        
        # Create virtual nodes for this machine
        for vnode_id in range(self.nodes_per_machine):
            vnode_hash = self.hash_function(f'machine{machine_id}_vnode{vnode_id}')
            vnodes[vnode_hash] = vnode_id
        
        self.machines[machine_id] = {
            'color': color,
            'vnodes': vnodes,
            'name': f'M{machine_id}'
        }
        
        return machine_id
    
    def remove_machine(self, machine_id):
        """Remove a machine from the ring"""
        if machine_id in self.machines:
            del self.machines[machine_id]
            return True
        return False
    
    def generate_random_walk(self, num_events=20, seed=42):
        """Generate a random walk of join/leave events with exactly 4 machines"""
        random.seed(seed)
        
        # Start with Machine 0
        machine_0 = self.add_machine()
        self.events.append({
            'type': 'join',
            'machine_id': machine_0,
            'description': f'Machine {machine_0} joins'
        })
        
        active_machines = [machine_0]
        all_machine_ids = [0, 1, 2, 3]  # Exactly 4 machines
        
        for i in range(num_events - 1):
            # Get inactive machines
            inactive_machines = [m for m in all_machine_ids if m not in active_machines]
            
            # Decide: join or leave?
            can_join = len(inactive_machines) > 0
            can_leave = len(active_machines) > 1
            
            if can_join and can_leave:
                action = random.choice(['join', 'leave'])
            elif can_join:
                action = 'join'
            elif can_leave:
                action = 'leave'
            else:
                break
            
            if action == 'join':
                # Join a specific inactive machine
                machine_id = inactive_machines[0]
                
                # Manually add this specific machine
                color = MACHINE_COLORS[machine_id % len(MACHINE_COLORS)]
                vnodes = {}
                for vnode_id in range(self.nodes_per_machine):
                    vnode_hash = self.hash_function(f'machine{machine_id}_vnode{vnode_id}')
                    vnodes[vnode_hash] = vnode_id
                
                self.machines[machine_id] = {
                    'color': color,
                    'vnodes': vnodes,
                    'name': f'M{machine_id}'
                }
                
                active_machines.append(machine_id)
                self.events.append({
                    'type': 'join',
                    'machine_id': machine_id,
                    'description': f'Machine {machine_id} joins'
                })
            else:  # leave
                machine_id = random.choice(active_machines)
                if self.remove_machine(machine_id):
                    active_machines.remove(machine_id)
                    self.events.append({
                        'type': 'leave',
                        'machine_id': machine_id,
                        'description': f'Machine {machine_id} leaves'
                    })
    
    def get_ring_state_at_event(self, event_idx):
        """Get the state of the ring at a specific event"""
        # Reset and replay events up to event_idx
        temp_machines = {}
        temp_next_id = 0
        
        for i in range(event_idx + 1):
            event = self.events[i]
            
            if event['type'] == 'join':
                machine_id = event['machine_id']
                color = MACHINE_COLORS[machine_id % len(MACHINE_COLORS)]
                vnodes = {}
                
                for vnode_id in range(self.nodes_per_machine):
                    vnode_hash = self.hash_function(f'machine{machine_id}_vnode{vnode_id}')
                    vnodes[vnode_hash] = vnode_id
                
                temp_machines[machine_id] = {
                    'color': color,
                    'vnodes': vnodes,
                    'name': f'M{machine_id}'
                }
            else:  # leave
                machine_id = event['machine_id']
                if machine_id in temp_machines:
                    del temp_machines[machine_id]
        
        return temp_machines
    
    def draw_ring_state(self, ax, machines, event_description='', total_nodes=0):
        """Draw the hash ring for a given machine state"""
        ax.clear()
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Set dark background
        ax.set_facecolor(BG_COLOR)
        
        # Draw main ring circle
        ring_circle = plt.Circle((0, 0), 1.0, fill=False, color=RING_COLOR, 
                                linewidth=3, linestyle='--', alpha=0.3)
        ax.add_patch(ring_circle)
        
        # Title with node count
        title = f"Consistent Hash Ring - {total_nodes} Virtual Nodes\n{event_description}"
        ax.text(0, 1.35, title, ha='center', va='center', 
               fontsize=14, fontweight='bold', color=TEXT_COLOR)
        
        # Get all virtual nodes
        all_vnodes = []
        for machine_id, machine_data in machines.items():
            for vnode_hash, vnode_id in machine_data['vnodes'].items():
                all_vnodes.append((vnode_hash, machine_id, vnode_id, machine_data['color']))
        
        if not all_vnodes:
            ax.text(0, 0, "Empty Ring", ha='center', va='center',
                   fontsize=14, color=TEXT_COLOR)
            return
        
        # Sort by hash
        all_vnodes.sort(key=lambda x: x[0])
        max_hash = max(v[0] for v in all_vnodes) if all_vnodes else 1
        
        # Draw virtual nodes
        for vnode_hash, machine_id, vnode_id, color in all_vnodes:
            # Calculate angle
            angle = (vnode_hash / max_hash) * 2 * math.pi if max_hash > 0 else 0
            
            # Position on the ring
            x = math.cos(angle)
            y = math.sin(angle)
            
            # Node size based on scale
            if total_nodes <= 30:
                node_size = 200
                show_labels = True
            elif total_nodes <= 300:
                node_size = 100
                show_labels = False
            elif total_nodes <= 3000:
                node_size = 30
                show_labels = False
            else:
                node_size = 10
                show_labels = False
            
            # Draw virtual node
            ax.scatter(x, y, s=node_size, c=color, alpha=0.8, 
                      edgecolors=TEXT_COLOR, linewidths=1.5 if total_nodes <= 300 else 0.5, 
                      zorder=5)
            
            # Add labels for small rings
            if show_labels:
                label_x = x * 1.12
                label_y = y * 1.12
                ax.text(label_x, label_y, f"v{vnode_id}", ha='center', va='center',
                       fontsize=7, color=TEXT_COLOR, fontweight='bold', zorder=6)
        
        # Draw legend
        legend_y = -1.25
        legend_items = list(machines.items())
        num_machines = len(legend_items)
        
        if num_machines > 0:
            total_width = min(2.0, num_machines * 0.5)
            spacing = total_width / num_machines if num_machines > 1 else 0
            start_x = -total_width / 2
            
            for idx, (machine_id, machine_data) in enumerate(legend_items):
                x_pos = start_x + idx * spacing + spacing / 2
                
                # Draw colored circle
                ax.scatter(x_pos, legend_y, s=100, c=machine_data['color'], alpha=0.8,
                          edgecolors=TEXT_COLOR, linewidths=1)
                
                # Add machine label
                label = f"{machine_data['name']} ({self.nodes_per_machine} vnodes)"
                ax.text(x_pos, legend_y - 0.12, label, ha='center', va='top',
                       fontsize=8, color=TEXT_COLOR, fontweight='bold')
    
    def generate_frames(self, output_dir='simulation_frames', fps=10, duration=10):
        """Generate animation frames for all events"""
        os.makedirs(output_dir, exist_ok=True)
        
        total_frames = int(fps * duration)
        events_count = len(self.events)
        
        print(f"🎬 Generating {total_frames} frames for {events_count} events...")
        print(f"   Duration: {duration}s @ {fps} FPS")
        
        frames_per_event = total_frames // events_count if events_count > 0 else total_frames
        
        frame_idx = 0
        for event_idx, event in enumerate(self.events):
            # Get ring state at this event
            machines = self.get_ring_state_at_event(event_idx)
            total_nodes = sum(len(m['vnodes']) for m in machines.values())
            
            # Generate multiple frames for this event
            for _ in range(frames_per_event):
                fig, ax = plt.subplots(figsize=(12, 12), dpi=100)
                fig.patch.set_facecolor(BG_COLOR)
                
                self.draw_ring_state(ax, machines, event['description'], total_nodes)
                
                frame_path = os.path.join(output_dir, f'frame_{frame_idx:04d}.png')
                plt.tight_layout()
                plt.savefig(frame_path, facecolor=BG_COLOR, dpi=100)
                plt.close()
                
                frame_idx += 1
                
                if frame_idx % 20 == 0:
                    print(f"   Generated {frame_idx}/{total_frames} frames...")
        
        # Fill remaining frames with final state
        if frame_idx < total_frames:
            machines = self.get_ring_state_at_event(len(self.events) - 1)
            total_nodes = sum(len(m['vnodes']) for m in machines.values())
            
            for _ in range(total_frames - frame_idx):
                fig, ax = plt.subplots(figsize=(12, 12), dpi=100)
                fig.patch.set_facecolor(BG_COLOR)
                
                self.draw_ring_state(ax, machines, "Final State", total_nodes)
                
                frame_path = os.path.join(output_dir, f'frame_{frame_idx:04d}.png')
                plt.tight_layout()
                plt.savefig(frame_path, facecolor=BG_COLOR, dpi=100)
                plt.close()
                
                frame_idx += 1
        
        print(f"✅ Generated {frame_idx} frames in {output_dir}/")
        return frame_idx


def main():
    parser = argparse.ArgumentParser(description='Simulate hash ring node dynamics')
    parser.add_argument('--nodes', type=int, default=10,
                       help='Number of virtual nodes per machine (10, 100, 1000, or 10000)')
    parser.add_argument('--machines', type=int, default=3,
                       help='Maximum number of machines (default: 3)')
    parser.add_argument('--events', type=int, default=20,
                       help='Number of join/leave events (default: 20)')
    parser.add_argument('--duration', type=int, default=10,
                       help='Animation duration in seconds (default: 10)')
    parser.add_argument('--fps', type=int, default=10,
                       help='Frames per second (default: 10)')
    parser.add_argument('--output', default='simulation_frames',
                       help='Output directory for frames')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"  HASH RING SIMULATION")
    print(f"  {args.nodes} nodes/machine | {args.machines} max machines")
    print("=" * 60)
    print()
    
    # Create simulator
    sim = HashRingSimulator(nodes_per_machine=args.nodes, max_machines=args.machines)
    
    # Generate random walk
    print(f"🎲 Generating random walk with {args.events} events...")
    sim.generate_random_walk(num_events=args.events)
    print(f"✓ Created {len(sim.events)} events")
    print()
    
    # Show event summary
    print("Events:")
    for i, event in enumerate(sim.events[:10]):  # Show first 10
        print(f"  {i+1}. {event['description']}")
    if len(sim.events) > 10:
        print(f"  ... and {len(sim.events) - 10} more events")
    print()
    
    # Generate frames
    output_dir = f"{args.output}_{args.nodes}nodes"
    frames = sim.generate_frames(output_dir=output_dir, fps=args.fps, duration=args.duration)
    
    print()
    print("✅ Simulation complete!")
    print(f"   Frames saved to: {output_dir}/")
    print()
    print("Next steps:")
    print(f"  1. Create animation:")
    print(f"     python3 generate_animation.py --frames-dir {output_dir} --output simulation_{args.nodes}nodes --fps {args.fps}")
    print()


if __name__ == '__main__':
    main()
