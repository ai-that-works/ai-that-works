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

export interface ZoomRecording {
  meeting_id: string
  meeting_title: string
  recording_id: string
  recording_type: string
  file_size: number
  recording_start?: string
  recording_end?: string
  download_url?: string
  file_extension: string
  status: string
  duration?: number
}

export interface ZoomMeetingRecordings {
  meeting_id: string
  meeting_title: string
  recording_start: string
  recording_end: string
  recordings: ZoomRecording[]
}

export interface ZoomMeetingsResponse {
  meetings: ZoomMeetingRecordings[]
  total_count: number
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

  // Get Zoom recordings
  async getZoomRecordings(params?: {
    from_date?: string
    to_date?: string
    user_id?: string
  }): Promise<ZoomMeetingsResponse> {
    const searchParams = new URLSearchParams()
    if (params?.from_date) searchParams.append('from_date', params.from_date)
    if (params?.to_date) searchParams.append('to_date', params.to_date)
    if (params?.user_id) searchParams.append('user_id', params.user_id)
    
    const url = `${API_BASE_URL}/zoom/recordings${searchParams.toString() ? `?${searchParams.toString()}` : ''}`
    const response = await fetch(url)
    return response.json()
  },

  // Trigger video summarization
  async summarizeVideo(videoId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/summarize`, {
      method: 'POST',
    })
    
    if (!response.ok) {
      throw new Error(`Failed to trigger summarization: ${response.statusText}`)
    }
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

  async getTranscript(videoId: string): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/transcript`, {
    })
    
    if (!response.ok) {
      throw new Error(`Failed to get transcript: ${response.statusText}`)
    }
    
    const data = await response.json()
    return data.transcript
  },
} 