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
for port in 3000 4001 6001; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "⚠ Port $port is in use. Run ./stop_machine1.sh first."
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
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - use osascript
        osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR'; $cmd\""
    elif command -v gnome-terminal &> /dev/null; then
        # Linux - gnome-terminal
        gnome-terminal --tab --title="$title" -- bash -c "cd '$PROJECT_DIR'; $cmd; exec bash" &
    elif command -v xterm &> /dev/null; then
        # Linux - xterm
        xterm -T "$title" -e "cd '$PROJECT_DIR'; $cmd; exec bash" &
    elif command -v konsole &> /dev/null; then
        # Linux - konsole
        konsole --new-tab -e "bash -c \"cd '$PROJECT_DIR'; $cmd; exec bash\"" &
    else
        echo "No supported terminal found. Please run manually:"
        echo "cd '$PROJECT_DIR' && $cmd"
    fi
}

# Terminal 1: SpawnWorker
echo "1. Starting SpawnWorker..."
open_tab "SpawnWorker" "cd test && python3 spawn_worker.py"
sleep 2

# Terminal 2: HashRing Coordinator
echo "2. Starting HashRing Coordinator..."
open_tab "HashRing" "python3 consistent-hashing/HashRing.py"
sleep 2

# Terminal 3: Client
echo "3. Starting Client..."
open_tab "Client" "python3 code/client.py"
sleep 2

# Terminal 4: Test Interface
echo "4. Starting Test Interface..."
open_tab "Test" "cd test && python3 test.py"


# Terminal 5: Worker Logs (Monitor gossip and quorum)
echo "5. Opening Worker Logs Monitor..."
open_tab "Worker Logs" "echo 'Waiting for workers to start...'; sleep 3; tail -f /tmp/worker_*.log 2>/dev/null || echo 'No worker logs yet. Workers will appear after allocation.'; exec bash"

# Terminal 6: Quorum Events (GET/PUT)
echo "6. Opening Quorum Events Monitor..."
open_tab "Quorum Events" "echo 'Waiting for quorum events...'; sleep 3; tail -f /tmp/quorum.log 2>/dev/null || echo 'No quorum events yet.'; exec bash"

echo ""
echo "=========================================="
echo "  Machine 1 Started Successfully!"
echo "=========================================="
echo ""
echo "Checking Machine 2 connectivity..."
MACHINE2_IP=$(grep -A 5 '"machine2"' config.json | grep '"ip"' | cut -d'"' -f4)
echo "Machine 2 IP from config: $MACHINE2_IP"

if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$MACHINE2_IP/4001" 2>/dev/null; then
    echo "✓ Machine 2 SpawnWorker is REACHABLE on port 4001"
else
    echo "⚠ Machine 2 SpawnWorker is NOT reachable yet"
    echo "  Make sure to start Machine 2 before allocating nodes!"
fi

echo ""
echo "Terminals Opened:"
echo "  1. SpawnWorker - Spawns worker processes"
echo "  2. HashRing - Coordinator for consistent hashing"
echo "  3. Client - RPC client interface"
echo "  4. Test - Interactive test menu"
echo "  5. Worker Logs - Monitor gossip, quorum checks, node status"
echo ""
echo "Next Steps:"
echo "----------"
echo "1. In SpawnWorker terminal:"
echo "   → Select: 0 (Keep server alive)"
echo ""
echo "2. In HashRing terminal:"
echo "   → Select: 2 (Syntactic workers)"
echo ""
echo "3. In Client terminal:"
echo "   → Select: 2 (Syntactic workers)"
echo ""
echo "4. Verify Machine 2 is ready (check above ✓)"
echo "   If not ready, start Machine 2 now!"
echo ""
echo "5. In Test Interface terminal:"
echo "   → Option 2: Allocate nodes"
echo "   → Enter: 2 (to allocate both machines)"
echo ""
echo "6. Watch Worker Logs terminal for:"
echo "   → Gossip activity (🗣️)"
echo "   → Node status changes (❌ DOWN / ✅ UP)"
echo "   → Quorum checks during GET/PUT"
echo ""
echo "6. Test multi-machine quorum:"
echo "   → Option 3: PUT data"
echo "   → Option 4: GET data"
echo ""
echo "Configuration:"
echo "  N = 8 (4 vnodes per machine)"
echo "  R = 5 (read quorum)"
echo "  W = 3 (write quorum)"
echo ""
echo "=========================================="
