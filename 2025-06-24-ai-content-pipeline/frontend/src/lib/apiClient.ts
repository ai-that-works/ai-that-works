import type { EmailDraft, TwitterThread, LinkedInPost } from "@/baml_client/types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Type aliases for consistency with existing code
type XDraft = TwitterThread
type LinkedInDraft = LinkedInPost

interface DraftContent {
  email_draft: EmailDraft | null
  x_draft: XDraft | null  
  linkedin_draft: LinkedInDraft | null
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: response.statusText }))
    throw new Error(errorData.message || `API request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export const api = {
  summarizeVideo: async (videoId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/summarize`, {
      method: "POST",
    })
    return handleResponse(response)
  },

  getTranscript: async (videoId: string): Promise<string> => {
    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/transcript`)
    const data = await handleResponse<{ transcript: string }>(response)
    return data.transcript
  },

  saveDraft: async (videoId: string, draftContent: DraftContent, version?: number): Promise<any> => {
    console.log('🌐 API Call - Save Draft:', {
      videoId,
      draftContent,
      url: `${API_BASE_URL}/videos/${videoId}/drafts`
    })
    
    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/drafts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(draftContent),
    })
    
    const result = await handleResponse(response)
    console.log('🌐 API Response - Save Draft:', result)
    return result
  },

  getZoomRecordings: async (params: { from_date: string; to_date: string }): Promise<{ meetings: any[] }> => {
    const queryParams = new URLSearchParams(params).toString()
    const response = await fetch(`${API_BASE_URL}/zoom/recordings?${queryParams}`)
    return handleResponse(response)
  },

  importVideo: async (payload: { zoom_meeting_id: string }): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/videos/import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    return handleResponse(response)
  },
}

// NOTE: You'll need to implement the actual API routes (e.g., using Next.js Route Handlers)
// that these client-side functions will call.
