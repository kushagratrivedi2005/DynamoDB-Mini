import rpyc
import logging
from rpyc.utils.server import ThreadedServer 
from subprocess import call, Popen, run

logging.basicConfig(level=logging.DEBUG)


class SpawnWorkers(rpyc.Service):
    def __init__(self):
        self.REDIS_PORT = 6379
    def exposed_spawn_worker(self, port, vnodes, spawn_whom='syntactic'):
        logging.debug (f'SPAWN WORKER: Port {port}, vnodes = {vnodes}')
        # Always use the main worker.py file for both semantic and syntactic
        for i in range(0, vnodes):
            Popen(['python3', '../code/worker.py', str(port + i)])
        return "success"
    
 
if __name__ == "__main__":
    port = 4001
    logging.debug (f'Listening at port 4001...')
    ThreadedServer(SpawnWorkers(), hostname='0.0.0.0', port=port).start()
