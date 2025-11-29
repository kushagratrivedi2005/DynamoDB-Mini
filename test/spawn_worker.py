import rpyc
import logging
from rpyc.utils.server import ThreadedServer 
from subprocess import call, Popen, run

import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
import utils.config as config

logging.basicConfig(level=logging.DEBUG)


class SpawnWorkers(rpyc.Service):
    def __init__(self):
        self.REDIS_PORT = config.get_port('redis')
        # Get absolute path to worker.py
        self.project_root = dirname(dirname(abspath(__file__)))
        self.worker_path = f"{self.project_root}/code/worker.py"
        
    def exposed_spawn_worker(self, port, vnodes, spawn_whom='syntactic'):
        logging.debug (f'SPAWN WORKER: Port {port}, vnodes = {vnodes}')
        logging.debug (f'Worker path: {self.worker_path}')
        # Always use the main worker.py file for both semantic and syntactic
        for i in range(0, vnodes):
            Popen(['python3', self.worker_path, str(port + i)])
        return "success"
    
 
if __name__ == "__main__":
    port = config.get_port('spawn_worker')
    logging.debug (f'SpawnWorker listening on all interfaces (0.0.0.0) at port {port}...')
    ThreadedServer(SpawnWorkers(), hostname='0.0.0.0', port=port).start()
