#!/bin/bash

echo "Stopping all DynamoMini processes..."

# Kill all Python processes related to DynamoMini
pkill -f "worker.py" && echo "✓ Killed workers"
pkill -f "spawn_worker.py" && echo "✓ Killed spawn_worker"
pkill -f "client.py" && echo "✓ Killed client"
pkill -f "HashRing.py" && echo "✓ Killed HashRing"

echo ""
echo "All DynamoMini processes stopped!"
echo "Note: Redis is still running (use 'redis-cli shutdown' to stop it)"
