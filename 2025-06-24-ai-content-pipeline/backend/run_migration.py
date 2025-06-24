#!/usr/bin/env python3
"""
Migration script to add processing_stage column to videos table
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to add processing_stage column"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        sys.exit(1)
    
    try:
        # Create Supabase client
        client: Client = create_client(supabase_url, supabase_key)
        
        # Migration SQL
        migration_sql = """
        -- Add processing_stage column if it doesn't exist
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'videos' AND column_name = 'processing_stage'
            ) THEN
                ALTER TABLE videos ADD COLUMN processing_stage TEXT NOT NULL DEFAULT 'queued';
            END IF;
        END $$;

        -- Add index for processing_stage if it doesn't exist
        CREATE INDEX IF NOT EXISTS idx_videos_processing_stage ON videos(processing_stage);

        -- Update existing records to have a default processing_stage
        UPDATE videos SET processing_stage = 'queued' WHERE processing_stage IS NULL;
        """
        
        # Execute migration
        result = client.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        print("✅ Migration completed successfully!")
        print("Added processing_stage column to videos table")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nAlternative: Run the SQL manually in your Supabase SQL editor:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Run the SQL from migrations/add_processing_stage.sql")
        sys.exit(1)

if __name__ == "__main__":
    run_migration() 