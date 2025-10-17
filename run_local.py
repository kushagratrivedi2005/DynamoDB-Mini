#!/usr/bin/env python3
"""
DynamoMini Local Setup Script
Cross-platform script for macOS and Linux
Assumes Redis is already installed
"""

import subprocess
import time
import sys
import os
import platform

def run_command(command, wait=True, capture_output=False):
    """Run a shell command and handle output"""
    print(f"Running: {command}")
    try:
        if wait:
            result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
            if result.returncode != 0 and not capture_output:
                print(f"Command failed with return code: {result.returncode}")
            return result
        else:
            return subprocess.Popen(command, shell=True)
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def check_redis_running():
    """Check if Redis is already running"""
    try:
        result = run_command("redis-cli ping", capture_output=True)
        return result.returncode == 0 and "PONG" in result.stdout
    except:
        return False

def start_redis():
    """Start Redis server"""
    print("Starting Redis...")
    
    # Check if Redis is already running
    if check_redis_running():
        print("Redis is already running")
        return True
    
    # Start Redis server in background mode
    print("Starting Redis server in background mode...")
    redis_process = run_command("redis-server --daemonize yes", wait=False)
    time.sleep(3)
    
    if check_redis_running():
        print("Redis started successfully!")
        return True
    else:
        print("Failed to start Redis automatically.")
        print("Please start Redis manually:")
        print("redis-server --daemonize yes")
        print("Or: redis-server (in foreground)")
        return False

def update_config_files():
    """Update configuration files for localhost"""
    print("Updating configuration files for localhost...")
    
    # Update worker.py
    worker_file = "code/worker.py"
    if os.path.exists(worker_file):
        with open(worker_file, 'r') as f:
            content = f.read()
        
        # Replace hardcoded IP with localhost
        old_line = "self.hash_ring_url = ('172.30.231.182', 3000)"
        new_line = "self.hash_ring_url = ('localhost', 3000)"
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            with open(worker_file, 'w') as f:
                f.write(content)
            print(f"Updated {worker_file}")
        else:
            print(f"No changes needed in {worker_file}")
    
    # Update client.py
    client_file = "code/client.py"
    if os.path.exists(client_file):
        with open(client_file, 'r') as f:
            content = f.read()
        
        # Replace hardcoded IP with localhost
        old_line = "'ip': '172.30.231.182',"
        new_line = "'ip': 'localhost',"
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            with open(client_file, 'w') as f:
                f.write(content)
            print(f"Updated {client_file}")
        else:
            print(f"No changes needed in {client_file}")
    
    # Update HashRing.py
    hashring_file = "consistent-hashing/HashRing.py"
    if os.path.exists(hashring_file):
        with open(hashring_file, 'r') as f:
            content = f.read()
        
        # Replace hardcoded hostname with localhost
        old_line = "'hostname': '172.30.231.182',"
        new_line = "'hostname': 'localhost',"
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            with open(hashring_file, 'w') as f:
                f.write(content)
            print(f"Updated {hashring_file}")
        else:
            print(f"No changes needed in {hashring_file}")

def create_env_file():
    """Create .env file for HashRing if it doesn't exist"""
    env_file = "consistent-hashing/.env"
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("# Environment variables for HashRing\n")
            f.write("# Add your credentials here if needed\n")
            f.write("USERNAME_LOCALHOST=password\n")
        print(f"Created {env_file}")
    else:
        print(f"{env_file} already exists")

def check_dependencies():
    """Check if required Python packages are installed"""
    print("Checking Python dependencies...")
    
    # Map package names to their import names
    packages = {
        'rpyc': 'rpyc',
        'redis': 'redis', 
        'pexpect': 'pexpect',
        'python-dotenv': 'dotenv'  # This is the key fix
    }
    
    missing_packages = []
    
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - MISSING")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("All Python dependencies are installed!")
    return True

def print_usage_instructions():
    """Print step-by-step instructions for running the system"""
    print("\n" + "=" * 70)
    print("DynamoMini System Ready!")
    print("=" * 70)
    print("\nTo run the complete system, open 4 terminals and run:")
    print("\nTerminal 1 - Start HashRing Coordinator:")
    print("  cd DynamoMini")
    print("  python3 consistent-hashing/HashRing.py")
    print("  → Choose option 1 when prompted (Semantic)")
    print("  → Wait for 'Hashring started listening on port 3000...'")
    
    print("\nTerminal 2 - Start Worker Spawner:")
    print("  cd DynamoMini/test")
    print("  python3 spawn_worker.py")
    print("  → Wait for 'Listening at port 4001...'")
    
    print("\nTerminal 3 - Start Client:")
    print("  cd DynamoMini")
    print("  python3 code/client.py")
    print("  → Wait for 'Client is listening at port 6001...'")
    
    print("\nTerminal 4 - Run Tests:")
    print("  cd DynamoMini/test")
    print("  python3 test.py")
    print("  → Choose option 2 to allocate nodes")
    print("  → Choose option 3 to test PUT operations")
    print("  → Choose option 4 to test GET operations")
    
    print("\n" + "=" * 70)
    print("Quick Test Sequence:")
    print("=" * 70)
    print("1. In test.py, choose option 2 → Enter '1' to allocate 1 node")
    print("2. Choose option 3 → Enter key 'test' → Enter value 'hello'")
    print("3. Choose option 4 → Enter key 'test' to retrieve the value")
    print("4. Choose option 9 to see node status")
    
    print("\nTo stop Redis when done:")
    print("  pkill redis-server")
    print("  # or")
    print("  redis-cli shutdown")

def main():
    print("=" * 70)
    print("DynamoMini Local Setup Script")
    print("Cross-platform (macOS & Linux)")
    print("=" * 70)
    
    # Detect OS
    os_name = platform.system()
    print(f"Detected OS: {os_name}")
    
    print("\nStarting DynamoMini setup...")
    print("(Assuming Redis is already installed)")
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies first:")
        print("pip install -r requirements.txt")
        return
    
    # Start Redis
    if not start_redis():
        print("\nRedis startup failed. Please ensure Redis is installed and try again.")
        print("\nTo install Redis:")
        if os_name == "Darwin":  # macOS
            print("  brew install redis")
        else:  # Linux
            print("  sudo apt-get install redis-server  # Ubuntu/Debian")
            print("  sudo yum install redis             # CentOS/RHEL")
            print("  sudo pacman -S redis               # Arch")
        return
    
    # Update configuration files
    update_config_files()
    
    # Create .env file
    create_env_file()
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main()
