#!/bin/bash

echo "Stopping all DynamoMini processes..."

# Kill all Python processes related to DynamoMini (force kill first)
pkill -9 -f "worker.py" 2>/dev/null && echo "✓ Force killed workers"
pkill -9 -f "spawn_worker.py" 2>/dev/null && echo "✓ Force killed spawn_worker"
pkill -9 -f "client.py" 2>/dev/null && echo "✓ Force killed client"
pkill -9 -f "HashRing.py" 2>/dev/null && echo "✓ Force killed HashRing"
pkill -9 -f "test.py" 2>/dev/null && echo "✓ Force killed test.py"

# Also kill by exact Python venv path (more specific)
pkill -9 -f ".venv.*python" 2>/dev/null

echo ""
echo "Waiting for ports to be freed..."
sleep 3

# Force kill any processes still using the ports
echo "Checking for processes on ports..."
for port in 3000 3100 3200 3201 3202 3203 4001 6001 6379; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "✓ Killing process on port $port (PID: $PID)"
        kill -9 $PID 2>/dev/null
        sleep 0.5
    fi
done

# Force close any TCP connections in TIME_WAIT state
echo ""
echo "Clearing TCP connections..."
sudo ss -K dst :3000 2>/dev/null
sudo ss -K dst :3200 2>/dev/null
sudo ss -K dst :3201 2>/dev/null
sudo ss -K dst :3202 2>/dev/null
sudo ss -K dst :3203 2>/dev/null
sudo ss -K dst :4001 2>/dev/null
sudo ss -K dst :6001 2>/dev/null

# Clear any iptables rules
echo "Clearing iptables rules..."
sudo iptables -F OUTPUT 2>/dev/null && echo "✓ Cleared iptables OUTPUT"
sudo iptables -F INPUT 2>/dev/null && echo "✓ Cleared iptables INPUT"

# Clean up any stale socket files
echo "Cleaning up socket files..."
rm -f /tmp/rpyc_* 2>/dev/null
rm -f /tmp/dynamomini_* 2>/dev/null

# Clean up log files
echo "Cleaning up log files..."
rm -f /tmp/worker_*.log 2>/dev/null
rm -f /tmp/quorum.log 2>/dev/null
rm -f /tmp/spawn_worker.log 2>/dev/null

# Drop any connection tracking
echo "Clearing connection tracking..."
sudo conntrack -D -p tcp --dport 3000 2>/dev/null
sudo conntrack -D -p tcp --dport 3200 2>/dev/null
sudo conntrack -D -p tcp --dport 3201 2>/dev/null
sudo conntrack -D -p tcp --dport 3202 2>/dev/null
sudo conntrack -D -p tcp --dport 3203 2>/dev/null
sudo conntrack -D -p tcp --dport 4001 2>/dev/null
sudo conntrack -D -p tcp --dport 6001 2>/dev/null

# Clear Redis cache
echo "Clearing Redis cache..."
redis-cli FLUSHALL 2>/dev/null && echo "✓ Redis cache cleared"

echo ""
sleep 2
echo "Verifying all ports are free..."
for port in 3000 3200 3201 3202 3203 4001 6001; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "⚠ WARNING: Port $port still in use!"
    else
        echo "✓ Port $port is free"
    fi
done

echo ""
echo "All DynamoMini processes stopped and ports freed!"
echo "Redis cache has been cleared"