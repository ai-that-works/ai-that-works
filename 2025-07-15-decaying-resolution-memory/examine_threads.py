#!/usr/bin/env python3
import redis
import json
from typing import List, Dict, Any
import sys
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Redis connection URL
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL is not set")

def connect_to_redis():
    """Connect to Redis instance"""
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
        print("✅ Connected to Redis successfully")
        return r
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        sys.exit(1)

def examine_thread_keys(r: redis.Redis):
    """Examine all thread keys in detail"""
    # Get all thread keys
    thread_keys = []
    cursor = 0
    while True:
        cursor, batch = r.scan(cursor, match="thread_*", count=100)
        thread_keys.extend(batch)
        if cursor == 0:
            break
    
    print(f"\n📊 Found {len(thread_keys)} thread keys")
    
    # Sort by timestamp (appears to be in the key name)
    thread_keys.sort()
    
    # Examine each thread
    for i, key in enumerate(thread_keys):
        print(f"\n{'='*60}")
        print(f"Thread {i+1}/{len(thread_keys)}: {key}")
        
        key_type = r.type(key)
        print(f"Type: {key_type}")
        
        if key_type == 'string':
            value = r.get(key)
            try:
                # Try to parse as JSON
                data = json.loads(value)
                print(f"\n📄 JSON Content:")
                print(json.dumps(data, indent=2))
                
                # Extract key information if available
                if isinstance(data, dict):
                    print(f"\n📌 Key Information:")
                    for field in ['id', 'timestamp', 'type', 'name', 'status', 'created_at', 'updated_at']:
                        if field in data:
                            print(f"  - {field}: {data[field]}")
                    
                    # Look for trace-related fields
                    trace_fields = ['traces', 'spans', 'events', 'logs', 'metrics', 'telemetry']
                    for field in trace_fields:
                        if field in data:
                            print(f"\n🔍 Found '{field}' field:")
                            if isinstance(data[field], list):
                                print(f"  - Count: {len(data[field])}")
                                if data[field]:
                                    print(f"  - Sample: {json.dumps(data[field][0], indent=4)[:200]}...")
                            else:
                                print(f"  - Content: {json.dumps(data[field], indent=4)[:200]}...")
                
            except json.JSONDecodeError:
                print(f"\n📄 Raw Content (not JSON):")
                print(value[:500] + "..." if len(value) > 500 else value)
        
        elif key_type == 'hash':
            fields = r.hgetall(key)
            print(f"\n🗂️ Hash Fields ({len(fields)}):")
            for field, value in fields.items():
                print(f"  - {field}: {value[:100]}..." if len(value) > 100 else f"  - {field}: {value}")
        
        elif key_type == 'list':
            length = r.llen(key)
            print(f"\n📋 List Length: {length}")
            if length > 0:
                # Get all items for analysis
                items = r.lrange(key, 0, -1)
                print(f"📋 Items:")
                for idx, item in enumerate(items[:5]):  # Show first 5
                    try:
                        parsed = json.loads(item)
                        print(f"\n  Item {idx+1}:")
                        print(json.dumps(parsed, indent=4)[:300] + "..." if len(json.dumps(parsed)) > 300 else json.dumps(parsed, indent=4))
                    except:
                        print(f"\n  Item {idx+1}: {item[:200]}..." if len(item) > 200 else f"\n  Item {idx+1}: {item}")
                
                if length > 5:
                    print(f"\n  ... and {length - 5} more items")
        
        # Check TTL
        ttl = r.ttl(key)
        if ttl > 0:
            print(f"\n⏰ TTL: {ttl} seconds ({ttl // 3600} hours, {(ttl % 3600) // 60} minutes)")
        elif ttl == -1:
            print(f"\n⏰ TTL: No expiration")
        
        # Pause after first few for readability
        if i == 2 and len(thread_keys) > 3:
            print(f"\n\n{'='*60}")
            print(f"... showing first 3 threads. {len(thread_keys) - 3} more threads available.")
            break

def export_threads_to_files(r: redis.Redis, output_dir: str = "raw"):
    """Export thread data to text files"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all thread keys
    thread_keys = []
    cursor = 0
    while True:
        cursor, batch = r.scan(cursor, match="thread_*", count=100)
        thread_keys.extend(batch)
        if cursor == 0:
            break
    
    thread_keys.sort()
    
    print(f"\n📁 Exporting {len(thread_keys)} threads to {output_dir}/ directory...")
    
    for key in thread_keys:
        # Create filename from key
        filename = f"{key}.txt"
        filepath = os.path.join(output_dir, filename)
        
        key_type = r.type(key)
        
        with open(filepath, 'w') as f:
            f.write(f"Key: {key}\n")
            f.write(f"Type: {key_type}\n")
            f.write(f"{'='*60}\n\n")
            
            if key_type == 'string':
                value = r.get(key)
                try:
                    data = json.loads(value)
                    f.write(json.dumps(data, indent=2))
                except:
                    f.write(value)
            
            elif key_type == 'list':
                items = r.lrange(key, 0, -1)
                f.write(f"List with {len(items)} items:\n\n")
                for i, item in enumerate(items):
                    f.write(f"Item {i+1}:\n")
                    f.write("-" * 40 + "\n")
                    try:
                        data = json.loads(item)
                        f.write(json.dumps(data, indent=2))
                    except:
                        f.write(item)
                    f.write("\n\n")
            
            elif key_type == 'hash':
                fields = r.hgetall(key)
                f.write(f"Hash with {len(fields)} fields:\n\n")
                for field, value in fields.items():
                    f.write(f"{field}:\n")
                    f.write("-" * 40 + "\n")
                    try:
                        data = json.loads(value)
                        f.write(json.dumps(data, indent=2))
                    except:
                        f.write(value)
                    f.write("\n\n")
        
        print(f"  ✓ Exported: {filename}")
    
    print(f"\n✅ Export complete! Files saved to {output_dir}/")

def main():
    r = connect_to_redis()
    
    # Examine thread keys
    examine_thread_keys(r)
    
    # Ask if we should export
    print("\n" + "="*60)
    print("\n📤 Ready to export all threads to raw/ folder")
    print("This will create text files for each thread key.")
    
    # Export to files
    export_threads_to_files(r)

if __name__ == "__main__":
    main()