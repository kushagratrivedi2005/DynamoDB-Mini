#!/bin/bash

# Generic Secondary Node Setup Script
# Usage: ./start_secondarynode.sh --machine2
#        ./start_secondarynode.sh --machine3
#        etc.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
MACHINE_NAME=""
for arg in "$@"; do
    if [[ $arg == --machine* ]]; then
        MACHINE_NAME="${arg#--}"
        break
    fi
done

if [ -z "$MACHINE_NAME" ]; then
    echo "Error: Machine name not specified"
    echo "Usage: $0 --machine2|--machine3|--machine4|..."
    echo "Example: $0 --machine2"
    exit 1
fi

# Extract machine number
MACHINE_NUM=$(echo "$MACHINE_NAME" | grep -o '[0-9]\+')

echo "=========================================="
echo "  $MACHINE_NAME - Worker Host Setup"
echo "=========================================="
echo ""

# Check if we're on the right machine
echo "Detected IP addresses:"
ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print "  - " $2}'
echo ""

# Get expected IP from config
EXPECTED_IP=$(grep -A 5 "\"$MACHINE_NAME\"" config.json | grep '"ip"' | cut -d'"' -f4)
if [ -z "$EXPECTED_IP" ]; then
    echo "⚠ Warning: $MACHINE_NAME not found in config.json"
else
    echo "Expected IP from config: $EXPECTED_IP"
fi
echo ""

read -p "Is this $MACHINE_NAME (Worker Host)? (y/n): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Cancelled."
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
    echo "⚠ Port 4001 is in use. Run ./stop_secondarynode.sh first."
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
echo "  Starting Components on $MACHINE_NAME"
echo "=========================================="
echo ""

# Start Worker Spawner in background
echo "Starting Worker Spawner in background..."
nohup python3 test/spawn_worker.py > /tmp/spawn_worker.log 2>&1 &
SPAWN_PID=$!

echo "Waiting for SpawnWorker to start..."
sleep 3

if ps -p $SPAWN_PID > /dev/null 2>&1; then
    echo "✓ SpawnWorker started successfully (PID: $SPAWN_PID)"
else
    echo "✗ Failed to start SpawnWorker"
    exit 1
fi

echo ""
echo "Opening additional terminals..."

# Terminal 1: Network Control (Partition/Heal)
echo "1. Opening Network Control terminal..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use osascript
    osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR'; python3 test/secondary_network_control.py\""
elif command -v gnome-terminal &> /dev/null; then
    # Linux - gnome-terminal
    gnome-terminal --tab --title="Network Control" -- bash -c "cd '$PROJECT_DIR'; python3 test/secondary_network_control.py; exec bash" &
elif command -v xterm &> /dev/null; then
    # Linux - xterm
    xterm -T "Network Control" -e "cd '$PROJECT_DIR'; python3 test/secondary_network_control.py; exec bash" &
elif command -v konsole &> /dev/null; then
    # Linux - konsole
    konsole --new-tab -e "bash -c \"cd '$PROJECT_DIR'; python3 test/secondary_network_control.py; exec bash\"" &
else
    echo "No supported terminal found. Please run manually:"
    echo "cd '$PROJECT_DIR' && python3 test/secondary_network_control.py"
fi
sleep 1

# Terminal 2: Worker Logs Monitor
echo "2. Opening Worker Logs terminal..."
open_tab "Worker Logs" "echo 'Waiting for workers to start...'; while [ ! -f /tmp/worker_3200.log ]; do sleep 2; echo 'Still waiting for allocation from Machine 1...'; done; echo 'Workers detected! Monitoring logs...'; tail -f /tmp/worker_*.log"

echo ""
echo "Checking Machine 1 connectivity..."
if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$machine1_ip/3000" 2>/dev/null; then
    echo "✓ Machine 1 HashRing is REACHABLE"
else
    echo "⚠ Machine 1 HashRing is NOT reachable yet"
    echo "  Machine 1 should be started first!"
fi

echo ""
echo "=========================================="
echo "  $MACHINE_NAME Started Successfully!"
echo "=========================================="
echo ""
echo "Services running:"
echo "  - SpawnWorker (background, PID: $SPAWN_PID)"
echo "  - Network Control (terminal)"
echo "  - Worker Logs Monitor (terminal)"
echo ""
echo "Next steps:"
echo "----------"
echo "1. Go to Machine 1's Test Interface"
echo "2. Select Option 2: Allocate nodes"
echo "3. Enter the number of machines to allocate"
echo ""
echo "To stop $MACHINE_NAME:"
echo "  ./stop_secondarynode.sh"
echo ""
echo "=========================================="
