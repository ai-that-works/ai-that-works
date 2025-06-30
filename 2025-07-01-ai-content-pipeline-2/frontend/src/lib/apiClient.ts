import type {
  EmailDraft,
  LinkedInPost,
  TwitterThread,
} from "@/baml_client/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8011";

// Type aliases for consistency with existing code
type XDraft = TwitterThread;
type LinkedInDraft = LinkedInPost;

interface DraftContent {
  email_draft: EmailDraft | null;
  x_draft: XDraft | null;
  linkedin_draft: LinkedInDraft | null;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: response.statusText }));
    throw new Error(
      errorData.message || `API request failed with status ${response.status}`,
    );
  }
  return response.json() as Promise<T>;
}

export const api = {
  summarizeVideo: async (videoId: string): Promise<any> => {
    const response = await fetch(
      `${API_BASE_URL}/videos/${videoId}/summarize`,
      {
        method: "POST",
      },
    );
    return handleResponse(response);
  },

  getTranscript: async (videoId: string): Promise<string> => {
    const response = await fetch(
      `${API_BASE_URL}/videos/${videoId}/transcript`,
    );
    const data = await handleResponse<{ transcript: string }>(response);
    return data.transcript;
  },

  saveDraft: async (
    videoId: string,
    draftContent: DraftContent,
    _version?: number,
  ): Promise<any> => {
    console.log("🌐 API Call - Save Draft:", {
      videoId,
      draftContent,
      url: `${API_BASE_URL}/videos/${videoId}/drafts`,
    });

    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/drafts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(draftContent),
    });

    const result = await handleResponse(response);
    console.log("🌐 API Response - Save Draft:", result);
    return result;
  },

  refineContent: async (
    videoId: string,
    feedback: string,
    contentType: "email" | "x" | "linkedin",
    currentDraft: any,
  ): Promise<any> => {
    console.log("🌐 API Call - Refine Content:", {
      videoId,
      feedback,
      contentType,
      currentDraft,
      url: `${API_BASE_URL}/videos/${videoId}/refine-content`,
    });

    const response = await fetch(
      `${API_BASE_URL}/videos/${videoId}/refine-content`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          feedback,
          content_type: contentType,
          current_draft: currentDraft,
        }),
      },
    );

    const result = await handleResponse(response);
    console.log("🌐 API Response - Refine Content:", result);
    return result;
  },

  generateTitle: async (videoId: string): Promise<any> => {
    console.log("🌐 API Call - Generate Title:", {
      videoId,
      url: `${API_BASE_URL}/videos/${videoId}/generate-title`,
    });

    const response = await fetch(
      `${API_BASE_URL}/videos/${videoId}/generate-title`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      },
    );

    const result = await handleResponse(response);
    console.log("🌐 API Response - Generate Title:", result);
    return result;
  },

  updateTitle: async (videoId: string, title: string): Promise<any> => {
    console.log("🌐 API Call - Update Title:", {
      videoId,
      title,
      url: `${API_BASE_URL}/videos/${videoId}/title`,
    });

    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/title`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });

    const result = await handleResponse(response);
    console.log("🌐 API Response - Update Title:", result);
    return result;
  },

  createGitHubPR: async (
    videoId: string,
    nextEpisodeSummary: string,
    nextEpisodeLumaLink: string,
  ): Promise<{ pr_url: string; message: string }> => {
    console.log("🌐 API Call - Create GitHub PR:", {
      videoId,
      nextEpisodeSummary,
      nextEpisodeLumaLink,
      url: `${API_BASE_URL}/videos/${videoId}/create-github-pr`,
    });

    const response = await fetch(
      `${API_BASE_URL}/videos/${videoId}/create-github-pr`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          next_episode_summary: nextEpisodeSummary,
          next_episode_luma_link: nextEpisodeLumaLink,
        }),
      },
    );

    const result = await handleResponse(response);
    console.log("🌐 API Response - Create GitHub PR:", result);
    return result;
  },

  importVideo: async (data: {
    zoom_meeting_id: string;
    title: string;
    thumbnail_url: string;
  }): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/videos/import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  getZoomRecordings: async (params: {
    from_date: string;
    to_date: string;
  }): Promise<any> => {
    const queryParams = new URLSearchParams(params);
    const response = await fetch(
      `${API_BASE_URL}/zoom/recordings?${queryParams}`,
    );
    return handleResponse(response);
  },

  getLumaMatch: async (
    meetingId: string,
  ): Promise<{ matched: boolean; event: any }> => {
    const response = await fetch(
      `${API_BASE_URL}/zoom/recordings/${meetingId}/luma-match`,
    );
    return handleResponse(response);
  },

  getNextAIThatWorksEvent: async (): Promise<{
    found: boolean;
    event: {
      event_id: string;
      title: string;
      description: string;
      url: string;
      start_at: string;
      end_at: string;
      thumbnail_url: string;
    } | null;
  }> => {
    const response = await fetch(
      `${API_BASE_URL}/luma/next-ai-that-works-event`,
    );
    return handleResponse(response);
  },
};

// Export apiClient as an alias for api for compatibility
export const apiClient = api;

// NOTE: You'll need to implement the actual API routes (e.g., using Next.js Route Handlers)
// that these client-side functions will call.
