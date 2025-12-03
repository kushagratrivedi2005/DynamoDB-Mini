#!/usr/bin/env python3
"""
Generate accurate graphs for DynamoDB-MINI Gossip Protocol Report
Based on actual implementation in worker.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import networkx as nx
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import random

# Professional styling
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f8f9fa'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11

# DynamoDB colors
COLORS = {
    'primary': '#FF9900',
    'secondary': '#232F3E',
    'active': '#00A8E1',
    'down': '#EC7211',
    'success': '#1B9C85',
    'grid': '#e0e0e0'
}


def generate_gossip_protocol_diagram():
    """Generate diagram showing the gossip protocol flow"""
    print("Generating gossip protocol flow diagram...")
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'DynamoDB-MINI Gossip Protocol Flow', 
            ha='center', fontsize=18, fontweight='bold', color=COLORS['secondary'])
    
    # Step 1: Node Selection
    step1_y = 8
    ax.add_patch(FancyBboxPatch((0.5, step1_y), 4, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor=COLORS['primary'], 
                                edgecolor=COLORS['secondary'], linewidth=2))
    ax.text(2.5, step1_y + 0.4, 'Step 1: Random Peer Selection', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    ax.text(2.5, step1_y - 0.5, 'Each node picks random peer\nevery 3 seconds (GOSSIP_INTERVAL)', 
            ha='center', va='top', fontsize=9, style='italic')
    
    # Arrow
    ax.annotate('', xy=(2.5, step1_y - 0.8), xytext=(2.5, step1_y),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    # Step 2: Exchange Tables
    step2_y = 6.2
    ax.add_patch(FancyBboxPatch((0.5, step2_y), 4, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor=COLORS['active'], 
                                edgecolor=COLORS['secondary'], linewidth=2))
    ax.text(2.5, step2_y + 0.4, 'Step 2: Exchange Routing Tables', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    ax.text(2.5, step2_y - 0.5, 'Send: routing_table + down_routing_table\nReceive: gift_routing_table + gift_down_routing_table', 
            ha='center', va='top', fontsize=9, style='italic')
    
    # Arrow
    ax.annotate('', xy=(2.5, step2_y - 0.8), xytext=(2.5, step2_y),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    # Step 3: Version Comparison
    step3_y = 4.4
    ax.add_patch(FancyBboxPatch((0.5, step3_y), 4, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor=COLORS['success'], 
                                edgecolor=COLORS['secondary'], linewidth=2))
    ax.text(2.5, step3_y + 0.4, 'Step 3: Vector Clock Comparison', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    ax.text(2.5, step3_y - 0.5, 'Compare version_number for each node\nUpdate if peer has newer information', 
            ha='center', va='top', fontsize=9, style='italic')
    
    # Arrow
    ax.annotate('', xy=(2.5, step3_y - 0.8), xytext=(2.5, step3_y),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    # Step 4: Update & Ping
    step4_y = 2.6
    ax.add_patch(FancyBboxPatch((0.5, step4_y), 4, 0.8, 
                                boxstyle="round,pad=0.1", 
                                facecolor=COLORS['down'], 
                                edgecolor=COLORS['secondary'], linewidth=2))
    ax.text(2.5, step4_y + 0.4, 'Step 4: Update & Failure Detection', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    ax.text(2.5, step4_y - 0.5, 'Update local tables with newer entries\nPing unreachable nodes to verify status', 
            ha='center', va='top', fontsize=9, style='italic')
    
    # Right side: Example
    example_x = 5.5
    ax.text(7.5, 9, 'Example: Node A gossips with Node B', 
            ha='center', fontsize=13, fontweight='bold', color=COLORS['secondary'])
    
    # Node A
    ax.add_patch(Circle((6.5, 7.5), 0.4, facecolor=COLORS['primary'], 
                       edgecolor=COLORS['secondary'], linewidth=2))
    ax.text(6.5, 7.5, 'A', ha='center', va='center', fontsize=14, 
           fontweight='bold', color='white')
    ax.text(6.5, 6.8, 'Routing Table:\nNode C: v2\nNode D: v1', 
           ha='center', va='top', fontsize=8, bbox=dict(boxstyle='round', 
           facecolor='white', alpha=0.8))
    
    # Node B
    ax.add_patch(Circle((8.5, 7.5), 0.4, facecolor=COLORS['active'], 
                       edgecolor=COLORS['secondary'], linewidth=2))
    ax.text(8.5, 7.5, 'B', ha='center', va='center', fontsize=14, 
           fontweight='bold', color='white')
    ax.text(8.5, 6.8, 'Routing Table:\nNode C: v1\nNode D: v2', 
           ha='center', va='top', fontsize=8, bbox=dict(boxstyle='round', 
           facecolor='white', alpha=0.8))
    
    # Gossip arrow
    ax.annotate('', xy=(8.1, 7.5), xytext=(6.9, 7.5),
                arrowprops=dict(arrowstyle='<->', lw=3, color=COLORS['success']))
    ax.text(7.5, 7.8, 'Gossip', ha='center', fontsize=10, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='white', edgecolor=COLORS['success'], linewidth=2))
    
    # After gossip
    ax.text(7.5, 5.5, 'After Gossip:', ha='center', fontsize=11, fontweight='bold')
    ax.text(6.5, 5, 'Node A updates:\nNode D: v1→v2', ha='center', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='#e8f5e9', alpha=0.9))
    ax.text(8.5, 5, 'Node B updates:\nNode C: v1→v2', ha='center', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='#e8f5e9', alpha=0.9))
    
    # Config box
    config_text = 'Configuration (config.json):\n• GOSSIP_INTERVAL: 3s\n• N (Replication): 60\n• Nodes: 3 machines'
    ax.text(7.5, 1.5, config_text, ha='center', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff3e0', 
           edgecolor=COLORS['primary'], linewidth=2))
    
    plt.tight_layout()
    plt.savefig('gossip_protocol_diagram.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: gossip_protocol_diagram.png")
    plt.close()


def generate_routing_table_structure():
    """Generate diagram showing routing table structure"""
    print("Generating routing table structure...")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'Routing Table Structure in DynamoDB-MINI', 
            ha='center', fontsize=16, fontweight='bold', color=COLORS['secondary'])
    
    # Active Routing Table
    ax.text(2.5, 8.5, 'Active Routing Table', ha='center', fontsize=13, 
           fontweight='bold', color=COLORS['primary'])
    
    table_data = [
        ['Hash (end_of_range)', 'IP', 'Port', 'Version', 'Load', 'Start Range'],
        ['0x1a2b...', '10.2.136.226', '3100', '5', '0.23', '0x0f1a...'],
        ['0x4c5d...', '10.2.137.162', '3101', '3', '0.18', '0x1a2b...'],
        ['0x7e8f...', '10.2.133.235', '3102', '4', '0.31', '0x4c5d...'],
    ]
    
    y_pos = 7.5
    col_widths = [1.5, 1.2, 0.7, 0.8, 0.6, 1.2]
    x_start = 0.3
    
    for row_idx, row in enumerate(table_data):
        x_pos = x_start
        for col_idx, cell in enumerate(row):
            if row_idx == 0:
                color = COLORS['primary']
                text_color = 'white'
                weight = 'bold'
            else:
                color = 'white'
                text_color = COLORS['secondary']
                weight = 'normal'
            
            ax.add_patch(FancyBboxPatch((x_pos, y_pos - row_idx * 0.5), 
                                       col_widths[col_idx], 0.45,
                                       boxstyle="round,pad=0.02",
                                       facecolor=color,
                                       edgecolor=COLORS['secondary'], linewidth=1))
            ax.text(x_pos + col_widths[col_idx]/2, y_pos - row_idx * 0.5 + 0.225,
                   cell, ha='center', va='center', fontsize=8, 
                   color=text_color, fontweight=weight)
            x_pos += col_widths[col_idx] + 0.05
    
    # Down Routing Table
    ax.text(2.5, 5, 'Down Routing Table (Failed Nodes)', ha='center', 
           fontsize=13, fontweight='bold', color=COLORS['down'])
    
    down_table = [
        ['Hash', 'IP', 'Port', 'Version', 'Last Seen'],
        ['0x9fa0...', '10.2.137.162', '3105', '2', '23:15:42'],
    ]
    
    y_pos = 4
    for row_idx, row in enumerate(down_table):
        x_pos = x_start
        for col_idx, cell in enumerate(row):
            width = [1.2, 1.2, 0.7, 0.8, 1.0][col_idx]
            if row_idx == 0:
                color = COLORS['down']
                text_color = 'white'
                weight = 'bold'
            else:
                color = '#ffebee'
                text_color = COLORS['secondary']
                weight = 'normal'
            
            ax.add_patch(FancyBboxPatch((x_pos, y_pos - row_idx * 0.5), 
                                       width, 0.45,
                                       boxstyle="round,pad=0.02",
                                       facecolor=color,
                                       edgecolor=COLORS['down'], linewidth=1))
            ax.text(x_pos + width/2, y_pos - row_idx * 0.5 + 0.225,
                   cell, ha='center', va='center', fontsize=8,
                   color=text_color, fontweight=weight)
            x_pos += width + 0.05
    
    # Vector Clock explanation
    vc_text = '''Vector Clock (VectorClock class):
• Tracks version_number for each node
• Incremented on updates/failures
• Used to determine which info is newer
• Ensures eventual consistency'''
    
    ax.text(7.5, 6.5, vc_text, ha='center', va='top', fontsize=10,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#e3f2fd',
           edgecolor=COLORS['active'], linewidth=2))
    
    # Gossip operations
    ops_text = '''Key Operations:
1. serialize() - Convert to dict for RPC
2. deserialize() - Restore from dict
3. do_chit_chat() - Exchange tables
4. ping_thread() - Verify node status'''
    
    ax.text(7.5, 3.5, ops_text, ha='center', va='top', fontsize=10,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff3e0',
           edgecolor=COLORS['primary'], linewidth=2))
    
    plt.tight_layout()
    plt.savefig('routing_table_structure.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: routing_table_structure.png")
    plt.close()


def generate_failure_detection_flow():
    """Generate failure detection flowchart"""
    print("Generating failure detection flowchart...")
    
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(5, 11.5, 'Node Failure Detection & Recovery via Gossip', 
            ha='center', fontsize=16, fontweight='bold', color=COLORS['secondary'])
    
    def add_box(x, y, w, h, text, color, text_color='white'):
        ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                                   boxstyle="round,pad=0.1",
                                   facecolor=color,
                                   edgecolor=COLORS['secondary'], linewidth=2))
        ax.text(x, y, text, ha='center', va='center',
               fontsize=10, fontweight='bold', color=text_color)
    
    # Flow
    add_box(5, 10, 3, 0.6, 'Node A tries to gossip with Node B', COLORS['primary'])
    ax.annotate('', xy=(5, 9.5), xytext=(5, 9.7),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    add_box(5, 9, 3, 0.6, 'Connection fails (timeout)', COLORS['down'])
    ax.annotate('', xy=(5, 8.5), xytext=(5, 8.7),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    add_box(5, 8, 3.5, 0.6, 'Node A calls ping_thread(Node B)', COLORS['active'])
    ax.annotate('', xy=(5, 7.5), xytext=(5, 7.7),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    add_box(5, 7, 2.5, 0.6, 'Ping fails', '#ff5252')
    ax.annotate('', xy=(5, 6.5), xytext=(5, 6.7),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    add_box(5, 6, 4, 0.8, 'Move Node B from routing_table\nto down_routing_table', COLORS['down'])
    ax.annotate('', xy=(5, 5.3), xytext=(5, 5.6),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    add_box(5, 4.8, 3.5, 0.6, 'Increment version_number', COLORS['success'])
    ax.annotate('', xy=(5, 4.3), xytext=(5, 4.5),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    add_box(5, 3.8, 4, 0.8, 'Call handle_node_failure()\nUpdate ranges for next node', COLORS['primary'])
    ax.annotate('', xy=(5, 3.1), xytext=(5, 3.4),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    add_box(5, 2.6, 4.5, 0.8, 'Gossip spreads failure info\nto other nodes', COLORS['active'])
    
    # Recovery path
    ax.text(8.5, 6, 'Recovery Path', ha='center', fontsize=12, 
           fontweight='bold', color=COLORS['success'])
    add_box(8.5, 5.2, 2.5, 0.6, 'Node B recovers', COLORS['success'])
    ax.annotate('', xy=(8.5, 4.7), xytext=(8.5, 4.9),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    add_box(8.5, 4.2, 3, 0.8, 'Ping succeeds in\nthread_ping_down_node()', COLORS['success'])
    ax.annotate('', xy=(8.5, 3.5), xytext=(8.5, 3.8),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['secondary']))
    
    add_box(8.5, 3, 3.5, 0.8, 'Move back to routing_table\nCall handle_node_recovery()', COLORS['primary'])
    
    # Code reference
    code_text = '''Key Functions (worker.py):
• ping() - TCP socket ping
• ping_thread() - Verify node status
• thread_ping_down_node() - Periodic recovery check
• handle_node_failure() - Update ranges
• handle_node_recovery() - Restore ranges'''
    
    ax.text(5, 1, code_text, ha='center', va='top', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='#f5f5f5',
           edgecolor=COLORS['secondary'], linewidth=2))
    
    plt.tight_layout()
    plt.savefig('failure_detection_flow.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: failure_detection_flow.png")
    plt.close()


def generate_gossip_timeline():
    """Generate timeline showing gossip rounds"""
    print("Generating gossip timeline...")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Timeline data
    rounds = np.arange(0, 11)
    nodes = ['Node A', 'Node B', 'Node C', 'Node D']
    
    # Create timeline
    for i, node in enumerate(nodes):
        y = len(nodes) - i - 1
        ax.plot([0, 10], [y, y], 'k-', alpha=0.2, linewidth=1)
        ax.text(-0.5, y, node, ha='right', va='center', fontweight='bold', fontsize=11)
        
        # Gossip events
        if node == 'Node A':
            gossip_rounds = [1, 4, 7, 10]
            partners = ['B', 'C', 'D', 'B']
        elif node == 'Node B':
            gossip_rounds = [2, 5, 8]
            partners = ['C', 'D', 'A']
        elif node == 'Node C':
            gossip_rounds = [3, 6, 9]
            partners = ['D', 'A', 'B']
        else:
            gossip_rounds = [1, 4, 7]
            partners = ['A', 'B', 'C']
        
        for round_num, partner in zip(gossip_rounds, partners):
            ax.scatter(round_num, y, s=200, c=COLORS['primary'], 
                      edgecolors=COLORS['secondary'], linewidth=2, zorder=3)
            ax.text(round_num, y + 0.15, f'→{partner}', ha='center', va='bottom',
                   fontsize=8, fontweight='bold', color=COLORS['active'])
    
    # Failure event
    ax.axvline(x=5, color=COLORS['down'], linestyle='--', linewidth=2, alpha=0.7)
    ax.text(5, 4.2, 'Node D Fails', ha='center', fontsize=11, 
           fontweight='bold', color=COLORS['down'],
           bbox=dict(boxstyle='round', facecolor='white', edgecolor=COLORS['down'], linewidth=2))
    
    ax.set_xlabel('Time (Gossip Rounds, 3s interval)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Nodes', fontsize=12, fontweight='bold')
    ax.set_title('Gossip Protocol Timeline: Random Peer Selection & Information Spread', 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(-1, 11)
    ax.set_ylim(-0.5, len(nodes) - 0.5)
    ax.set_xticks(rounds)
    ax.set_xticklabels([f'{r*3}s' for r in rounds])
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('gossip_timeline.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: gossip_timeline.png")
    plt.close()


def generate_architecture_diagram():
    """Generate system architecture showing gossip integration"""
    print("Generating system architecture...")
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.7, 'DynamoDB-MINI Architecture: Gossip Protocol Integration', 
            ha='center', fontsize=16, fontweight='bold', color=COLORS['secondary'])
    
    # Worker nodes
    worker_positions = [(2, 7), (5, 7), (8, 7)]
    for idx, (x, y) in enumerate(worker_positions):
        # Worker box
        ax.add_patch(FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2,
                                   boxstyle="round,pad=0.1",
                                   facecolor=COLORS['active'],
                                   edgecolor=COLORS['secondary'], linewidth=2))
        ax.text(x, y + 0.3, f'Worker {idx+1}', ha='center', fontsize=11,
               fontweight='bold', color='white')
        ax.text(x, y, f'Port: 310{idx}', ha='center', fontsize=9, color='white')
        ax.text(x, y - 0.3, f'Redis: 637{idx}', ha='center', fontsize=9, color='white')
    
    # Gossip connections
    for i in range(len(worker_positions)):
        for j in range(i+1, len(worker_positions)):
            x1, y1 = worker_positions[i]
            x2, y2 = worker_positions[j]
            ax.plot([x1, x2], [y1-0.7, y2-0.7], '--', color=COLORS['primary'], 
                   linewidth=2, alpha=0.7)
    
    ax.text(5, 6, 'Gossip Protocol (3s interval)', ha='center', fontsize=10,
           fontweight='bold', color=COLORS['primary'])
    
    # Threads
    thread_y = 4.5
    threads = [
        ('start_gossip()', COLORS['primary']),
        ('sync_replica()', COLORS['success']),
        ('thread_ping_down_node()', COLORS['down'])
    ]
    
    ax.text(5, 5.2, 'Background Threads per Worker:', ha='center', 
           fontsize=12, fontweight='bold')
    
    for idx, (thread_name, color) in enumerate(threads):
        x = 2 + idx * 2.5
        ax.add_patch(FancyBboxPatch((x-0.9, thread_y-0.3), 1.8, 0.6,
                                   boxstyle="round,pad=0.05",
                                   facecolor=color,
                                   edgecolor=COLORS['secondary'], linewidth=1.5))
        ax.text(x, thread_y, thread_name, ha='center', va='center',
               fontsize=9, fontweight='bold', color='white')
    
    # Data structures
    ax.text(5, 3.5, 'Shared Data Structures:', ha='center', 
           fontsize=12, fontweight='bold')
    
    data_y = 2.8
    ax.add_patch(FancyBboxPatch((1.5, data_y-0.3), 2.5, 0.6,
                               boxstyle="round,pad=0.05",
                               facecolor='white',
                               edgecolor=COLORS['primary'], linewidth=2))
    ax.text(2.75, data_y, 'routing_table\n(Active Nodes)', ha='center', va='center',
           fontsize=9, color=COLORS['secondary'])
    
    ax.add_patch(FancyBboxPatch((6, data_y-0.3), 2.5, 0.6,
                               boxstyle="round,pad=0.05",
                               facecolor='white',
                               edgecolor=COLORS['down'], linewidth=2))
    ax.text(7.25, data_y, 'down_routing_table\n(Failed Nodes)', ha='center', va='center',
           fontsize=9, color=COLORS['secondary'])
    
    # Config
    config_text = '''Config (config.json):
• gossip: 3s
• ping_down_node: 2s
• replicate_sync: 5s
• N: 60, R: 40, W: 30'''
    
    ax.text(5, 1.2, config_text, ha='center', fontsize=9,
           bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff3e0',
           edgecolor=COLORS['primary'], linewidth=2))
    
    plt.tight_layout()
    plt.savefig('system_architecture.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: system_architecture.png")
    plt.close()


def main():
    """Generate all meaningful graphs for the report"""
    print("=" * 70)
    print("Generating DynamoDB-MINI Gossip Protocol Visualizations")
    print("Based on actual implementation in worker.py")
    print("=" * 70)
    print()
    
    generate_gossip_protocol_diagram()
    generate_routing_table_structure()
    generate_failure_detection_flow()
    generate_gossip_timeline()
    generate_architecture_diagram()
    
    print()
    print("=" * 70)
    print("✓ All visualizations generated successfully!")
    print("=" * 70)
    print("\nGenerated files (ready for your report):")
    print("  1. gossip_protocol_diagram.png - Complete protocol flow")
    print("  2. routing_table_structure.png - Data structure details")
    print("  3. failure_detection_flow.png - Failure handling flowchart")
    print("  4. gossip_timeline.png - Timeline of gossip rounds")
    print("  5. system_architecture.png - Overall system design")
    print("\nThese diagrams accurately represent your DynamoDB-MINI implementation!")


if __name__ == "__main__":
    main()
