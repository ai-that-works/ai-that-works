"use client"

import { useEffect, useState, useCallback } from "react"
import { useParams, useRouter } from "next/navigation" // Added useRouter
import { supabase, type Video } from "@/lib/supabase" // Assuming supabase.ts is in lib
import { api } from "@/lib/apiClient" // Assuming apiClient.ts for client-side API calls
import { TranscriptViewer } from "@/components/video/transcript-viewer"
import { DraftEditor } from "@/components/video/draft-editor"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Sparkles, Clock, Loader2 } from "lucide-react"
import { toast } from "sonner"
import { formatDuration, formatDate } from "@/lib/utils"
import { LoadingIndicator } from "@/components/shared/loading-indicator"
import { ErrorMessage } from "@/components/shared/error-message"
import { YouTubeEmbed } from "@/components/shared/youtube-embed"
import { getVideoStatusIcon } from "@/components/shared/utils"

export default function VideoDetailPage() {
  const params = useParams()
  const router = useRouter() // For navigation
  const videoId = params.id as string

  const [video, setVideo] = useState<Video | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSummarizing, setIsSummarizing] = useState(false)
  const [realtimeStatus, setRealtimeStatus] = useState<string>("disconnected")

  const fetchVideo = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data, error: fetchError } = await supabase.from("videos").select("*").eq("id", videoId).single()

      if (fetchError) throw fetchError
      setVideo(data)
    } catch (err) {
      console.error("Error fetching video:", err)
      setError(err instanceof Error ? err.message : "Failed to fetch video details.")
      setVideo(null)
    } finally {
      setLoading(false)
    }
  }, [videoId])

  useEffect(() => {
    if (videoId) {
      fetchVideo()

      console.log(`🔗 Setting up real-time subscription for video ${videoId}`)
      
      const channel = supabase
        .channel(`video-${videoId}`, {
          config: {
            broadcast: { self: true },
            presence: { key: videoId },
            private: false
          }
        })
        .on(
          "postgres_changes",
          { 
            event: "*", 
            schema: "public", 
            table: "videos", 
            filter: `id=eq.${videoId}` 
          },
          (payload) => {
            console.log("🔔 Video change received:", payload)
            fetchVideo() // Refetch to get the latest data
          },
        )
        .on(
          "postgres_changes",
          { 
            event: "*", 
            schema: "public", 
            table: "drafts", 
            filter: `video_id=eq.${videoId}` 
          },
          (payload) => {
            console.log("🔔 Draft change received:", payload)
            // Notify DraftEditor component to update
            window.dispatchEvent(new CustomEvent(`draft-update-${videoId}`))
          },
        )
        .subscribe((status, err) => {
          console.log(`📡 Combined subscription status: ${status}`)
          setRealtimeStatus(status)
          
          if (status === "SUBSCRIBED") {
            console.log(`✅ Successfully subscribed to video-${videoId} changes (videos + drafts)`)
          } else if (status === "CHANNEL_ERROR") {
            console.error(`❌ Channel error for video-${videoId}:`, err)
          } else if (status === "TIMED_OUT") {
            console.error(`⏱️ Subscription timed out for video-${videoId}`)
          } else if (status === "CLOSED") {
            console.log(`🔌 Channel closed for video-${videoId}`)
          }
          if (err) {
            console.error(`❌ Subscription error for video-${videoId}:`, err)
          }
        })

      return () => {
        supabase.removeChannel(channel)
      }
    }
  }, [videoId, fetchVideo])

  const handleSummarize = async () => {
    if (!videoId) return
    setIsSummarizing(true)
    toast.promise(api.summarizeVideo(videoId), {
      // Assuming api.summarizeVideo exists
      loading: "Generating summary...",
      success: () => {
        // fetchVideo() // Re-fetch video data to update summary if it's part of the video object
        return "Summary generation started! You will be notified upon completion."
      },
      error: (err) => {
        console.error("Error triggering summarization:", err)
        return `Failed to start summarization: ${err.message || "Unknown error"}`
      },
      finally: () => setIsSummarizing(false),
    })
  }

  if (loading && !video) {
    // Show full page loader only on initial load
    return <LoadingIndicator fullPage text="Loading video details..." />
  }

  if (error && !video) {
    // Show full page error if video couldn't be fetched at all
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 dark:from-slate-900 dark:to-gray-800 flex items-center justify-center p-4">
        <ErrorMessage title="Could not load video" message={error} onRetry={fetchVideo} />
      </div>
    )
  }

  if (!video) {
    // Fallback if video is null after loading and no error (should ideally not happen if error handling is robust)
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 dark:from-slate-900 dark:to-gray-800 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Video Not Found</CardTitle>
          </CardHeader>
          <CardContent>
            <p>The video you are looking for does not exist or could not be loaded.</p>
          </CardContent>
          <CardFooter>
            <Button onClick={() => router.back()} variant="outline">
              <ArrowLeft className="w-4 h-4 mr-2" /> Go Back
            </Button>
          </CardFooter>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Native macOS Toolbar */}
      <div className="macos-material-toolbar p-4 flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
          className="macos-focus"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back
        </Button>
        
        <div className="flex-1">
          <h1 className="macos-text-title1 text-foreground truncate">{video.title}</h1>
          <div className="flex items-center gap-4 mt-1">
            <span className="flex items-center gap-1 macos-text-callout text-muted-foreground">
              {getVideoStatusIcon(video.status)}
              <span className="capitalize">
                {video.status === "processing" && (video as any).processing_stage 
                  ? `${video.status} (${(video as any).processing_stage.replace('_', ' ')})`
                  : video.status
                }
              </span>
            </span>
            <span className="flex items-center gap-1 macos-text-callout text-muted-foreground">
              <Clock className="w-3 h-3" />
              {formatDuration(video.duration)}
            </span>
            <span className="macos-text-callout text-muted-foreground">
              {formatDate(video.created_at, { month: "short", day: "numeric", year: "numeric" })}
            </span>
            
            {/* Real-time Status Indicator */}
            <span className={`macos-text-caption1 px-2 py-1 rounded-full text-xs ${
              realtimeStatus === "SUBSCRIBED" 
                ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" 
                : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
            }`}>
              📡 {realtimeStatus === "SUBSCRIBED" ? "Live" : realtimeStatus}
            </span>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={handleSummarize}
            disabled={isSummarizing || video.status === "processing"}
          >
            {isSummarizing ? (
              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4 mr-1" />
            )}
            {video.summary_points && video.summary_points.length > 0 ? "Re-Summarize" : "Summarize"}
          </Button>
          
        </div>
      </div>

      {/* Content Area with native spacing */}
      <main className="flex-1 p-6 overflow-auto macos-scroll-area macos-scroll-fade">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Processing Status Card */}
          {video.status === "processing" && (
            <Card className="border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-950/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                  Processing in Progress
                </CardTitle>
                <CardDescription>
                  {(video as any).processing_stage === "summarizing" && "Analyzing video content and generating summary..."}
                  {(video as any).processing_stage === "generating_content" && "Creating drafts for email, X, and LinkedIn..."}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between macos-text-callout">
                    <span>Summary Generation</span>
                    <span className="text-green-600">
                      {(video as any).processing_stage === "generating_content" || video.summary_points ? "✓ Complete" : "⏳ Processing..."}
                    </span>
                  </div>
                  <div className="flex items-center justify-between macos-text-callout">
                    <span>Content Drafts</span>
                    <span className="text-blue-600">
                      {(video as any).processing_stage === "generating_content" ? "⏳ In Progress..." : "⌛ Waiting..."}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Summary Points Card */}
          {video.summary_points && video.summary_points.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Key Summary Points</CardTitle>
                <CardDescription>AI-generated key takeaways from the video</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {video.summary_points.map((point, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="flex-shrink-0 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center macos-text-caption2 font-semibold mt-0.5">
                        {index + 1}
                      </span>
                      <span className="macos-text-body text-foreground flex-1">{point}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Video and Transcript Section */}
          <div className={`grid gap-6 ${video.youtube_url && video.status === "ready" ? "lg:grid-cols-2" : "grid-cols-1"}`}>
            {/* YouTube Video Player */}
            {video.youtube_url && video.status === "ready" && (
              <Card>
                <CardHeader>
                  <CardTitle>Video Player</CardTitle>
                  <CardDescription>Watch the full video</CardDescription>
                </CardHeader>
                <CardContent>
                  <YouTubeEmbed 
                    url={video.youtube_url} 
                    size="large"
                    title={video.title || "Video"}
                  />
                </CardContent>
              </Card>
            )}

            {/* Transcript Viewer */}
            <Card>
              <CardHeader>
                <CardTitle>Transcript</CardTitle>
                <CardDescription>Full video transcript with timestamps</CardDescription>
              </CardHeader>
              <CardContent>
                <TranscriptViewer videoId={videoId} initialTranscript={video.transcript || ""} />
              </CardContent>
            </Card>
          </div>

          {/* Draft Editor Card */}
          <Card>
            <CardHeader>
              <CardTitle>Content Drafts</CardTitle>
              <CardDescription>Create and manage content for different platforms</CardDescription>
            </CardHeader>
            <CardContent>
              <DraftEditor videoId={videoId} />
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
