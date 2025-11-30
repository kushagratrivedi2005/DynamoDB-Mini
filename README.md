# **DynamoDB-MINI**

A distributed key-value store inspired by Amazon DynamoDB. This project focuses on providing **scalability**, **fault tolerance**, **high availability**, and **eventual consistency** through techniques such as **consistent hashing**, **vector clocks**, **quorum-based replication**, **hinted handoff**, and **Merkle trees** for anti-entropy.

## **Features**
- **Decentralized Architecture**: Peer-to-peer communication with no single point of failure
- **Consistent Hashing**: Dynamic load balancing with virtual nodes
- **Replication and Fault Tolerance**: Configurable N/R/W quorum-based replication
- **Hinted Handoff**: Temporary storage when primary replicas are unavailable
- **Merkle Trees**: Anti-entropy mechanism for replica synchronization
- **Vector Clocks**: Conflict resolution for concurrent updates
- **Eventual Consistency**: Guarantees data consistency across replicas over time
- **Performance Monitoring**: Built-in latency and throughput analysis with visualizations

> **Note**: Currently, only **syntactic workers** are fully implemented. Semantic worker implementation is planned for future releases. We apologize for any inconvenience.

## **Directory Structure**

```
ds-majorproject/
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── config.json                        # System configuration
├── Report.pdf                         # Detailed project report
├── start_machine1.sh                  # Start primary node
├── start_secondarynode.sh             # Start secondary nodes
├── stop_machine1.sh                   # Stop primary node
├── stop_secondarynode.sh              # Stop secondary nodes
│
├── code/                              # Core implementation
│   ├── worker.py                      # Worker node (handles GET/PUT/replication)
│   └── client.py                      # Client service (routing layer)
│
├── consistent-hashing/                # Consistent hashing implementation
│   └── HashRing.py                    # Hash ring with virtual nodes
│
├── hinted_handoff/                    # Hinted handoff mechanism
├── merkle_trees/                      # Anti-entropy using Merkle trees
│
├── test/                              # Testing utilities
│   ├── test.py                        # Interactive CLI (main interface)
│   ├── spawn_worker.py                # Spawn multiple workers
│   ├── network_partition.py           # Simulate network failures
│   └── analyze_performance.py         # Performance testing
│
├── logs/                              # System logs with timestamps
│
├── run_visualizations/                # Performance analysis
│   └── analyze_logs_latency.py        # Generate performance graphs
│   └── visualizations/                # Generated graphs
│
├── hashring_visuatlization/           # Hash ring visualization tools
└── system_design_diagrams/            # Architecture diagrams
```

## **Setup**

### **Prerequisites**
- Python 3.8+
- Redis

### **Install Dependencies**
```bash
pip install -r requirements.txt

# Start Redis
redis-server
```

### **Configuration**
Edit `config.json` to configure system parameters:
```json
{
    "ports": {
        "client": 18812,
        "syntactic_worker_start": 3200
    },
    "nodes": [
        {
            "ip": "localhost",
            "port": 3200,
            "vnodes": 3
        }
    ],
    "quorum": {
        "N": 3,  // Number of replicas
        "R": 2,  // Read quorum
        "W": 2   // Write quorum
    }
}
```

## **Running the System**

## **Basic Setup**

First, create and activate a venv , then download requirements.


```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```
On the machine you want to use as your primary one, run the below commands to start the system:
```
./start_machine1.sh
```

On other machines, run:
```
./start_secondarynode.sh
```

Whatever operations you want to do can be done on the terminals that open up. If you want to run locally, make the necessary changes in config.json(add localhost in hostname and 127.0.0.1 in IP address).

## **Configuration**

Edit `config.json` to configure system parameters:

```json
{
    "ports": {
        "client": 18812,
        "syntactic_worker_start": 3200
    },
    "nodes": [
        {
            "ip": "localhost",
            "port": 3200,
            "vnodes": 3
        }
    ],
    "quorum": {
        "N": 3,  // Number of replicas
        "R": 2,  // Read quorum
        "W": 2   // Write quorum
    },
    "timeout": {
        "cache": 300,
        "gossip": 5,
        "heartbeat": 2
    }
}
```

**Key Parameters:**
- **N**: Number of replicas for each key
- **R**: Read quorum (minimum replicas to read from)
- **W**: Write quorum (minimum replicas to write to)
- **vnodes**: Virtual nodes per physical node (for load balancing)

