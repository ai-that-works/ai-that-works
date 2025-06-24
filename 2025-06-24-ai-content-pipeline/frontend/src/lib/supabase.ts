import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://localhost:54321'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'dummy-key'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface Video {
  id: string
  title: string
  duration: number
  youtube_url?: string
  status: 'processing' | 'ready' | 'failed'
  created_at: string
  summary_points?: string[]
  transcript?: string
}

export interface Draft {
  id: string
  video_id: string
  email_content: string
  x_content: string
  linkedin_content: string
  created_at: string
  version: number
}

export interface Feedback {
  id: string
  draft_id: string
  content: string
  created_at: string
} 