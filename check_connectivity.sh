#!/bin/bash

# Check connectivity between machines

echo "=========================================="
echo "  Multi-Machine Connectivity Check"
echo "=========================================="
echo ""

# Get IPs from config
MACHINE1_IP=$(grep -A 5 '"localhost"' config.json | grep '"ip"' | cut -d'"' -f4)
MACHINE2_IP=$(grep -A 5 '"machine2"' config.json | grep '"ip"' | cut -d'"' -f4)

echo "Configuration:"
echo "  Machine 1: $MACHINE1_IP"
echo "  Machine 2: $MACHINE2_IP"
echo ""

# Check which machine we're on
CURRENT_IP=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d'/' -f1 | head -1)
echo "Current machine IP: $CURRENT_IP"
echo ""

# Function to check port
check_port() {
    local ip=$1
    local port=$2
    local name=$3
    
    if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$ip/$port" 2>/dev/null; then
        echo "✓ $name ($ip:$port) is REACHABLE"
        return 0
    else
        echo "✗ $name ($ip:$port) is NOT reachable"
        return 1
    fi
}

echo "Checking Machine 1 Services:"
echo "----------------------------"
check_port "$MACHINE1_IP" 4001 "SpawnWorker"
check_port "$MACHINE1_IP" 3000 "HashRing"
check_port "$MACHINE1_IP" 6001 "Client"
check_port "$MACHINE1_IP" 6379 "Redis"

echo ""
echo "Checking Machine 2 Services:"
echo "----------------------------"
check_port "$MACHINE2_IP" 4001 "SpawnWorker"
check_port "$MACHINE2_IP" 6379 "Redis"

echo ""
echo "Checking Worker Ports (both machines):"
echo "--------------------------------------"
for port in 3200 3201 3202 3203; do
    if lsof -i:$port >/dev/null 2>&1; then
        echo "✓ Port $port is IN USE (worker running locally)"
    else
        # Check remote
        check_port "$MACHINE1_IP" $port "Machine 1 Worker" >/dev/null 2>&1 && echo "✓ Machine 1 - Port $port in use" || true
        check_port "$MACHINE2_IP" $port "Machine 2 Worker" >/dev/null 2>&1 && echo "✓ Machine 2 - Port $port in use" || true
    fi
done

echo ""
echo "Network Test:"
echo "-------------"
if ping -c 2 "$MACHINE2_IP" >/dev/null 2>&1; then
    echo "✓ Can ping Machine 2"
else
    echo "✗ Cannot ping Machine 2"
fi

echo ""
echo "=========================================="
echo "Summary:"
if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$MACHINE1_IP/4001" 2>/dev/null && \
   timeout 2 bash -c "cat < /dev/null > /dev/tcp/$MACHINE2_IP/4001" 2>/dev/null; then
    echo "✓ Both machines are ready!"
    echo "  You can allocate nodes now."
else
    echo "⚠ Not all services are ready."
    echo "  Start missing services before allocating nodes."
fi
echo "=========================================="
