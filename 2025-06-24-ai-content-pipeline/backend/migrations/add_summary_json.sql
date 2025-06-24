-- Add summary JSONB field to store rich summary data from BAML
ALTER TABLE videos ADD COLUMN IF NOT EXISTS summary JSONB;

-- Create index for summary field for efficient querying
CREATE INDEX IF NOT EXISTS idx_videos_summary ON videos USING GIN (summary);