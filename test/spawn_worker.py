import rpyc
import logging
from rpyc.utils.server import ThreadedServer 
from subprocess import call, Popen, run

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
        logging.FileHandler(os.path.join(log_dir, 'spawn_worker.log')),
        logging.StreamHandler()
    ]
)


class SpawnWorkers(rpyc.Service):
    def __init__(self):
        self.REDIS_PORT = config.get_port('redis')
        # Get absolute path to worker.py
        self.project_root = dirname(dirname(abspath(__file__)))
        self.worker_path = f"{self.project_root}/code/worker.py"
        
    def exposed_spawn_worker(self, port, vnodes, spawn_whom='syntactic'):
        import os
        logging.debug (f'SPAWN WORKER: Port {port}, vnodes = {vnodes}')
        logging.debug (f'Worker path: {self.worker_path}')
        
        # Create logs directory if it doesn't exist
        logs_dir = f'{self.project_root}/logs'
        os.makedirs(logs_dir, exist_ok=True)
        
        # Always use the main worker.py file for both semantic and syntactic
        for i in range(0, vnodes):
            worker_port = port + i
            log_file = f'{logs_dir}/worker_{worker_port}.log'
            with open(log_file, 'w') as log:
                Popen(['python3', self.worker_path, str(worker_port)], 
                      stdout=log, stderr=log)
            logging.debug(f'Started worker on port {worker_port}, logs: {log_file}')
        return "success"
    
 
if __name__ == "__main__":
    port = config.get_port('spawn_worker')
    logging.debug (f'SpawnWorker listening on all interfaces (0.0.0.0) at port {port}...')
    ThreadedServer(SpawnWorkers(), hostname='0.0.0.0', port=port).start()
