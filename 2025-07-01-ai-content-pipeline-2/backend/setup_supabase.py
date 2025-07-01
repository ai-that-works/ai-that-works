#!/usr/bin/env python3
"""
Supabase Database Setup Script
Run this script to initialize your Supabase database with the required tables.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    # Check if Supabase credentials are set
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        print(
            "❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in your .env file"
        )
        print("\nPlease:")
        print("1. Copy env.template to .env")
        print("2. Fill in your Supabase credentials")
        print("3. Run this script again")
        sys.exit(1)

    # Read the schema file
    schema_file = Path(__file__).parent / "schema.sql"
    if not schema_file.exists():
        print("❌ Error: schema.sql not found")
        sys.exit(1)

    with open(schema_file, "r") as f:
        schema_sql = f.read()

    print("📋 Supabase Database Setup")
    print("=" * 40)
    print(f"Supabase URL: {supabase_url}")
    print(f"Schema file: {schema_file}")
    print()

    print("📝 To set up your database:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to the SQL Editor")
    print("3. Copy and paste the following SQL:")
    print()
    print("-" * 40)
    print(schema_sql)
    print("-" * 40)
    print()
    print("4. Click 'Run' to execute the schema")
    print("5. Your database will be ready!")
    print()

    # Test connection
    try:
        from supabase import create_client

        client = create_client(supabase_url, supabase_key)

        # Test a simple query
        result = client.table("videos").select("count", count="exact").execute()
        print("✅ Supabase connection successful!")
        print("✅ Database is accessible")

    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        print("Please check your credentials and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
