#!/bin/bash

# Multi-Machine Setup Script for Machine 1 (Coordinator)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "  Machine 1 - Coordinator Setup"
echo "=========================================="
echo ""

# Check if we're on the right machine
echo "Detected IP addresses:"
ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print "  - " $2}'
echo ""

read -p "Is this Machine 1 (Coordinator)? (y/n): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Cancelled. Use start_machine2.sh on Machine 2."
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

# Check ports
echo ""
echo "Checking if required ports are free..."
for port in 3000 6001; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "⚠ Port $port is in use. Run ./stop_all.sh first."
        exit 1
    else
        echo "✓ Port $port is free"
    fi
done

echo ""
echo "=========================================="
echo "  Starting Components on Machine 1"
echo "=========================================="
echo ""

# Function to open terminal
open_tab() {
    local title="$1"
    local cmd="$2"
    
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --tab --title="$title" -- bash -c "cd '$PROJECT_DIR'; $cmd; exec bash" &
    elif command -v xterm &> /dev/null; then
        xterm -T "$title" -e "cd '$PROJECT_DIR'; $cmd; exec bash" &
    elif command -v konsole &> /dev/null; then
        konsole --new-tab -e "bash -c \"cd '$PROJECT_DIR'; $cmd; exec bash\"" &
    else
        echo "No supported terminal found. Please run manually:"
        echo "cd '$PROJECT_DIR' && $cmd"
    fi
}

# Terminal 1: HashRing Coordinator
echo "1. Starting HashRing Coordinator..."
open_tab "HashRing" "python3 consistent-hashing/HashRing.py"
sleep 2

# Terminal 2: Client
echo "2. Starting Client..."
open_tab "Client" "python3 code/client.py"
sleep 2

# Terminal 3: Test Interface
echo "3. Starting Test Interface..."
open_tab "Test" "cd test && python3 test.py"

echo ""
echo "=========================================="
echo "  Machine 1 Started Successfully!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "----------"
echo "1. In HashRing terminal:"
echo "   → Select: 2 (Syntactic workers)"
echo ""
echo "2. In Client terminal:"
echo "   → Select: 2 (Syntactic workers)"
echo ""
echo "3. Wait for Machine 2 to start its Worker Spawner"
echo ""
echo "4. In Test Interface terminal:"
echo "   → Option 2: Allocate nodes"
echo "   → Enter: 2 (to allocate both machines)"
echo ""
echo "5. Test multi-machine quorum:"
echo "   → Option 3: PUT data"
echo "   → Option 4: GET data"
echo ""
echo "Configuration:"
echo "  N = 8 (4 vnodes per machine)"
echo "  R = 5 (read quorum)"
echo "  W = 3 (write quorum)"
echo ""
echo "=========================================="
