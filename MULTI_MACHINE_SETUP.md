# Multi-Machine Deployment Guide

This guide explains how to set up and test the distributed key-value store across **2 physical machines**.

---

## 🎯 Overview

**Current Configuration:**
- **Machine 1** (Coordinator): Runs HashRing, Client, Test Interface, and 4 worker vnodes
- **Machine 2** (Worker Host): Runs Worker Spawner, Redis, and 4 worker vnodes
- **Quorum Settings**: N=8, R=5, W=3
- **Total vnodes**: 8 (4 per machine)

---

## 📋 Prerequisites

### Both Machines Need:
1. **Python 3.8+** with required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Redis Server** installed and running:
   ```bash
   # Install Redis (if not already installed)
   sudo apt-get update
   sudo apt-get install redis-server
   
   # Start Redis
   redis-server --daemonize yes
   
   # Verify
   redis-cli ping  # Should return "PONG"
   ```

3. **Network connectivity** between machines
4. **Same project code** synchronized on both machines

---

## 🔧 Configuration

### 1. Update IP Addresses in `config.json`

**Machine 1** should have the **actual IP** (not localhost). Edit the config:

```json
{
  "nodes": [
    {
      "hostname": "machine1",
      "ip": "192.168.1.10",     # ← Update with Machine 1's actual IP
      "vnodes": 4
    },
    {
      "hostname": "machine2",
      "ip": "192.168.1.20",     # ← Update with Machine 2's actual IP
      "vnodes": 4
    }
  ]
}
```

**To find your IP address:**
```bash
ip addr show | grep "inet " | grep -v "127.0.0.1"
```

### 2. Configure Redis to Accept Remote Connections

**On Machine 2** (and Machine 1 if needed):

```bash
# Check current binding
redis-cli config get bind

# Bind to all interfaces
redis-cli config set bind "0.0.0.0"
redis-cli config set protected-mode "no"

# Save configuration
redis-cli config rewrite

# Restart Redis
sudo systemctl restart redis-server
```

**Verify Redis accessibility:**
```bash
# From Machine 1, test Machine 2's Redis:
redis-cli -h 192.168.1.20 ping   # Should return "PONG"
```

### 3. Firewall Configuration

**Open required ports on both machines:**

```bash
# Machine 1 ports:
sudo ufw allow 3000/tcp   # HashRing
sudo ufw allow 6001/tcp   # Client
sudo ufw allow 3200:3203/tcp  # Workers
sudo ufw allow 6379/tcp   # Redis

# Machine 2 ports:
sudo ufw allow 4001/tcp   # SpawnWorker
sudo ufw allow 3200:3203/tcp  # Workers
sudo ufw allow 6379/tcp   # Redis

# Enable firewall
sudo ufw enable
sudo ufw status
```

**For iptables:**
```bash
sudo iptables -A INPUT -p tcp --dport 3000:6379 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 4001 -j ACCEPT
```

---

## 🚀 Starting the System

### Step 1: Start Machine 2 (Worker Host)

```bash
cd /path/to/ds-majorproject
chmod +x start_machine2.sh
./start_machine2.sh
```

**In the SpawnWorker terminal that opens:**
- Select option **0** (Keep server alive)

This starts the Worker Spawner service that will spawn worker processes on demand.

---

### Step 2: Start Machine 1 (Coordinator)

```bash
cd /path/to/ds-majorproject
chmod +x start_machine1.sh
./start_machine1.sh
```

This opens **3 terminals**:

1. **HashRing Terminal**:
   - Select option **2** (Syntactic workers)

2. **Client Terminal**:
   - Select option **2** (Syntactic workers)

3. **Test Interface Terminal**:
   - Wait for the next step

---

### Step 3: Allocate Nodes

**In Machine 1's Test Interface terminal:**

1. Select option **2** (Allocate nodes)
2. Enter **2** (number of machines to allocate)

This will:
- Connect to both machines' Worker Spawners
- Spawn 4 worker processes on Machine 1 (ports 3200-3203)
- Spawn 4 worker processes on Machine 2 (ports 3200-3203)
- Build the consistent hash ring with 8 vnodes total

---

## ✅ Verification

### 1. Check Workers on Machine 1:
```bash
ps aux | grep worker.py
lsof -i :3200-3203
```

### 2. Check Workers on Machine 2:
```bash
ps aux | grep worker.py
lsof -i :3200-3203
```

### 3. Test Basic Operations

**In Machine 1's Test Interface:**

**PUT Operation:**
```
Select option: 3
Enter key: test_key
Enter value: test_value
```

**GET Operation:**
```
Select option: 4
Enter key: test_key
```

You should see the value returned successfully!

---

## 🧪 Testing Quorum with Network Partition

### Test Scenario 1: Block Machine 2 Completely

