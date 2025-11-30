#!/usr/bin/env python3
"""
Automated 100 PUT + 100 GET Operations Runner

This script performs 100 sequential PUT operations followed by 100 sequential GET operations
for testing the distributed hash ring with visualization.

Usage:
    python3 run_100_operations.py
"""

import rpyc
import time
import random
import string
import logging
import sys
from os.path import dirname, abspath

# Add parent directory to path
sys.path.append(dirname(dirname(abspath(__file__))))
import utils.config as config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_random_key(length=8):
    """Generate a random key"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def generate_random_value():
    """Generate a random value"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def run_operations():
    """Run 100 PUT and 100 GET operations"""
    
    # Connect to client
    client_url = ('localhost', config.get_port('client'))
    
    print("=" * 60)
    print("  AUTOMATED HASH RING TESTING")
    print("  100 PUT + 100 GET Operations")
    print("=" * 60)
    print()
    
    try:
        # Test connection first
        print("🔌 Connecting to client...")
        conn = rpyc.connect(*client_url, config={'sync_request_timeout': 120})
        print("✓ Connected to client at", client_url)
        print()
    except Exception as e:
        print(f"❌ Failed to connect to client: {e}")
        print("\nMake sure:")
        print("  1. You've started the system with ./start_machine1.sh")
        print("  2. You've allocated nodes via test.py (option 2)")
        print("  3. The client is running on port", config.get_port('client'))
        return
    
    # Store keys for GET operations
    keys_values = []
    
    # ===========================
    # Part 1: 100 PUT Operations
    # ===========================
    print("📝 Starting 100 PUT operations...")
    print("-" * 60)
    
    put_success = 0
    put_failed = 0
    
    for i in range(100):
        key = f"key_{i:03d}_{generate_random_key(4)}"
        value = generate_random_value()
        
        try:
            result = conn.root.put(key, value)
            keys_values.append((key, value))
            put_success += 1
            
            if (i + 1) % 10 == 0:
                print(f"  ✓ PUT {i + 1}/100 complete (success: {put_success}, failed: {put_failed})")
        
        except Exception as e:
            put_failed += 1
            logging.error(f"PUT failed for key {key}: {e}")
            
            if (i + 1) % 10 == 0:
                print(f"  ⚠ PUT {i + 1}/100 complete (success: {put_success}, failed: {put_failed})")
        
        # Small delay to avoid overwhelming the system
        time.sleep(0.05)
    
    print()
    print(f"✅ PUT operations complete: {put_success} success, {put_failed} failed")
    print()
    
    # Small pause between PUT and GET
    time.sleep(2)
    
    # ===========================
    # Part 2: 100 GET Operations
    # ===========================
    print("📖 Starting 100 GET operations...")
    print("-" * 60)
    
    get_success = 0
    get_failed = 0
    get_correct = 0
    get_incorrect = 0
    
    # GET all the keys we just PUT
    for i, (key, expected_value) in enumerate(keys_values):
        try:
            result = conn.root.get(key)
            get_success += 1
            
            # Extract actual value from response
            # Response format: {'status': 0, 'value': {actual_value}}
            actual_value = None
            if isinstance(result, dict):
                if 'value' in result:
                    # Value might be in a set, extract it
                    value_field = result['value']
                    if isinstance(value_field, set):
                        actual_value = list(value_field)[0] if value_field else None
                    else:
                        actual_value = value_field
            else:
                actual_value = result
            
            # Verify the value matches
            if str(actual_value) == str(expected_value):
                get_correct += 1
            else:
                get_incorrect += 1
                logging.warning(f"Value mismatch for {key}: expected {expected_value}, got {actual_value} (from response: {result})")
            
            if (i + 1) % 10 == 0:
                print(f"  ✓ GET {i + 1}/100 complete (success: {get_success}, failed: {get_failed}, correct: {get_correct})")
        
        except Exception as e:
            get_failed += 1
            logging.error(f"GET failed for key {key}: {e}")
            
            if (i + 1) % 10 == 0:
                print(f"  ⚠ GET {i + 1}/100 complete (success: {get_success}, failed: {get_failed}, correct: {get_correct})")
        
        # Small delay
        time.sleep(0.05)
    
    print()
    print(f"✅ GET operations complete: {get_success} success, {get_failed} failed")
    print(f"   Data integrity: {get_correct} correct, {get_incorrect} incorrect")
    print()
    
    # ===========================
    # Summary
    # ===========================
    print("=" * 60)
    print("  OPERATION SUMMARY")
    print("=" * 60)
    print(f"  PUT Operations: {put_success}/{100} successful")
    print(f"  GET Operations: {get_success}/{100} successful")
    print(f"  Data Integrity: {get_correct}/{get_success} values matched")
    print(f"  Overall Success Rate: {((put_success + get_success) / 200) * 100:.1f}%")
    print("=" * 60)
    print()
    print("🎨 Next steps:")
    print("  1. Generate visualization:")
    print("     cd code && python3 hash_ring_viz.py --frames")
    print()
    print("  2. Create animation:")
    print("     python3 generate_animation.py")
    print()
    
    conn.close()


if __name__ == '__main__':
    run_operations()
