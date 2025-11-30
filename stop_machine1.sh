#!/bin/bash

# Stop Script for Machine 1 (Coordinator)

echo "=========================================="
echo "  Stopping Machine 1 (Coordinator)"
echo "=========================================="
echo ""

# Kill HashRing
echo "Stopping HashRing (port 3000)..."
pkill -9 -f "HashRing.py"
lsof -ti:3000 | xargs -r kill -9 2>/dev/null

# Kill Client
echo "Stopping Client (port 6001)..."
pkill -9 -f "code/client.py"
lsof -ti:6001 | xargs -r kill -9 2>/dev/null

# Kill Test Interface
echo "Stopping Test Interface..."
pkill -9 -f "test/test.py"

# Kill SpawnWorker (if running on Machine 1)
echo "Stopping SpawnWorker (port 4001)..."
pkill -9 -f "spawn_worker.py"
lsof -ti:4001 | xargs -r kill -9 2>/dev/null

# Kill all worker processes
echo "Stopping all Worker processes (ports 3200-3203)..."
pkill -9 -f "code/worker.py"
for port in {3200..3203}; do
    lsof -ti:$port | xargs -r kill -9 2>/dev/null
done

# Clean up TCP connections
echo "Cleaning up TCP connections..."
for port in 3000 3200 3201 3202 3203 4001 6001; do
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
rm -f /tmp/worker_*.log 2>/dev/null
rm -f /tmp/quorum.log 2>/dev/null
rm -f /tmp/spawn_worker.log 2>/dev/null

echo ""
echo "=========================================="
echo "  Machine 1 Stopped Successfully!"
echo "=========================================="
echo ""
echo "Verification:"
echo "Checking remaining processes..."
REMAINING=$(ps aux | grep -E "(HashRing|client.py|test.py|worker.py|spawn_worker)" | grep -v grep)
if [ -z "$REMAINING" ]; then
    echo "✓ All processes stopped successfully!"
else
    echo "⚠ Some processes still running:"
    echo "$REMAINING"
fi

echo ""
echo "Checking ports..."
for port in 3000 3200 3201 3202 3203 4001 6001; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "⚠ Port $port still in use"
    fi
done
echo "✓ Port check complete"
