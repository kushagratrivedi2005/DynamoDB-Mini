#!/usr/bin/env python3
"""
Network Control Interface for Machine 2
Allows blocking/healing connections to Machine 1
"""

import subprocess
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import utils.config as config

def get_machine1_ip():
    """Get Machine 1 IP from config"""
    nodes = config.get_nodes()
    # Assume first node is Machine 1
    return nodes[0]['ip'], nodes[0]['hostname']

def block_machine1():
    """Block incoming/outgoing traffic to Machine 1"""
    machine1_ip, machine1_name = get_machine1_ip()
    
    print(f"\n{'='*50}")
    print(f"BLOCK MACHINE 1")
    print(f"{'='*50}")
    print(f"Machine 1: {machine1_name} ({machine1_ip})")
    print(f"This will block all traffic between this machine and Machine 1")
    print(f"{'='*50}\n")
    
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    
    print("\nBlocking traffic to Machine 1...")
    
    # Get worker ports
    syntactic_start = config.get_port('syntactic_worker_start')
    semantic_start = config.get_port('semantic_worker_start')
    num_vnodes = config.get_quorum('N')
    
    all_ports = []
    all_ports.extend([syntactic_start + i for i in range(num_vnodes)])
    all_ports.extend([semantic_start + i for i in range(num_vnodes)])
    
    # Also block coordinator ports
    all_ports.append(config.get_port('hash_ring'))  # 3000
    all_ports.append(config.get_port('client'))      # 6001
    
    for port in all_ports:
        # Block incoming from Machine 1
        cmd_in = f"sudo iptables -I INPUT 1 -s {machine1_ip} -p tcp --sport {port} -j DROP"
        subprocess.run(cmd_in, shell=True, stderr=subprocess.DEVNULL)
        
        # Block outgoing to Machine 1
        cmd_out = f"sudo iptables -I OUTPUT 1 -d {machine1_ip} -p tcp --dport {port} -j DROP"
        subprocess.run(cmd_out, shell=True, stderr=subprocess.DEVNULL)
    
    print(f"✅ Blocked all traffic to/from Machine 1 ({machine1_ip})")
    print(f"\nBlocked {len(all_ports)} ports")
    print("\nTo verify:")
    print(f"  sudo iptables -L -n -v | grep {machine1_ip}")
    print("\nTo heal:")
    print("  Select option 2 in this menu")

def heal_network():
    """Remove all iptables rules"""
    machine1_ip, machine1_name = get_machine1_ip()
    
    print(f"\n{'='*50}")
    print(f"HEAL NETWORK")
    print(f"{'='*50}")
    print(f"This will remove all iptables rules and restore connectivity")
    print(f"{'='*50}\n")
    
    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    
    print("\nRemoving all iptables rules...")
    
    subprocess.run("sudo iptables -F", shell=True)
    subprocess.run("sudo iptables -X", shell=True)
    subprocess.run("sudo iptables -t nat -F", shell=True)
    subprocess.run("sudo iptables -t nat -X", shell=True)
    subprocess.run("sudo iptables -t mangle -F", shell=True)
    subprocess.run("sudo iptables -t mangle -X", shell=True)
    
    print(f"✅ All iptables rules removed")
    print(f"✅ Network connectivity restored with Machine 1")

def show_status():
    """Show current iptables rules"""
    machine1_ip, machine1_name = get_machine1_ip()
    
    print(f"\n{'='*50}")
    print(f"NETWORK STATUS")
    print(f"{'='*50}")
    print(f"Machine 1: {machine1_name} ({machine1_ip})")
    print(f"{'='*50}\n")
    
    print("Active iptables rules related to Machine 1:")
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
    
    print(f"\nTo see all rules:")
    print(f"  sudo iptables -L -n -v")

def main():
    """Main menu loop"""
    machine1_ip, machine1_name = get_machine1_ip()
    
    print(f"\n{'='*60}")
    print(f"  MACHINE 2 - NETWORK CONTROL")
    print(f"{'='*60}")
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