**Configuration Presets:**

Edit the `"quorum"` section in `config.json` based on your use case:

**High Availability** (Eventual Consistency):
```json
"quorum": { "N": 3, "R": 1, "W": 1 }
```
- Fast reads and writes
- Maximum availability
- Eventual consistency

**Strong Consistency**:
```json
"quorum": { "N": 3, "R": 2, "W": 2 }
```
- Guaranteed consistency (R + W > N)
- Balanced read/write performance
- Recommended for most applications

**Read-Heavy Workload**:
```json
"quorum": { "N": 3, "R": 1, "W": 3 }
```
- Optimized for fast reads
- Slower writes
- Good for caching scenarios

**Write-Heavy Workload**:
```json
"quorum": { "N": 3, "R": 3, "W": 1 }
```
- Optimized for fast writes
- Slower reads
- Good for logging/event systems

*Note: For strong consistency, ensure R + W > N*

## **Performance Analysis**

After running operations, generate performance visualizations:

```bash
python3 run_visualizations/analyze_logs_latency.py --log-dir ../logs
```

This creates 6 graphs in `run_visualizations/visualizations/`:

1. **`latency_distribution.png`** - Histogram of GET/PUT latencies
2. **`latency_cdf.png`** - Cumulative distribution with p95/p99
3. **`latency_boxplot_comparison.png`** - Side-by-side GET vs PUT
4. **`throughput_histogram.png`** - Overall throughput distribution
5. **`throughput_boxplot_comparison.png`** - GET vs PUT throughput
6. **`throughput_stacked.png`** - Stacked area chart



## **Testing & Simulation**

### **Network Partition Simulation**
```bash
python3 test/network_partition.py --port 3201
# This blocks port 3201 to test fault tolerance
```

### **Load Testing**
```bash
cd hashring_visuatlization
python3 run_100_operations.py
```

## **Configuration Presets**

Edit the `"quorum"` section in `config.json`:

**High Availability** (Eventual Consistency):
```json
"quorum": { "N": 3, "R": 1, "W": 1 }
```

**Strong Consistency**:
```json
"quorum": { "N": 3, "R": 2, "W": 2 }
```

**Read-Heavy Workload**:
```json
"quorum": { "N": 3, "R": 1, "W": 3 }
```

**Write-Heavy Workload**:
```json
"quorum": { "N": 3, "R": 3, "W": 1 }
```

*Note: For strong consistency, ensure R + W > N*

## **Troubleshooting**

**System won't start:**
```bash
# Check if ports are in use
lsof -i :3200

# Kill existing processes
pkill -f worker.py
pkill -f client.py

# Try again
./start_machine1.sh
```

**Redis connection errors:**
```bash
# Verify Redis is running
redis-cli ping  # Should return "PONG"

# Start Redis if needed
redis-server

# Check Redis on macOS
brew services list | grep redis
```

**Workers not responding:**
```bash
# Check worker logs
tail -f logs/worker_3200.log
tail -f logs/worker_3201.log
tail -f logs/worker_3202.log

# Verify config.json
cat config.json
```

## **System Architecture**

### **Key Components:**
- **Workers** (`worker.py`): Handle GET/PUT/APPEND, maintain replicas, gossip protocol
- **Client Service** (`client.py`): Routes requests, caches routing info, handles retries
- **Consistent Hashing**: Maps keys to nodes using MD5 with virtual nodes
- **Replication**: Quorum-based (N/R/W) with async propagation
- **Hinted Handoff**: Temporary storage when replicas unavailable
- **Merkle Trees**: Anti-entropy synchronization between replicas

For detailed flows, see `system_design_diagrams/`.

## **Performance Characteristics**

Based on testing with 3 nodes (N=3, R=2, W=2):

- **PUT Latency**: ~200-250ms (median), ~500ms (p95)
- **GET Latency**: ~100-150ms (median), ~300ms (p95)
- **Throughput**: ~8-10 ops/sec (single client)
- **Scalability**: Linear with number of nodes
- **Fault Tolerance**: Survives N-W node failures (writes), N-R (reads)

## **Known Limitations**

- **Semantic Workers**: Not yet implemented. Currently only syntactic workers are available.
- **Single Client**: Performance metrics based on single-client testing
- **Local Network**: Optimized for low-latency local network environments

We apologize for any limitations and welcome contributions to enhance the system.



---

**Need help?** Check `run_instructions.md` or `system_design_diagrams/`.