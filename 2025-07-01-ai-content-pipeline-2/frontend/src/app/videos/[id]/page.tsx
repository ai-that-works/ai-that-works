"use client";

import {
  ArrowLeft,
  Check,
  Clock,
  Edit3,
  Loader2,
  RotateCcw,
  Sparkles,
  X,
} from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { CreateGitHubPRButton } from "@/components/github/CreateGitHubPRButton";
import { ErrorMessage } from "@/components/shared/error-message";
import { LoadingIndicator } from "@/components/shared/loading-indicator";
import { getVideoStatusIcon } from "@/components/shared/utils";
import { YouTubeEmbed } from "@/components/shared/youtube-embed";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { DraftEditor } from "@/components/video/draft-editor";
import { TranscriptViewer } from "@/components/video/transcript-viewer";
import { api } from "@/lib/apiClient";
import { supabase, type Video } from "@/lib/supabase";
import { formatDate, formatDuration } from "@/lib/utils";

export default function VideoDetailPage() {
  const params = useParams();
  const router = useRouter(); // For navigation
  const videoId = params.id as string;

  const [video, setVideo] = useState<Video | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState("");
  const [isSavingTitle, setIsSavingTitle] = useState(false);
  const [realtimeStatus, setRealtimeStatus] = useState<string>("disconnected");
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const fetchVideo = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data, error: fetchError } = await supabase
        .from("videos")
        .select("*")
        .eq("id", videoId)
        .single();

      if (fetchError) throw fetchError;
      setVideo(data);
    } catch (err) {
      console.error("Error fetching video:", err);
      setError(
        err instanceof Error ? err.message : "Failed to fetch video details.",
      );
      setVideo(null);
    } finally {
      setLoading(false);
    }
  }, [videoId]);

  const setupRealtimeSubscription = useCallback(() => {
    console.log(`🔗 Setting up real-time subscription for video ${videoId}`);

    const channel = supabase
      .channel(`video-${videoId}`, {
        config: {
          broadcast: { self: true },
          presence: { key: videoId },
          private: false,
        },
      })
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "videos",
          filter: `id=eq.${videoId}`,
        },
        (payload) => {
          console.log("🔔 Video change received:", payload);
          fetchVideo();
        },
      )
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "drafts",
          filter: `video_id=eq.${videoId}`,
        },
        (payload) => {
          console.log("🔔 Draft change received:", payload);
          window.dispatchEvent(new CustomEvent(`draft-update-${videoId}`));
        },
      )
      .subscribe((status, err) => {
        console.log(`📡 Combined subscription status: ${status}`);
        setRealtimeStatus(status);

        if (status === "SUBSCRIBED") {
          console.log(
            `✅ Successfully subscribed to video-${videoId} changes (videos + drafts)`,
          );
          setReconnectAttempts(0); // Reset attempts on successful connection
        } else if (status === "CHANNEL_ERROR") {
          console.error(`❌ Channel error for video-${videoId}:`, err);
        } else if (status === "TIMED_OUT") {
          console.error(`⏱️ Subscription timed out for video-${videoId}`);
          // Auto-reconnect after timeout
          const maxAttempts = 3;
          if (reconnectAttempts < maxAttempts) {
            const delay = Math.min(5000 * 2 ** reconnectAttempts, 30000); // Exponential backoff, max 30s
            console.log(
              `🔄 Auto-reconnecting in ${delay / 1000}s (attempt ${reconnectAttempts + 1}/${maxAttempts})`,
            );
            setTimeout(() => {
              setReconnectAttempts((prev) => prev + 1);
              supabase.removeChannel(channel);
              setupRealtimeSubscription();
            }, delay);
          } else {
            console.log("🛑 Max reconnection attempts reached");
          }
        } else if (status === "CLOSED") {
          console.log(`🔌 Channel closed for video-${videoId}`);
        }
        if (err) {
          console.error(`❌ Subscription error for video-${videoId}:`, err);
        }
      });

    return channel;
  }, [videoId, fetchVideo, reconnectAttempts]);

  useEffect(() => {
    if (videoId) {
      fetchVideo();
      const channel = setupRealtimeSubscription();

      return () => {
        supabase.removeChannel(channel);
      };
    }
  }, [videoId, fetchVideo, setupRealtimeSubscription]);

  const handleSummarize = async () => {
    if (!videoId) return;
    setIsSummarizing(true);
    toast.promise(api.summarizeVideo(videoId), {
      // Assuming api.summarizeVideo exists
      loading: "Generating summary...",
      success: () => {
        // fetchVideo() // Re-fetch video data to update summary if it's part of the video object
        return "Summary generation started! You will be notified upon completion.";
      },
      error: (err) => {
        console.error("Error triggering summarization:", err);
        return `Failed to start summarization: ${err.message || "Unknown error"}`;
      },
      finally: () => setIsSummarizing(false),
    });
  };

  const handleReset = async () => {
    if (!videoId) return;
    setIsResetting(true);

    try {
      // Update video status to reset the processing state
      const { error } = await supabase
        .from("videos")
        .update({
          status: "ready",
          processing_stage: "ready",
        })
        .eq("id", videoId);

      if (error) {
        console.error("❌ Reset failed:", error);
        toast.error(`Failed to reset: ${error.message}`);
      } else {
        console.log("✅ Video status reset");
        toast.success(
          "Processing status reset. You can now re-trigger summarization.",
        );
        fetchVideo(); // Refresh to show updated status
      }
    } catch (err) {
      console.error("❌ Reset error:", err);
      toast.error("Failed to reset processing status");
    } finally {
      setIsResetting(false);
    }
  };

  // Handle title editing
  const startTitleEdit = () => {
    setEditedTitle(video?.title || "");
    setIsEditingTitle(true);
  };

  const cancelTitleEdit = () => {
    setIsEditingTitle(false);
    setEditedTitle("");
  };

  const saveTitleEdit = async () => {
    if (!videoId || !editedTitle.trim()) return;

    setIsSavingTitle(true);
    try {
      await api.updateTitle(videoId, editedTitle.trim());
      setIsEditingTitle(false);
      toast.success("Title updated successfully!");
    } catch (error: any) {
      console.error("Error updating title:", error);
      toast.error(
        `Failed to update title: ${error.message || "Unknown error"}`,
      );
    } finally {
      setIsSavingTitle(false);
    }
  };

  if (loading && !video) {
    // Show full page loader only on initial load
    return <LoadingIndicator fullPage text="Loading video details..." />;
  }

  if (error && !video) {
    // Show full page error if video couldn't be fetched at all
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 dark:from-slate-900 dark:to-gray-800 flex items-center justify-center p-4">
        <ErrorMessage
          title="Could not load video"
          message={error}
          onRetry={fetchVideo}
        />
      </div>
    );
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
            <p>
              The video you are looking for does not exist or could not be
              loaded.
            </p>
          </CardContent>
          <CardFooter>
            <Button onClick={() => router.back()} variant="outline">
              <ArrowLeft className="w-4 h-4 mr-2" /> Go Back
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
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
          {isEditingTitle ? (
            <div className="flex items-center gap-2">
              <Input
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                className="macos-text-title1 font-bold border-2 border-blue-500"
                placeholder="Enter video title..."
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    saveTitleEdit();
                  } else if (e.key === "Escape") {
                    cancelTitleEdit();
                  }
                }}
                autoFocus
              />
              <div className="flex gap-1">
                <Button
                  size="sm"
                  onClick={saveTitleEdit}
                  disabled={isSavingTitle || !editedTitle.trim()}
                >
                  {isSavingTitle ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Check className="w-4 h-4" />
                  )}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={cancelTitleEdit}
                  disabled={isSavingTitle}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <h1 className="macos-text-title1 text-foreground truncate">
                {video.title}
              </h1>
              <Button
                size="sm"
                variant="ghost"
                onClick={startTitleEdit}
                className="opacity-60 hover:opacity-100"
              >
                <Edit3 className="w-4 h-4" />
              </Button>
            </div>
          )}
          <div className="flex items-center gap-4 mt-1">
            <span className="flex items-center gap-1 macos-text-callout text-muted-foreground">
              {getVideoStatusIcon(video.status)}
              <span className="capitalize">
                {video.status === "processing" &&
                (video as any).processing_stage
                  ? `${video.status} (${(video as any).processing_stage.replace("_", " ")})`
                  : video.status}
              </span>
            </span>
            <span className="flex items-center gap-1 macos-text-callout text-muted-foreground">
              <Clock className="w-3 h-3" />
              {formatDuration(video.duration)}
            </span>
            <span className="macos-text-callout text-muted-foreground">
              {formatDate(video.created_at, {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </span>

            {/* Real-time Status Indicator */}
            <span
              className={`macos-text-caption1 px-2 py-1 rounded-full text-xs ${
                realtimeStatus === "SUBSCRIBED"
                  ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                  : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
              }`}
            >
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
            {(video.summary_points && video.summary_points.length > 0) ||
            video.summary
              ? "Re-Summarize"
              : "Summarize"}
          </Button>

          <CreateGitHubPRButton
            video={video}
            onSuccess={(prUrl) => {
              console.log("GitHub PR created:", prUrl);
              // Optionally refresh the video data to show the PR URL
            }}
          />
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
                  {(video as any).processing_stage === "summarizing" &&
                    "Analyzing video content and generating summary..."}
                  {(video as any).processing_stage === "generating_content" &&
                    "Creating drafts for email, X, and LinkedIn..."}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between macos-text-callout">
                      <span>Summary Generation</span>
                      <span className="text-green-600">
                        {(video as any).processing_stage ===
                          "generating_content" || video.summary_points
                          ? "✓ Complete"
                          : "⏳ Processing..."}
                      </span>
                    </div>
                    <div className="flex items-center justify-between macos-text-callout">
                      <span>Content Drafts</span>
                      <span className="text-blue-600">
                        {(video as any).processing_stage ===
                        "generating_content"
                          ? "⏳ In Progress..."
                          : "⌛ Waiting..."}
                      </span>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-blue-200 dark:border-blue-800">
                    <p className="macos-text-caption1 text-muted-foreground mb-3">
                      If processing appears stuck, you can reset the status and
                      retry.
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleReset}
                      disabled={isResetting}
                      className="border-red-200 text-red-700 hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950"
                    >
                      {isResetting ? (
                        <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                      ) : (
                        <RotateCcw className="w-4 h-4 mr-1" />
                      )}
                      {isResetting ? "Resetting..." : "Reset Processing"}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Video and Transcript Section */}
          <div
            className={`grid gap-6 ${video.youtube_url ? "lg:grid-cols-2" : "grid-cols-1"}`}
          >
            {/* YouTube Video Player */}
            {video.youtube_url && (
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
                <CardDescription>
                  Full video transcript with timestamps
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TranscriptViewer
                  videoId={videoId}
                  initialTranscript={video.transcript || ""}
                />
              </CardContent>
            </Card>
          </div>

          {/* Video Summary Card */}
          {((video.summary_points && video.summary_points.length > 0) ||
            video.summary) && (
            <Card>
              <CardHeader>
                <CardTitle>Video Summary</CardTitle>
                <CardDescription>
                  AI-generated insights and key takeaways from the video
                </CardDescription>
              </CardHeader>
              <CardContent>
                {video.summary ? (
                  // New BAML structured summary
                  <div className="space-y-6">
                    {video.summary.timed_data &&
                      video.summary.timed_data.length > 0 && (
                        <div>
                          <h4 className="macos-text-title3 font-semibold mb-3">
                            Timeline Summary
                          </h4>
                          <div className="space-y-3">
                            {video.summary.timed_data.map((segment, index) => (
                              <div
                                key={index}
                                className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                              >
                                <div className="flex-shrink-0">
                                  <div className="macos-text-caption1 font-semibold text-primary">
                                    {segment.start_time} - {segment.end_time}
                                  </div>
                                </div>
                                <div className="flex-1">
                                  <p className="macos-text-body text-foreground">
                                    {segment.summary}
                                  </p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                    {video.summary.bullet_points &&
                      video.summary.bullet_points.length > 0 && (
                        <div>
                          <h4 className="macos-text-title3 font-semibold mb-3">
                            Key Points
                          </h4>
                          <ul className="space-y-2">
                            {video.summary.bullet_points.map((point, index) => (
                              <li
                                key={index}
                                className="flex items-start gap-3"
                              >
                                <span className="flex-shrink-0 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center macos-text-caption2 font-semibold mt-0.5">
                                  {index + 1}
                                </span>
                                <span className="macos-text-body text-foreground flex-1">
                                  {point}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                    {video.summary.key_topics &&
                      video.summary.key_topics.length > 0 && (
                        <div>
                          <h4 className="macos-text-title3 font-semibold mb-3">
                            Key Topics
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {video.summary.key_topics.map((topic, index) => (
                              <span
                                key={index}
                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                              >
                                {topic}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                    {video.summary.main_takeaways &&
                      video.summary.main_takeaways.length > 0 && (
                        <div>
                          <h4 className="macos-text-title3 font-semibold mb-3">
                            Main Takeaways
                          </h4>
                          <ul className="space-y-2">
                            {video.summary.main_takeaways.map(
                              (takeaway, index) => (
                                <li
                                  key={index}
                                  className="flex items-start gap-2"
                                >
                                  <span className="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mt-2"></span>
                                  <span className="macos-text-body text-foreground">
                                    {takeaway}
                                  </span>
                                </li>
                              ),
                            )}
                          </ul>
                        </div>
                      )}
                  </div>
                ) : (
                  // Legacy summary format
                  video.summary_points && (
                    <div>
                      <h4 className="macos-text-title3 font-semibold mb-3">
                        Summary Points
                      </h4>
                      <ul className="space-y-3">
                        {video.summary_points.map((point, index) => (
                          <li key={index} className="flex items-start gap-3">
                            <span className="flex-shrink-0 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center macos-text-caption2 font-semibold mt-0.5">
                              {index + 1}
                            </span>
                            <span className="macos-text-body text-foreground flex-1">
                              {point}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )
                )}
              </CardContent>
            </Card>
          )}

          {/* Draft Editor Card */}
          <Card>
            <CardHeader>
              <CardTitle>Content Drafts</CardTitle>
              <CardDescription>
                Create and manage content for different platforms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DraftEditor videoId={videoId} />
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
