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

logging.basicConfig(level=logging.DEBUG)

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
    conn: rpyc.Connection = rpyc.connect(*url)
    conn._config['sync_request_timeout'] = None 
    res: dict = conn.root.allocate_nodes(count)
    logging.debug(msg=res)
    if res["status"] == -1:
        logging.debug(msg=f"Reached maximum limit of resources : left {res['output']}")
    

def test_client_put(key: str, value: int) -> None:
    url: tuple = ('localhost', config.get_port('client'))
    conn: rpyc.Connection = rpyc.connect(*url)
    logging.debug(msg=f"Syntactic put:: key: {key}")
    conn._config['sync_request_timeout'] = None 
    logging.debug(msg=f'PUT REQUEST: For {key} = {value}')
    res: str = conn.root.put(key, value)
    logging.debug(msg=f'PUT RESPONSE: {res}')

def test_client_get(key: str) -> None:
    url: tuple = ('localhost', config.get_port('client'))
    conn: rpyc.Connection = rpyc.connect(*url)
    conn._config['sync_request_timeout'] = None 
    logging.debug(msg=f'GET REQUEST : For {key}')
    res: int = conn.root.get(key)
    logging.debug(msg=f'GET REPONSE for key {key} = {res}')


def test_semantic_put(key: str) -> None:
    select_item: str = 'y'
    ''' talk to the client of semantic '''
    url: tuple = ('localhost', config.get_port('client'))
    conn: rpyc.Connection = rpyc.connect(*url)
    logging.debug(msg=f"Semantic put:: key: {key}")
    conn._config['sync_request_timeout'] = None 
    print("Options: Add(+), Remove(-), Append(a)")
    value: str = input('Select option: ')
    
    if value == '+':
        res: str = conn.root.put(key, 1)
        logging.debug(msg=f'PUT RESPONSE: {res}')
    elif value == '-':
        res: str = conn.root.put(key, -1)
        logging.debug(f'PUT RESPONSE: {res}')
    elif value == 'a':
        val_to_append = input("Enter string to append: ")
        # We need to implement exposed_append in client.py first
        try:
            res: str = conn.root.append(key, val_to_append)
            logging.debug(f'APPEND RESPONSE: {res}')
        except AttributeError:
            logging.error("Append not implemented in client yet")
    
        # test_semantic_get(key=key)
        

def test_semantic_get(key: str) -> None:
    url: tuple = ('localhost', config.get_port('client'))
    conn: rpyc.Connection = rpyc.connect(*url)
    conn._config['sync_request_timeout'] = None 
    logging.debug(msg=f'GET REQUEST : For {key}')
    res: int = conn.root.get(key)
    logging.debug(msg=f'GET REPONSE for key {key} = {res}')

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
    7. Network PARTITION
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
            print("Select target node:")
            print("1. Localhost")
            print("2. Other (Legacy)")
            select_ip = int(input('Which node? '))
            
            if select_ip == 1:
                target_ip = '127.0.0.1'
            else:
                # Legacy options
                node1_ip = '10.1.128.42'
                node2_ip = '172.30.231.182'
                legacy_choice = int(input('Which node manav(1)/pratham(2): '))
                target_ip = node1_ip if legacy_choice == 1 else node2_ip

            task_type = int(input("Sematic(1) or Syntactic(2) "))
            
            # For localhost, we need to use the specific ports we defined in network_partition.py
            if target_ip == '127.0.0.1':
                 # Semantic: 3100-3103, Syntactic: 3200-3203
                 ports = [3100, 3101, 3102, 3103] if task_type == 1 else [3200, 3201, 3202, 3203]
            else:
                 ports = semantic_ports if task_type == 1 else syntactic_ports
            
            block_traffic(target_ip, ports)
            
        elif option == 8:
            print("Select target node:")
            print("1. Localhost")
            print("2. Other (Legacy)")
            select_ip = int(input('Which node? '))
            
            if select_ip == 1:
                target_ip = '127.0.0.1'
            else:
                # Legacy options
                node1_ip = '10.1.128.42'
                node2_ip = '172.30.231.182'
                legacy_choice = int(input('Which node manav(1)/pratham(2): '))
                target_ip = node1_ip if legacy_choice == 1 else node2_ip

            task_type = int(input("Sematic(1) or Syntactic(2) "))
            
            if target_ip == '127.0.0.1':
                 ports = [3100, 3101, 3102, 3103] if task_type == 1 else [3200, 3201, 3202, 3203]
            else:
                 ports = semantic_ports if task_type == 1 else syntactic_ports
                 
            heal_firewall(target_ip, ports)       
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

