const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface VideoImportRequest {
  zoom_meeting_id: string
}

export interface DraftUpdateRequest {
  email_content: string
  x_content: string
  linkedin_content: string
}

export interface FeedbackRequest {
  content: string
}

export const api = {
  // Import video from Zoom
  async importVideo(request: VideoImportRequest) {
    const response = await fetch(`${API_BASE_URL}/videos/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    return response.json()
  },

  // Trigger video summarization
  async summarizeVideo(videoId: string) {
    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/summarize`, {
      method: 'POST',
    })
    return response.json()
  },

  // Save draft
  async saveDraft(videoId: string, draft: DraftUpdateRequest) {
    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/drafts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(draft),
    })
    return response.json()
  },

  // Add feedback
  async addFeedback(draftId: string, feedback: FeedbackRequest) {
    const response = await fetch(`${API_BASE_URL}/drafts/${draftId}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feedback),
    })
    return response.json()
  },
} 