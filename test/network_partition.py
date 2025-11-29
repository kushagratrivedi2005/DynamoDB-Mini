import logging 
import subprocess
import platform
import os

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
        print("Select target cluster:")
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
            
        semantic_vnodes = [3100, 3104, 3105]
        syntactic_vnodes = [3000, 3004, 3005]
        
        # Override ports for Localhost to match HashRing.py defaults (4 vnodes)
        if which_node == 3:
            # Semantic: 3100, 3101, 3102, 3103
            semantic_vnodes = [3100, 3101, 3102, 3103]
            # Syntactic: 3200, 3201, 3202, 3203 (HashRing spawns at 3200 for syntactic)
            syntactic_vnodes = [3200, 3201, 3202, 3203]
            
        vnodes = semantic_vnodes if which_task == 1 else syntactic_vnodes
        
        if which == 1:
            block_traffic(ip_address=ip, port_set=vnodes)
        elif which == 2:
            heal_firewall(ip_address=ip, port_set=vnodes)
    except ValueError:
        print("Invalid input. Please enter numbers.")
    except KeyboardInterrupt:
        print("\nExiting...")