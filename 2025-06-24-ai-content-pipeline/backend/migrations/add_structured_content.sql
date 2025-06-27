-- Replace text fields with structured JSON fields for better content management
ALTER TABLE drafts DROP COLUMN IF EXISTS email_content;
ALTER TABLE drafts DROP COLUMN IF EXISTS x_content;
ALTER TABLE drafts DROP COLUMN IF EXISTS linkedin_content;

-- Add structured content fields
ALTER TABLE drafts ADD COLUMN email_draft JSONB;
ALTER TABLE drafts ADD COLUMN x_draft JSONB;
ALTER TABLE drafts ADD COLUMN linkedin_draft JSONB;

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_drafts_email_draft ON drafts USING GIN (email_draft);
CREATE INDEX IF NOT EXISTS idx_drafts_x_draft ON drafts USING GIN (x_draft);
CREATE INDEX IF NOT EXISTS idx_drafts_linkedin_draft ON drafts USING GIN (linkedin_draft);