import logging 
import subprocess
import platform
import os

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import utils.config as config

logging.basicConfig(level=logging.DEBUG)

def block_traffic(ip_address, port_set) -> None:
    logging.debug(f'Network partition is called for ip: {ip_address} and ports= {port_set}')
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Create a temporary anchor file for pfctl
        # Create rules
        anchor_rules = ""
        for port in port_set:
            # Explicitly block on lo0 for Localhost traffic
            anchor_rules += f"block drop quick on lo0 inet proto tcp from any to any port {port}\n"
            anchor_rules += f"block drop quick on lo0 inet6 proto tcp from any to any port {port}\n"
            # Also block on any interface just in case
            anchor_rules += f"block drop quick proto tcp from any to any port {port}\n"
        
        # Apply rules using echo and pipe to pfctl
        # Note: This requires sudo access
        try:
            # Ensure pfctl is enabled
            subprocess.run("sudo pfctl -e", shell=True, check=False, stderr=subprocess.DEVNULL)
            
            # Load rules into MAIN ruleset
            cmd = f"echo '{anchor_rules}' | sudo pfctl -f -"
            logging.debug(f"Running macOS block command: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
            
            # Log the active rules to verify
            logging.debug("Active PF Rules:")
            subprocess.run("sudo pfctl -s rules", shell=True)
            
            logging.debug("Network partitioned on macOS using pfctl (Main Ruleset + lo0)")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to partition network on macOS: {e}")
            
    else:  # Linux (default to iptables)
        for port in port_set:
            isolate_command: str = \
            f'''sudo iptables -I INPUT 1 -s {ip_address} -p tcp --dport {port} -j DROP; 
            sudo iptables -I OUTPUT 1 -d {ip_address} -p tcp --dport {port} -j DROP;'''
            subprocess.run(args=[isolate_command], shell=True)
        logging.debug("Network is partitioned (Linux/iptables)...")

def heal_firewall(ip_address, port_set) -> None:
    logging.debug(f'Network heal is called for ip: {ip_address} and ports= {port_set}')
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Restore the default rules from /etc/pf.conf
        try:
            cmd = "sudo pfctl -f /etc/pf.conf"
            logging.debug(f"Running macOS heal command: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
            logging.debug("Network partition healed on macOS (Restored /etc/pf.conf)")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to heal network on macOS: {e}")
            
    else:  # Linux (default to iptables)
        for port in port_set:
            heal_command: str = \
            f'''sudo iptables -D INPUT -s {ip_address} -p tcp --dport {port} -j DROP; 
            sudo iptables -D OUTPUT -d {ip_address} -p tcp --dport {port} -j DROP;'''
            
            subprocess.run(args=[heal_command], shell=True)
        logging.debug("The network partition is healed (Linux/iptables)")


if __name__ == '__main__':
    logging.debug(f'1. Network partition')
    logging.debug(f'2. Heal partition')
    try:
        which = int(input('Which option ? '))
        print("\nSelect target cluster:")
        print("1. Sourav (10.237.27.95)")
        print("2. BaadalVM (10.17.50.254)")
        print("3. Localhost (127.0.0.1)")
        which_node = int(input('Which node cluster? '))
        
        which_task = int(input('Which task Semantic(1) and Syntactic(2) ? '))
        
        if which_node == 1:
            ip = '10.237.27.95'
        elif which_node == 2:
            ip = '10.17.50.254'
        elif which_node == 3:
            ip = '127.0.0.1'
        else:
            print("Invalid node selection. Defaulting to Localhost.")
            ip = '127.0.0.1'
            
        # Load ports from config
        semantic_start = config.get_port('semantic_worker_start')
        syntactic_start = config.get_port('syntactic_worker_start')
        num_vnodes = config.get_quorum('N')
        
        if which_node == 3: # Localhost
             # Generate ports based on config
             semantic_vnodes = [semantic_start + i for i in range(num_vnodes)]
             syntactic_vnodes = [syntactic_start + i for i in range(num_vnodes)]
        else:
             # Legacy/Remote nodes
             semantic_vnodes = [3100, 3104, 3105]
             syntactic_vnodes = [3000, 3004, 3005]
        
        all_vnodes = semantic_vnodes if which_task == 1 else syntactic_vnodes
        
        # Port selection menu
        print(f"\n=== Port Selection ===")
        print(f"Available ports: {all_vnodes}")
        print("\nChoose partition scenario:")
        print("1. Block ALL ports (complete network partition)")
        print("2. Block HALF (simulate 50% nodes down)")
        print("3. Block SPECIFIC ports (choose manually)")
        
        scenario = int(input('Select scenario: '))
        
        if scenario == 1:
            # Block all ports
            vnodes = all_vnodes
            print(f"Will block ALL {len(vnodes)} vnodes: {vnodes}")
        elif scenario == 2:
            # Block half
            half = len(all_vnodes) // 2
            vnodes = all_vnodes[:half]
            print(f"Will block HALF ({half} vnodes): {vnodes}")
            print(f"Remaining reachable: {all_vnodes[half:]}")
        elif scenario == 3:
            # Manual selection
            print(f"\nEnter port numbers to block (comma-separated)")
            print(f"Example: {all_vnodes[0]},{all_vnodes[1]}")
            port_input = input("Ports to block: ")
            vnodes = [int(p.strip()) for p in port_input.split(',')]
            remaining = [p for p in all_vnodes if p not in vnodes]
            print(f"Will block {len(vnodes)} vnodes: {vnodes}")
            print(f"Remaining reachable: {remaining}")
        else:
            print("Invalid scenario. Defaulting to block all.")
            vnodes = all_vnodes
        
        # Summary
        print(f"\n{'='*50}")
        print(f"Action: {'PARTITION' if which == 1 else 'HEAL'}")
        print(f"Target IP: {ip}")
        print(f"Ports affected: {vnodes}")
        print(f"{'='*50}\n")
        
        confirm = input("Proceed? (y/n): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            exit(0)
        
        if which == 1:
            block_traffic(ip_address=ip, port_set=vnodes)
        elif which == 2:
            heal_firewall(ip_address=ip, port_set=vnodes)
    except ValueError:
        logging.error(f'Invalid input!')
    except KeyboardInterrupt:
        logging.error(f'\\nCancelled by user!')