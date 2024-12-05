import rpyc

# Replace with the target machine's hostname or IP address and port
hostname = "172.30.231.182"
SPAWN_WORKER_PORT = 4001

try:
    conn = rpyc.connect(hostname, SPAWN_WORKER_PORT)
    print("Connection established")
    # Perform remote procedure calls here
except Exception as e:
    print(f"Failed to connect: {e}")
