-- Supabase schema for AI Content Pipeline
-- Run this in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    duration INTEGER NOT NULL, -- seconds
    zoom_meeting_id TEXT NOT NULL,
    youtube_url TEXT,
    processing_stage TEXT NOT NULL DEFAULT 'queued', -- 'queued', 'downloading', 'uploading', 'ready', 'failed'
    status TEXT NOT NULL DEFAULT 'processing', -- 'processing', 'ready', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    summary_points TEXT[], -- Array of summary points
    transcript TEXT -- Full video transcript
);

-- Drafts table
CREATE TABLE IF NOT EXISTS drafts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    email_content TEXT NOT NULL,
    x_content TEXT NOT NULL,
    linkedin_content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    draft_id UUID NOT NULL REFERENCES drafts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_videos_zoom_meeting_id ON videos(zoom_meeting_id);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_processing_stage ON videos(processing_stage);
CREATE INDEX IF NOT EXISTS idx_drafts_video_id ON drafts(video_id);
CREATE INDEX IF NOT EXISTS idx_drafts_created_at ON drafts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_draft_id ON feedback(draft_id);

-- Row Level Security (RLS) policies
-- Enable RLS on all tables
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- For now, allow all operations (you can restrict this later based on your auth requirements)
CREATE POLICY "Allow all operations on videos" ON videos FOR ALL USING (true);
CREATE POLICY "Allow all operations on drafts" ON drafts FOR ALL USING (true);
CREATE POLICY "Allow all operations on feedback" ON feedback FOR ALL USING (true); 