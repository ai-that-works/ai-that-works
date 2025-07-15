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
        # Test connection
        r.ping()
        print("✅ Connected to Redis successfully")
        return r
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        sys.exit(1)

def explore_keys(r: redis.Redis, pattern: str = "*", limit: int = 100):
    """Explore available keys in Redis"""
    print(f"\n🔍 Exploring keys with pattern '{pattern}' (limit: {limit})...")
    
    cursor = 0
    keys = []
    
    # Use SCAN to iterate through keys
    while len(keys) < limit:
        cursor, batch = r.scan(cursor, match=pattern, count=min(limit - len(keys), 100))
        keys.extend(batch)
        if cursor == 0:  # Completed full scan
            break
    
    keys = keys[:limit]
    print(f"📊 Found {len(keys)} keys")
    
    # Group keys by prefix/pattern
    key_groups = {}
    for key in keys:
        prefix = key.split(':')[0] if ':' in key else key.split('_')[0]
        key_groups.setdefault(prefix, []).append(key)
    
    print("\n📁 Key groups:")
    for prefix, group_keys in sorted(key_groups.items()):
        print(f"  {prefix}: {len(group_keys)} keys")
        # Show a few examples
        for i, key in enumerate(group_keys[:3]):
            print(f"    - {key}")
        if len(group_keys) > 3:
            print(f"    ... and {len(group_keys) - 3} more")
    
    return keys

def examine_key(r: redis.Redis, key: str):
    """Examine a specific key's type and content"""
    key_type = r.type(key)
    print(f"\n🔑 Key: {key}")
    print(f"📦 Type: {key_type}")
    
    try:
        if key_type == 'string':
            value = r.get(key)
            # Try to parse as JSON
            try:
                parsed = json.loads(value)
                print(f"📄 Value (JSON):")
                print(json.dumps(parsed, indent=2)[:500] + "..." if len(json.dumps(parsed)) > 500 else json.dumps(parsed, indent=2))
            except:
                print(f"📄 Value (string): {value[:200]}..." if len(value) > 200 else f"📄 Value: {value}")
        
        elif key_type == 'list':
            length = r.llen(key)
            print(f"📋 List length: {length}")
            if length > 0:
                sample = r.lrange(key, 0, 2)
                print(f"📋 First few items:")
                for item in sample:
                    print(f"  - {item[:100]}..." if len(item) > 100 else f"  - {item}")
        
        elif key_type == 'hash':
            fields = r.hkeys(key)
            print(f"🗂️ Hash fields ({len(fields)}): {', '.join(fields[:10])}")
            if len(fields) > 10:
                print(f"  ... and {len(fields) - 10} more fields")
            # Show a sample field
            if fields:
                sample_field = fields[0]
                sample_value = r.hget(key, sample_field)
                print(f"  Sample: {sample_field} = {sample_value[:100]}..." if len(sample_value) > 100 else f"  Sample: {sample_field} = {sample_value}")
        
        elif key_type == 'set':
            size = r.scard(key)
            print(f"🎯 Set size: {size}")
            if size > 0:
                sample = list(r.srandmember(key, min(3, size)))
                print(f"🎯 Random members:")
                for member in sample:
                    print(f"  - {member}")
        
        elif key_type == 'zset':
            size = r.zcard(key)
            print(f"📊 Sorted set size: {size}")
            if size > 0:
                sample = r.zrange(key, 0, 2, withscores=True)
                print(f"📊 Top members:")
                for member, score in sample:
                    print(f"  - {member} (score: {score})")
        
        # Check TTL
        ttl = r.ttl(key)
        if ttl > 0:
            print(f"⏰ TTL: {ttl} seconds ({ttl // 3600} hours)")
        elif ttl == -1:
            print(f"⏰ TTL: No expiration")
            
    except Exception as e:
        print(f"❌ Error examining key: {e}")

def find_trace_keys(r: redis.Redis, pattern: str = "*trace*"):
    """Find keys that might contain trace data"""
    print(f"\n🔍 Looking for trace-related keys...")
    
    # Common patterns for trace data
    patterns = [
        "*trace*",
        "*span*", 
        "*telemetry*",
        "*metric*",
        "*log*",
        "*event*",
        "*request*",
        "*debug*"
    ]
    
    all_keys = set()
    for pattern in patterns:
        keys = []
        cursor = 0
        while True:
            cursor, batch = r.scan(cursor, match=pattern, count=100)
            keys.extend(batch)
            if cursor == 0:
                break
            if len(keys) > 1000:  # Limit to prevent too many results
                break
        all_keys.update(keys[:1000])
        if keys:
            print(f"  ✓ Found {len(keys)} keys matching '{pattern}'")
    
    return list(all_keys)

def main():
    # Connect to Redis
    r = connect_to_redis()
    
    # Get basic info
    info = r.info()
    print(f"\n📊 Redis Info:")
    print(f"  - Version: {info.get('redis_version', 'Unknown')}")
    print(f"  - Used Memory: {info.get('used_memory_human', 'Unknown')}")
    print(f"  - Connected Clients: {info.get('connected_clients', 'Unknown')}")
    print(f"  - Total Keys: {r.dbsize()}")
    
    # Explore keys
    print("\n" + "="*60)
    all_keys = explore_keys(r, pattern="*", limit=200)
    
    # Look for trace-specific keys
    print("\n" + "="*60)
    trace_keys = find_trace_keys(r)
    
    if trace_keys:
        print(f"\n📍 Found {len(trace_keys)} potential trace keys")
        print("\n🔍 Examining first few trace keys:")
        for key in trace_keys[:5]:
            examine_key(r, key)
            print("\n" + "-"*40)
    
    # Let user know we're ready for next steps
    print("\n✅ Initial exploration complete!")
    print("\n📋 Next steps:")
    print("1. Identify specific trace keys to export")
    print("2. Export selected traces to raw/ folder")
    print("3. Parse and analyze trace data")

if __name__ == "__main__":
    main()