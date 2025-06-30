import { createClient } from "@supabase/supabase-js";
import type {
	EmailDraft,
	LinkedInPost,
	TwitterThread,
	VideoSummary,
} from "@/baml_client/types";

// Ensure these environment variables are correctly set in your Vercel project
// or .env.local file for local development.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl) {
	throw new Error("Missing env.NEXT_PUBLIC_SUPABASE_URL");
}
if (!supabaseAnonKey) {
	throw new Error("Missing env.NEXT_PUBLIC_SUPABASE_ANON_KEY");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
	realtime: {
		params: {
			eventsPerSecond: 10,
		},
		timeout: 120000, // 2 minutes
		heartbeatIntervalMs: 30000, // 30 seconds
	},
});

// Database types (ensure these match your table structures)
export interface Video {
	id: string;
	title: string;
	duration: number; // Assuming duration is in seconds
	youtube_url?: string | null;
	status: "processing" | "ready" | "failed" | "pending"; // Added 'pending' or other relevant statuses
	created_at: string;
	summary_points?: string[] | null; // Legacy field for backwards compatibility
	summary?: VideoSummary | null; // New structured summary from BAML
	transcript?: string | null; // Transcript might be fetched separately or stored here
}

// Use BAML-generated types
export type { EmailDraft, VideoSummary };
export type XDraft = TwitterThread;
export type LinkedInDraft = LinkedInPost;

export interface Draft {
	id: string;
	video_id: string;
	email_draft: EmailDraft | null;
	x_draft: XDraft | null;
	linkedin_draft: LinkedInDraft | null;
	created_at: string;
	version: number;
}

// You might have other types like Feedback, User, etc.
// export interface Feedback {
//   id: string;
//   draft_id: string;
//   content: string;
//   created_at: string;
// }
