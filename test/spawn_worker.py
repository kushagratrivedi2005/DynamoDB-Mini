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
    def exposed_spawn_worker(self, port, vnodes, spawn_whom='syntactic'):
        logging.debug (f'SPAWN WORKER: Port {port}, vnodes = {vnodes}')
        # Always use the main worker.py file for both semantic and syntactic
        for i in range(0, vnodes):
            Popen(['python3', '../code/worker.py', str(port + i)])
        return "success"
    
 
if __name__ == "__main__":
    port = config.get_port('spawn_worker')
    logging.debug (f'Listening at port 4001...')
    ThreadedServer(SpawnWorkers(), hostname='0.0.0.0', port=port).start()
