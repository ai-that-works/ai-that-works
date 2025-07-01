-- Migration: Add processing_stage column to videos table
-- Run this in your Supabase SQL editor if the column doesn't exist

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