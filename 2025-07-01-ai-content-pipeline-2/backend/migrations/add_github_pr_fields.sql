-- Add GitHub PR tracking fields to videos table
ALTER TABLE videos ADD COLUMN github_pr_url TEXT;
ALTER TABLE videos ADD COLUMN episode_path TEXT;
ALTER TABLE videos ADD COLUMN github_pr_created_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE videos ADD COLUMN github_pr_created_by TEXT;