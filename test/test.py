import time 
import rpyc
import string
import logging 

from random import choice, randint
from network_partition import heal_firewall, block_traffic

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import utils.config as config

import os
# Ensure logs directory exists
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'test.log')),
        logging.StreamHandler()
    ]
)

def get_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    result_str: str = ''.join(choice(seq=letters) for i in range(length))
    return result_str 

def test_hashring() -> None:
    pass 

def test_spawn_wokers() -> None:
    count: int = int(input('Allocate how much nodes ? '))
    logging.debug(msg=f"Allocating {count} number of nodes on Hashring...")
    url: tuple = ('localhost', config.get_port('hash_ring'))
    try:
        # Allocating nodes takes longer because it spawns workers and builds the ring
        conn: rpyc.Connection = rpyc.connect(*url, config={'sync_request_timeout': 60})
        res: dict = conn.root.allocate_nodes(count)
        logging.debug(msg=res)
        if res["status"] == -1:
            logging.debug(msg=f"Reached maximum limit of resources : left {res['output']}")
    except Exception as e:
        logging.error(f"Failed to allocate nodes: {e}")
        return

def _test_with_timeout(operation_name, func):
    """Wrapper to handle timeouts for test operations"""
    try:
        return func()
    except Exception as e:
        if 'timed out' in str(e).lower() or 'timeout' in str(e).lower():
            logging.error(f"\n{'='*50}")
            logging.error(f"TIMEOUT: {operation_name} timed out!")
            logging.error(f"This usually means:")
            logging.error(f"1. Network partition is active (blocking traffic)")
            logging.error(f"2. Workers are not responding")
            logging.error(f"3. Quorum requirements cannot be met")
            logging.error(f"{'='*50}\n")
        else:
            logging.error(f"{operation_name} failed: {e}")
        return None

def test_client_put(key: str, value: int) -> None:
    def _put():
        url: tuple = ('localhost', config.get_port('client'))
        # Long timeout needed: TCP connection to blocked ports takes ~10-15s to timeout on macOS
        conn: rpyc.Connection = rpyc.connect(*url, config={'sync_request_timeout': 60})
        logging.debug(msg=f"Syntactic put:: key: {key}")
        logging.debug(msg=f'PUT REQUEST: For {key} = {value}')
        res: str = conn.root.put(key, value)
        logging.debug(msg=f'PUT RESPONSE: {res}')
        return res
    _test_with_timeout('Syntactic PUT', _put)

def test_client_get(key: str) -> None:
    def _get():
        url: tuple = ('localhost', config.get_port('client'))
        conn: rpyc.Connection = rpyc.connect(*url, config={'sync_request_timeout': 60})
        logging.debug(msg=f'GET REQUEST : For {key}')
        res: int = conn.root.get(key)
        logging.debug(msg=f'GET REPONSE for key {key} = {res}')
        return res
    _test_with_timeout('Syntactic GET', _get)
    

def test_semantic_put(key: str) -> None:
    def _semantic_put():
        url: tuple = ('localhost', config.get_port('client'))
        conn: rpyc.Connection = rpyc.connect(*url, config={'sync_request_timeout': 10})
        logging.debug(msg=f"Semantic put:: key: {key}")
        print("Options: Add(+), Remove(-), Append(a)")
        value: str = input('Select option: ')
        
        if value == '+':
            res: str = conn.root.put(key, 1)
            logging.debug(msg=f'PUT RESPONSE: {res}')
            return res
        elif value == '-':
            res: str = conn.root.put(key, -1)
            logging.debug(f'PUT RESPONSE: {res}')
            return res
        elif value == 'a':
            val_to_append = input("Enter string to append: ")
            try:
                res: str = conn.root.append(key, val_to_append)
                logging.debug(f'APPEND RESPONSE: {res}')
                return res
            except AttributeError:
                logging.error("Append not implemented in client yet")
                return None
    _test_with_timeout('Semantic PUT', _semantic_put)
        

