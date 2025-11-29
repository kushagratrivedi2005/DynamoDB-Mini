#!/bin/bash

# Get the absolute path of the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting DynamoMini from $PROJECT_DIR..."

# Kill any existing processes
echo "Killing old processes..."
pkill -f "worker.py" 2>/dev/null || true
pkill -f "spawn_worker.py" 2>/dev/null || true
pkill -f "client.py" 2>/dev/null || true
pkill -f "HashRing.py" 2>/dev/null || true

# Clear Redis cache for fresh start
echo "Clearing Redis cache..."
redis-cli FLUSHALL 2>/dev/null || echo "Warning: Could not clear Redis (is it running?)"

echo "Starting fresh DynamoMini system..."

# Function to open a new tab/window and run a command
open_tab() {
    local title="$1"
    local cmd="$2"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR'; $cmd\""
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --tab --title="$title" -- bash -c "cd '$PROJECT_DIR'; $cmd; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -T "$title" -e "cd '$PROJECT_DIR'; $cmd; exec bash" &
        elif command -v konsole &> /dev/null; then
            konsole --new-tab -e "bash -c \"cd '$PROJECT_DIR'; $cmd; exec bash\"" &
        else
            echo "Error: No supported terminal emulator found (gnome-terminal, xterm, konsole)."
            echo "Please run the following command manually in a new terminal:"
            echo "cd '$PROJECT_DIR' && $cmd"
        fi
    else
        echo "Unsupported OS: $OSTYPE"
        echo "Please run manually: cd '$PROJECT_DIR' && $cmd"
    fi
}

# Terminal 1: HashRing Coordinator
echo "Starting HashRing Coordinator..."
open_tab "HashRing" "python3 consistent-hashing/HashRing.py"

# Terminal 2: Worker Spawner
echo "Starting Worker Spawner..."
open_tab "Worker Spawner" "cd test && python3 spawn_worker.py"

# Terminal 3: Client
echo "Starting Client..."
open_tab "Client" "python3 code/client.py"

# Terminal 4: Test Interface
echo "Starting Test Interface..."
open_tab "Test Interface" "cd test && python3 test.py"

echo "All components started in new Terminal windows/tabs."
