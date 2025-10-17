# DynamoMini - Step-by-Step Run Instructions

This guide will walk you through setting up and running the DynamoMini distributed key-value store from scratch.

## Prerequisites

Before starting, ensure you have the following installed:

### 1. Python 3.8+
Check your Python version:
```bash
python3 --version
```
If not installed, install from [python.org](https://www.python.org/downloads/)

### 2. Redis Server
Install Redis based on your operating system:

**macOS (using Homebrew):**
```bash
brew install redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
```

**CentOS/RHEL:**
```bash
sudo yum install redis
# or
sudo dnf install redis
```

**Arch Linux:**
```bash
sudo pacman -S redis
```

### 3. Git (for cloning)
```bash
git --version
```

## Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd DynamoMini
```

## Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `rpyc` - For RPC communication
- `redis` - Redis Python client
- `pexpect` - For SSH automation
- `python-dotenv` - Environment variable management

## Step 3: Run the Setup Script

```bash
python3 run_local.py
```

This script will:
- ✅ Check if Redis is running and start it if needed
- ✅ Update configuration files to use localhost
- ✅ Create necessary environment files
- ✅ Verify all dependencies are installed
- ✅ Provide detailed instructions for the next steps

## Step 4: Start the System Components

The setup script will provide instructions, but here's the complete process:

### Terminal 1 - Start HashRing Coordinator
```bash
cd DynamoMini
python3 consistent-hashing/HashRing.py
```
When prompted:
- Choose option **1** for "Semantic" (general key-value store)
- Wait for message: `Hashring started listening on port 3000...`

### Terminal 2 - Start Worker Spawner
```bash
cd DynamoMini/test
python3 spawn_worker.py
```
Wait for message: `Listening at port 4001...`

### Terminal 3 - Start Client Interface
```bash
cd DynamoMini
python3 code/client.py
```
Wait for message: `Client is listening at port 6001...`

### Terminal 4 - Run Tests
```bash
cd DynamoMini/test
python3 test.py
```

## Step 5: Test the System

In the test terminal (Terminal 4), you can now test the system:

### Allocate Nodes
1. Choose option **2** (Test spawn workers)
2. Enter **1** to allocate 1 node
3. Wait for allocation to complete

### Test PUT Operation
1. Choose option **3** (Syntactic PUT)
2. Enter key: `test`
3. Enter value: `hello`
4. You should see success message

### Test GET Operation
1. Choose option **4** (Syntactic GET)
2. Enter key: `test`
3. You should see the value: `hello`

### Check Node Status
1. Choose option **9** (Print nodes status)
2. View active and down nodes

## Step 6: Advanced Testing

### Test Multiple Operations
```bash
# Test different keys and values
Key: user123, Value: john_doe
Key: session456, Value: active
Key: config, Value: production
```

### Test Fault Tolerance
1. Choose option **7** (Network PARTITION) to simulate node failure
2. Try operations during partition
3. Choose option **8** (Network HEAL) to restore connectivity
4. Verify data consistency after recovery

## Troubleshooting

### Redis Issues
If Redis fails to start:
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start manually:
redis-server --daemonize yes

# Check Redis status
redis-cli info server
```

### Port Conflicts
If you get "port already in use" errors:
```bash
# Find processes using ports
lsof -i :3000  # HashRing port
lsof -i :4001  # Spawn worker port
lsof -i :6001  # Client port
lsof -i :3200  # Worker ports

# Kill processes if needed
kill -9 <process_id>
```

### Python Import Errors
If you get import errors:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python path
python3 -c "import sys; print(sys.path)"
```

### Connection Refused Errors
- Ensure all components are running in the correct order
- Check that IP addresses are set to localhost in config files
- Verify firewall isn't blocking ports

## System Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HashRing      │    │   SpawnWorker   │    │     Client      │
│   (Port 3000)   │    │   (Port 4001)   │    │   (Port 6001)   │
│                 │    │                 │    │                 │
│ - Manages ring  │    │ - Spawns nodes  │    │ - User interface│
│ - Coordinates   │    │ - Manages Redis │    │ - Caching       │
│ - Handles joins │    │ - Load balancing│    │ - Retry logic   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Worker Nodes   │
                    │  (Ports 3200+)  │
                    │                 │
                    │ - Data storage  │
                    │ - Replication   │
                    │ - Gossip protocol│
                    │ - Fault tolerance│
                    └─────────────────┘
```

## Stopping the System

To stop all components:

1. **Stop test script**: Press `Ctrl+C` in Terminal 4
2. **Stop client**: Press `Ctrl+C` in Terminal 3  
3. **Stop spawn worker**: Press `Ctrl+C` in Terminal 2
4. **Stop HashRing**: Press `Ctrl+C` in Terminal 1
5. **Stop Redis**: 
   ```bash
   redis-cli shutdown
   # or
   pkill redis-server
   ```

## Next Steps

Once you're comfortable with the basic operations:

1. **Scale up**: Allocate more nodes (option 2, enter larger numbers)
2. **Test consistency**: Write to multiple keys and verify reads
3. **Test fault tolerance**: Simulate network partitions
4. **Monitor performance**: Check node status and load distribution
5. **Explore code**: Examine the implementation details in the source files

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure all terminals are running the correct commands
4. Check the logs in each terminal for error messages

Happy distributed computing! 🚀