**On Machine 1:**
```bash
# Block Machine 2's IP
sudo iptables -A OUTPUT -d 192.168.1.20 -j DROP
sudo iptables -A INPUT -s 192.168.1.20 -j DROP
```

**Expected Result:**
- With N=8, R=5, W=3
- Machine 1 has 4 vnodes (not enough for R=5 or W=3)
- **PUT should FAIL** (cannot reach W=3)
- **GET should FAIL** (cannot reach R=5)

**Clear the block:**
```bash
sudo iptables -F
```

---

### Test Scenario 2: Block 2 of Machine 2's Workers

**On Machine 1:**
```bash
# Block specific ports on Machine 2
sudo iptables -A OUTPUT -d 192.168.1.20 -p tcp --dport 3200 -j DROP
sudo iptables -A OUTPUT -d 192.168.1.20 -p tcp --dport 3201 -j DROP
```

**Expected Result:**
- 6 vnodes accessible (4 on Machine 1 + 2 on Machine 2)
- **PUT should SUCCEED** (W=3, we have 6 nodes)
- **GET should SUCCEED** (R=5, we have 6 nodes)

**Clear the block:**
```bash
sudo iptables -F
```

---

## 🛑 Stopping the System

### On Machine 1:
```bash
./stop_all.sh
```

### On Machine 2:
```bash
./stop_all.sh
```

This will:
- Kill all worker processes
- Kill coordinator processes
- Free up all ports
- Clear iptables rules

---

## 🐛 Troubleshooting

### Problem: Cannot connect to Machine 2

**Check network connectivity:**
```bash
ping 192.168.1.20
telnet 192.168.1.20 4001
```

**Check firewall:**
```bash
sudo ufw status
sudo iptables -L -n
```

---

### Problem: Redis connection refused

**Check Redis is running:**
```bash
redis-cli ping
```

**Check Redis binding:**
```bash
redis-cli config get bind
# Should show: 0.0.0.0 or *
```

**Test remote Redis:**
```bash
redis-cli -h 192.168.1.20 ping
```

---

### Problem: Workers not spawning

**Check SpawnWorker is running on Machine 2:**
```bash
lsof -i :4001
```

**Check logs in worker terminals for errors**

**Verify config.json has correct IPs**

---

### Problem: Quorum failures

**Check how many workers are reachable:**
```bash
# On both machines
ps aux | grep worker.py | wc -l
```

**Verify timeout settings in config.json:**
- `cache_timeout`: 30
- `gossip_timeout`: 10
- `replicate_sync_timeout`: 10
- `replicated_timeout`: 30

**Check iptables rules:**
```bash
sudo iptables -L -n -v
```

---

## 📊 Monitoring

### Real-time Worker Status (Machine 1):
```bash
watch -n 2 'lsof -i :3200-3203'
```

### Real-time Worker Status (Machine 2):
```bash
watch -n 2 'lsof -i :3200-3203'
```

### Redis Data Check:
```bash
redis-cli keys '*'
redis-cli get <key>
```

### Network Traffic:
```bash
sudo tcpdump -i any port 3200 or port 3201 or port 3202 or port 3203
```

---

## 🎓 Understanding the Setup

### Why 2 Machines?

- **Single Machine**: All nodes share the same network stack, CPU, memory
- **Multi-Machine**: True distributed system testing with real network latency, independent failures

### Quorum Settings (N=8, R=5, W=3):

- **N=8**: Total replicas (8 vnodes across 2 machines)
- **R=5**: Read from 5 replicas (majority)
- **W=3**: Write to 3 replicas (minority)

This configuration:
- ✅ Tolerates 3 node failures for reads (8 - 5 = 3)
- ✅ Tolerates 5 node failures for writes (8 - 3 = 5)
- ✅ Ensures read-after-write consistency when R + W > N (5 + 3 = 8 > 8)

### Fast Failover:

With `connect_timeout=3` seconds:
- Blocked nodes fail in 3 seconds (not 60+ seconds)
- Client quickly tries alternative nodes
- Quorum can be satisfied even with network partitions

---

## 🔄 Next Steps

1. **Test with 3 machines**: Add a third node to `config.json`
2. **Implement automatic node discovery**: Remove manual IP configuration
3. **Add monitoring dashboard**: Real-time view of node status
4. **Test byzantine failures**: Workers returning incorrect data
5. **Benchmark performance**: Measure throughput and latency

---

## 📝 Summary

You now have a **true distributed system** running across 2 physical machines:

- ✅ Real network communication between nodes
- ✅ Quorum-based consistency (N=8, R=5, W=3)
- ✅ Network partition testing with iptables
- ✅ Fast failover (3-second timeout)
- ✅ Gossip-based failure detection
- ✅ Vector clock versioning

**Happy Testing! 🚀**
