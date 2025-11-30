#!/usr/bin/env python3
"""
Generic Network Control Interface for Secondary Nodes (Machine 2, 3, 4, ...)
Allows blocking/healing connections to Machine 1
"""

import subprocess
import sys
import platform
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import utils.config as config

def get_machine1_ip():
    """Get Machine 1 IP from config"""
    nodes = config.get_nodes()
    # Assume first node is Machine 1
    return nodes[0]['ip'], nodes[0]['hostname']

def get_current_machine_info():
    """Try to detect which machine we're on"""
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "unknown"
    return hostname, local_ip

def block_machine1():
    """Block incoming/outgoing traffic to Machine 1"""
    machine1_ip, machine1_name = get_machine1_ip()
    current_host, current_ip = get_current_machine_info()
    
    print(f"\n{'='*50}")
    print(f"BLOCK MACHINE 1")
    print(f"{'='*50}")
    print(f"Current machine: {current_host} ({current_ip})")
    print(f"Target: Machine 1 - {machine1_name} ({machine1_ip})")
    print(f"This will block all traffic between this machine and Machine 1")
    print(f"{'='*50}\n")
    
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    
    print("\nBlocking traffic from Machine 1...")
    
    # Get worker ports - block THIS machine's worker ports
    syntactic_start = config.get_port('syntactic_worker_start')
    semantic_start = config.get_port('semantic_worker_start')
    num_vnodes = config.get_quorum('N')
    
    # This machine's worker ports
    worker_ports = []
    worker_ports.extend([syntactic_start + i for i in range(num_vnodes)])
    worker_ports.extend([semantic_start + i for i in range(num_vnodes)])
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("Detected macOS. Using pfctl...")
        # Create rules
        anchor_rules = ""
        for port in worker_ports:
            # Block incoming from Machine 1
            anchor_rules += f"block drop quick proto tcp from {machine1_ip} to any port {port}\n"
            # Block outgoing to Machine 1 (responses)
            anchor_rules += f"block drop quick proto tcp from any port {port} to {machine1_ip}\n"
        
        try:
            # Ensure pfctl is enabled
            subprocess.run("sudo pfctl -e", shell=True, check=False, stderr=subprocess.DEVNULL)
            
            # Load rules into MAIN ruleset
            cmd = f"echo '{anchor_rules}' | sudo pfctl -f -"
            subprocess.run(cmd, shell=True, check=True)
            
            print(f"✅ Blocked Machine 1 ({machine1_ip}) using pfctl")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to partition network on macOS: {e}")
            return

    else:  # Linux (default to iptables)
        print("Detected Linux. Using iptables...")
        # Block Machine 1 from accessing this machine's workers
        for port in worker_ports:
            # Block incoming connections from Machine 1 to THIS machine's workers
            cmd_in = f"sudo iptables -I INPUT 1 -s {machine1_ip} -p tcp --dport {port} -j DROP"
            subprocess.run(cmd_in, shell=True, stderr=subprocess.DEVNULL)
            
            # Block outgoing responses from THIS machine's workers to Machine 1
            cmd_out = f"sudo iptables -I OUTPUT 1 -d {machine1_ip} -p tcp --sport {port} -j DROP"
            subprocess.run(cmd_out, shell=True, stderr=subprocess.DEVNULL)
        
        print(f"✅ Blocked Machine 1 ({machine1_ip}) using iptables")

    print(f"\nBlocked {len(worker_ports)} worker ports on THIS machine")
    print(f"Syntactic ports: {[syntactic_start + i for i in range(num_vnodes)]}")
    print(f"Semantic ports: {[semantic_start + i for i in range(num_vnodes)]}")
    
    if system == "Darwin":
        print("\nTo verify:")
        print("  sudo pfctl -s rules")
    else:
        print("\nTo verify:")
        print(f"  sudo iptables -L -n -v | grep {machine1_ip}")
    
    print("\nTo heal:")
    print("  Select option 2 in this menu")

def heal_network():
    """Remove all firewall rules"""
    machine1_ip, machine1_name = get_machine1_ip()
    system = platform.system()
    
    print(f"\n{'='*50}")
    print(f"HEAL NETWORK")
    print(f"{'='*50}")
    print(f"This will remove all firewall rules and restore connectivity")
    print(f"{'='*50}\n")
    
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    
    print("\nRemoving all firewall rules...")
    
    if system == "Darwin":  # macOS
        try:
            # Restore the default rules from /etc/pf.conf
            cmd = "sudo pfctl -f /etc/pf.conf"
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ Network partition healed on macOS (Restored /etc/pf.conf)")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to heal network on macOS: {e}")
            
    else:  # Linux (default to iptables)
        subprocess.run("sudo iptables -F", shell=True)
        subprocess.run("sudo iptables -X", shell=True)
        subprocess.run("sudo iptables -t nat -F", shell=True)
        subprocess.run("sudo iptables -t nat -X", shell=True)
        subprocess.run("sudo iptables -t mangle -F", shell=True)
        subprocess.run("sudo iptables -t mangle -X", shell=True)
        print(f"✅ All iptables rules removed")
    
    print(f"✅ Network connectivity restored with Machine 1")

def show_status():
    """Show current firewall rules"""
    machine1_ip, machine1_name = get_machine1_ip()
    current_host, current_ip = get_current_machine_info()
    system = platform.system()
    
    print(f"\n{'='*50}")
    print(f"NETWORK STATUS")
    print(f"{'='*50}")
    print(f"Current machine: {current_host} ({current_ip})")
    print(f"Machine 1: {machine1_name} ({machine1_ip})")
    print(f"{'='*50}\n")
    
    print("Active firewall rules:")
    
    if system == "Darwin":  # macOS
        result = subprocess.run(
            "sudo pfctl -s rules",
            shell=True,
            capture_output=True,
            text=True
        )
        # Check if our specific block rules exist
        if f"from {machine1_ip}" in result.stdout or f"to {machine1_ip}" in result.stdout:
             print(result.stdout)
             print("\n⚠ Traffic to Machine 1 is BLOCKED")
        else:
             print("No specific blocking rules found for Machine 1")
             print("\n✓ Traffic to Machine 1 is likely ALLOWED")
             
    else:  # Linux
        result = subprocess.run(
            f"sudo iptables -L -n -v | grep {machine1_ip} | head -20",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print(result.stdout)
            print("\n⚠ Traffic to Machine 1 is BLOCKED")
        else:
            print("No blocking rules found")
            print("\n✓ Traffic to Machine 1 is ALLOWED")

def main():
    """Main menu loop"""
    machine1_ip, machine1_name = get_machine1_ip()
    current_host, current_ip = get_current_machine_info()
    
    print(f"\n{'='*60}")
    print(f"  SECONDARY NODE - NETWORK CONTROL")
    print(f"{'='*60}")
    print(f"Current machine: {current_host} ({current_ip})")
    print(f"Machine 1: {machine1_name} ({machine1_ip})")
    print(f"{'='*60}\n")
    
    while True:
        print("\n" + "="*60)
        print("OPTIONS:")
        print("1. BLOCK Machine 1 (simulate network partition)")
        print("2. HEAL Network (restore connectivity)")
        print("3. Show Status (check current rules)")
        print("4. Exit")
        print("="*60)
        
        try:
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                block_machine1()
            elif choice == '2':
                heal_network()
            elif choice == '3':
                show_status()
            elif choice == '4':
                print("\nExiting...")
                break
            else:
                print("Invalid option. Please select 1-4.")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()