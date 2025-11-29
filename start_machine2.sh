#!/bin/bash

# Multi-Machine Setup Script for Machine 2 (Worker Host)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "  Machine 2 - Worker Host Setup"
echo "=========================================="
echo ""

# Check if we're on the right machine
echo "Detected IP addresses:"
ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print "  - " $2}'
echo ""
echo "Expected IP: 192.168.1.20"
echo ""

read -p "Is this Machine 2 (Worker Host)? (y/n): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Cancelled. Use start_machine1.sh on Machine 1."
    exit 1
fi

echo ""
echo "Prerequisites Check:"
echo "--------------------"

# Check Redis
if redis-cli ping &>/dev/null; then
    echo "✓ Redis is running"
else
    echo "⚠ Redis not running. Starting Redis..."
    redis-server --daemonize yes
    sleep 2
    if redis-cli ping &>/dev/null; then
        echo "✓ Redis started"
    else
        echo "✗ Failed to start Redis. Please start manually."
        exit 1
    fi
fi

# Check if Redis is bound to 0.0.0.0
redis_bind=$(redis-cli config get bind | tail -n 1)
if [[ "$redis_bind" == "*" ]] || [[ "$redis_bind" == "0.0.0.0" ]]; then
    echo "✓ Redis is bound to all interfaces"
else
    echo "⚠ Redis is bound to: $redis_bind"
    echo "Updating Redis to bind to all interfaces..."
    redis-cli config set bind "0.0.0.0"
    redis-cli config rewrite
    echo "✓ Redis configuration updated"
fi

# Check port
echo ""
echo "Checking if required port is free..."
if lsof -ti:4001 >/dev/null 2>&1; then
    echo "⚠ Port 4001 is in use. Run ./stop_all.sh first."
    exit 1
else
    echo "✓ Port 4001 is free"
fi

# Check connectivity to Machine 1
echo ""
echo "Checking connectivity to Machine 1..."
machine1_ip=$(grep -A 5 '"localhost"' config.json | grep '"ip"' | cut -d'"' -f4)
echo "Machine 1 IP from config.json: $machine1_ip"

if ping -c 2 "$machine1_ip" &>/dev/null; then
    echo "✓ Machine 1 is reachable"
else
    echo "✗ Cannot reach Machine 1 at $machine1_ip"
    echo "Please check network configuration."
    exit 1
fi

echo ""
echo "=========================================="
echo "  Starting Components on Machine 2"
echo "=========================================="
echo ""

# Start Worker Spawner in background
echo "Starting Worker Spawner..."
cd test
python3 -c "
import sys
sys.path.insert(0, '..')
from spawn_worker import SpawnWorkerService
import rpyc
from rpyc.utils.server import ThreadedServer

service = SpawnWorkerService()
server = ThreadedServer(service, hostname='0.0.0.0', port=4001, protocol_config={'allow_public_attrs': True, 'sync_request_timeout': None})
print('SpawnWorker started on 0.0.0.0:4001')
server.start()
" &

SPAWN_PID=$!
cd ..

echo "Waiting for SpawnWorker to start..."
sleep 3

if ps -p $SPAWN_PID > /dev/null 2>&1; then
    echo "✓ SpawnWorker started successfully (PID: $SPAWN_PID)"
else
    echo "✗ Failed to start SpawnWorker"
    exit 1
fi

echo ""
echo "=========================================="
echo "  Machine 2 Started Successfully!"
echo "=========================================="
echo ""
echo "SpawnWorker is running in background"
echo ""
echo "Checking Machine 1 connectivity..."
MACHINE1_IP=$(grep -A 5 '"localhost"' config.json | grep '"ip"' | cut -d'"' -f4)
echo "Machine 1 IP from config: $MACHINE1_IP"

if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$MACHINE1_IP/3000" 2>/dev/null; then
    echo "✓ Machine 1 HashRing is REACHABLE"
else
    echo "⚠ Machine 1 HashRing is NOT reachable yet"
    echo "  Machine 1 should be started first!"
fi

echo ""
echo "After this:"
echo "----------"
echo "1. Go to Machine 1's Test Interface"
echo ""
echo "2. Select Option 2: Allocate nodes"
echo "   → Enter: 2 (to allocate both machines)"
echo ""
echo "3. Workers will be spawned automatically on both machines"
echo ""
echo "4. You can monitor this machine's workers:"
echo "   → ps aux | grep worker.py"
echo "   → lsof -i :3200-3203"
echo ""
echo "5. To check connectivity anytime:"
echo "   → ./check_connectivity.sh"
echo ""
echo "6. To stop Machine 2:"
echo "   → ./stop_machine2.sh"
echo ""
echo "Configuration:"
echo "  Machine 2 will host: 4 worker vnodes"
echo "  Ports: 3200-3203 (assigned dynamically)"
echo "  Redis: Port 6379"
echo ""
echo "=========================================="