def test_semantic_get(key: str) -> None:
    def _get():
        url: tuple = ('localhost', config.get_port('client'))
        conn: rpyc.Connection = rpyc.connect(*url, config={'sync_request_timeout': 10})
        logging.debug(msg=f'GET REQUEST : For {key}')
        res: int = conn.root.get(key)
        logging.debug(msg=f'GET REPONSE for key {key} = {res}')
        return res
    _test_with_timeout('Semantic GET', _get)

def test_workers() -> None:
    url: tuple = ('localhost', config.get_port('hash_ring'))
    conn: rpyc.Connection = rpyc.connect(*url).root
    res: str = conn.get()

# Load ports from config
semantic_start = config.get_port('semantic_worker_start')
syntactic_start = config.get_port('syntactic_worker_start')
# Assuming 4 vnodes as per config, but here we list them explicitly for partition testing
# Or we can generate them. For now, let's generate a few.
semantic_ports = [semantic_start + i for i in range(4)]
syntactic_ports = [syntactic_start + i for i in range(4)]

while True: 
    logging.debug (
    f'''\n
    =========================================
    Go with one of the option
    1. Testing hashring
    2. Test spawn workers
    3. Syntactic PUT
    4. Syntactic GET
    5. Semantic PUT
    6. Semantic GET
    -------------------
    7. Network PARTITION (local/single-machine only)
    8. Network HEAL
    =========================================
    ''')
    try:
        option: int = int(input('Which option ? '))
        if option == 1:
            test_hashring() #DONE
        elif option == 2: 
            test_spawn_wokers()
        elif option == 3:
            key: str = input("provide key: ") #get_random_string(5)
            logging.debug (f'Key is {key}')
            value: str = input("provide value: ")
            test_client_put(key, value)
        elif option == 4:
            key: str = input("provide key: ") #get_random_string(5)
            test_client_get(key)
        elif option == 5:
            hold_key: list = list()
            key = 'rqdgq'
            test_semantic_put(key)
            
        elif option == 6:
            key: str = 'rqdgq'
            test_semantic_get(key)
        elif option == 7:
            print("\n=== NETWORK PARTITION ===")
            print("\n⚠ NOTE: This is for LOCAL/SINGLE-MACHINE testing only!")
            print("For multi-machine setup, use Machine 2's Network Control terminal.\n")
            
            # For single machine, always use localhost
            target_ip = '127.0.0.1'
            print(f"Target: Localhost (127.0.0.1)")

            task_type = int(input("Semantic(1) or Syntactic(2): "))
            
            # Load ports from config
            semantic_start = config.get_port('semantic_worker_start')
            syntactic_start = config.get_port('syntactic_worker_start')
            num_vnodes = config.get_quorum('N')
            
            # Generate ports based on config
            semantic_vnodes = [semantic_start + i for i in range(num_vnodes)]
            syntactic_vnodes = [syntactic_start + i for i in range(num_vnodes)]
            
            all_vnodes = semantic_vnodes if task_type == 1 else syntactic_vnodes
            
            # Port selection menu
            print(f"\n=== Port Selection ===")
            print(f"Available ports: {all_vnodes}")
            print(f"\nQuorum settings: N={config.get_quorum('N')}, R={config.get_quorum('R')}, W={config.get_quorum('W')}")
            print("\nChoose partition scenario:")
            print("1. Block ALL ports (complete network partition)")
            print(f"2. Block HALF (block {num_vnodes//2} vnodes)")
            print("3. Block SPECIFIC ports (choose manually)")
            print(f"4. Block {num_vnodes-1} vnodes (only 1 reachable - test W/R failure)")
            
            scenario = int(input('Select scenario: '))
            
            if scenario == 1:
                vnodes = all_vnodes
                print(f"Will block ALL {len(vnodes)} vnodes: {vnodes}")
            elif scenario == 2:
                half = len(all_vnodes) // 2
                vnodes = all_vnodes[:half]
                print(f"Will block HALF ({half} vnodes): {vnodes}")
                print(f"Remaining reachable: {all_vnodes[half:]}")
                print(f"Expected: WRITE (W={config.get_quorum('W')}) should {'SUCCEED' if len(all_vnodes[half:]) >= config.get_quorum('W') else 'FAIL'}")
                print(f"Expected: READ (R={config.get_quorum('R')}) should {'SUCCEED' if len(all_vnodes[half:]) >= config.get_quorum('R') else 'FAIL'}")
            elif scenario == 3:
                print(f"\nEnter port numbers to block (comma-separated)")
                print(f"Example: {all_vnodes[0]},{all_vnodes[1]}")
                port_input = input("Ports to block: ")
                vnodes = [int(p.strip()) for p in port_input.split(',')]
                remaining = [p for p in all_vnodes if p not in vnodes]
                print(f"Will block {len(vnodes)} vnodes: {vnodes}")
                print(f"Remaining reachable: {remaining}")
                print(f"Expected: WRITE (W={config.get_quorum('W')}) should {'SUCCEED' if len(remaining) >= config.get_quorum('W') else 'FAIL'}")
                print(f"Expected: READ (R={config.get_quorum('R')}) should {'SUCCEED' if len(remaining) >= config.get_quorum('R') else 'FAIL'}")
            elif scenario == 4:
                vnodes = all_vnodes[:num_vnodes-1]
                print(f"Will block {len(vnodes)} vnodes: {vnodes}")
                print(f"Remaining reachable: {all_vnodes[num_vnodes-1:]}")
                print(f"Expected: Both WRITE and READ should FAIL (only 1 vnode < W={config.get_quorum('W')}, R={config.get_quorum('R')})")
            else:
                print("Invalid scenario. Defaulting to block all.")
                vnodes = all_vnodes
            
            print(f"\n{'='*50}")
            print(f"Action: PARTITION")
            print(f"Target IP: {target_ip}")
            print(f"Ports to block: {vnodes}")
            print(f"{'='*50}\n")
            
            confirm = input("Proceed? (y/n): ")
            if confirm.lower() == 'y':
                block_traffic(target_ip, vnodes)
                print("\n✅ Partition applied! Try PUT/GET operations now.")
            else:
                print("Cancelled.")
                
        elif option == 8:
            print("\n=== HEAL NETWORK ===")
            target_ip = '127.0.0.1'
            print(f"Target: Localhost (127.0.0.1)")
            select_ip = 1
            
            if select_ip == 1:
                target_ip = '127.0.0.1'
            else:
                node1_ip = '10.1.128.42'
                node2_ip = '172.30.231.182'
                legacy_choice = int(input('Which node manav(1)/pratham(2): '))
                target_ip = node1_ip if legacy_choice == 1 else node2_ip

            task_type = int(input("Semantic(1) or Syntactic(2): "))
            
            # Load ports from config
            semantic_start = config.get_port('semantic_worker_start')
            syntactic_start = config.get_port('syntactic_worker_start')
            num_vnodes = config.get_quorum('N')
            
            if target_ip == '127.0.0.1':
                semantic_vnodes = [semantic_start + i for i in range(num_vnodes)]
                syntactic_vnodes = [syntactic_start + i for i in range(num_vnodes)]
            else:
                semantic_vnodes = [3100, 3104, 3105]
                syntactic_vnodes = [3000, 3004, 3005]
            
            all_vnodes = semantic_vnodes if task_type == 1 else syntactic_vnodes
            
            print(f"\n{'='*50}")
            print(f"Action: HEAL")
            print(f"Target IP: {target_ip}")
            print(f"Will restore ALL ports: {all_vnodes}")
            print(f"{'='*50}\n")
            
            confirm = input("Proceed? (y/n): ")
            if confirm.lower() == 'y':
                heal_firewall(target_ip, all_vnodes)
                print("\n✅ Network healed! All vnodes should be reachable now.")
            else:
                print("Cancelled.")       
        elif option == 9:
            url: tuple = ('localhost', 6001)
            conn: rpyc.Connection = rpyc.connect(*url)
            logging.debug(msg=f"Getting all the active & down nodes for syntactic")
            conn._config['sync_request_timeout'] = None 
            res: str = conn.root.print_nodes_status()
            logging.debug(msg=f'PRINTING THE RESPONSE: {res}')  
        else:
            break
    except Exception as e: 
        logging.debug ('Bad options ', e)
        continue

