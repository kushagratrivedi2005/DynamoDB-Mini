#!/bin/bash

# Stop Script for Secondary Nodes (Machine 2, 3, 4, ...)

echo "=========================================="
echo "  Stopping Secondary Node"
echo "=========================================="
echo ""

# Kill SpawnWorker
echo "Stopping SpawnWorker (port 4001)..."
pkill -9 -f "spawn_worker.py"
lsof -ti:4001 | xargs -r kill -9 2>/dev/null

# Kill network control script
echo "Stopping Network Control..."
pkill -9 -f "secondary_network_control.py"

# Kill all worker processes
echo "Stopping all Worker processes (ports 3200-3203, 3100-3103)..."
pkill -9 -f "code/worker.py"
for port in {3100..3103} {3200..3203}; do
    lsof -ti:$port | xargs -r kill -9 2>/dev/null
done

# Clean up TCP connections
echo "Cleaning up TCP connections..."
for port in 3100 3101 3102 3103 3200 3201 3202 3203 4001; do
    ss -K dst :$port 2>/dev/null
done

# Clear iptables rules
echo "Clearing iptables rules..."
sudo iptables -F 2>/dev/null
sudo iptables -X 2>/dev/null

# Flush Redis
echo "Flushing Redis database..."
redis-cli FLUSHALL 2>/dev/null

# Clean up log files
echo "Cleaning up log files..."
rm -f logs/worker_*.log 2>/dev/null
rm -f logs/quorum.log 2>/dev/null
rm -f logs/spawn_worker.log 2>/dev/null

echo ""
echo "=========================================="
echo "  Secondary Node Stopped Successfully!"
echo "=========================================="
echo ""
echo "Verification:"
echo "Checking remaining processes..."
REMAINING=$(ps aux | grep -E "(worker.py|spawn_worker|secondary_network)" | grep -v grep)
if [ -z "$REMAINING" ]; then
    echo "✓ All processes stopped successfully!"
else
    echo "⚠ Some processes still running:"
    echo "$REMAINING"
fi

echo ""
echo "Checking ports..."
for port in 3100 3101 3102 3103 3200 3201 3202 3203 4001; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "⚠ Port $port still in use"
    fi
done
echo "✓ Port check complete"
