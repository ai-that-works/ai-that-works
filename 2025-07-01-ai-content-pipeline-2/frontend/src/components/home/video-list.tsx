"use client";

import { Eye, ListVideo } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorMessage } from "@/components/shared/error-message";
import { LoadingIndicator } from "@/components/shared/loading-indicator";
import { YouTubeEmbed } from "@/components/shared/youtube-embed";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { supabase, type Video } from "@/lib/supabase";
import { formatDate, formatDuration } from "@/lib/utils";
import { getVideoStatusIcon } from "../shared/utils";

type FilterType = "all" | "processing" | "ready" | "failed";

interface VideoListProps {
  filter?: FilterType;
}

export function VideoList({ filter = "all" }: VideoListProps) {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVideos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let query = supabase
        .from("videos")
        .select("*")
        .order("created_at", { ascending: false });

      // Apply filter if not "all"
      if (filter !== "all") {
        query = query.eq("status", filter);
      }

      const { data, error: fetchError } = await query;

      if (fetchError) throw fetchError;
      setVideos(data || []);
    } catch (err) {
      console.error("Error fetching videos:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch videos.");
      setVideos([]);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchVideos();

    const channel = supabase
      .channel("videos-list")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "videos" },
        (payload) => {
          console.log("Videos list change received:", payload);
          toast.info("Video list updated.");
          fetchVideos();
        },
      )
      .subscribe((status, err) => {
        if (status === "SUBSCRIBED") {
          console.log("Subscribed to videos list changes");
        }
        if (err) {
          console.error("Error subscribing to videos list changes:", err);
          toast.error("Realtime video list update connection failed.");
        }
      });

    return () => {
      supabase.removeChannel(channel);
    };
  }, [fetchVideos]);

  if (loading) {
    return <LoadingIndicator text="Loading your videos..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        title="Could not load videos"
        message={error}
        onRetry={fetchVideos}
      />
    );
  }

  if (videos.length === 0) {
    const emptyStateMessages = {
      all: {
        title: "No Processed Videos Yet",
        description:
          "Once you import and process Zoom recordings, they will appear here.",
      },
      processing: {
        title: "No Processing Videos",
        description: "Videos currently being processed will appear here.",
      },
      ready: {
        title: "No Ready Videos",
        description: "Successfully processed videos will appear here.",
      },
      failed: {
        title: "No Failed Videos",
        description: "Videos that failed processing will appear here.",
      },
    };

    const message = emptyStateMessages[filter];

    return (
      <EmptyState
        Icon={ListVideo}
        title={message.title}
        description={message.description}
      />
    );
  }

  return (
    <div className="space-y-4">
      {videos.map((video) => (
        <Card key={video.id} className="macos-hover">
          <div className="flex gap-4 p-4">
            {/* YouTube Embed - Small size for home page */}
            {video.youtube_url && video.status === "ready" && (
              <div className="flex-shrink-0">
                <YouTubeEmbed
                  url={video.youtube_url}
                  size="small"
                  title={video.title || "Untitled Video"}
                  className="w-48"
                />
              </div>
            )}

            {/* Video Info */}
            <div className="flex-1 min-w-0">
              <CardHeader className="p-0">
                <div className="flex justify-between items-start gap-2">
                  <CardTitle className="macos-text-title2 line-clamp-2">
                    {video.title || "Untitled Video"}
                  </CardTitle>
                  <Badge
                    variant={video.status === "ready" ? "default" : "secondary"}
                    className="capitalize shrink-0"
                  >
                    {getVideoStatusIcon(video.status)}
                    <span className="ml-1.5">{video.status}</span>
                  </Badge>
                </div>
                <CardDescription className="macos-text-caption1 text-muted-foreground pt-1">
                  Created: {formatDate(video.created_at)} | Duration:{" "}
                  {formatDuration(video.duration)}
                </CardDescription>
              </CardHeader>

              <CardFooter className="p-0 pt-4 flex justify-end">
                <Link href={`/videos/${video.id}`} passHref legacyBehavior>
                  <Button size="sm" variant="default" asChild>
                    <a>
                      <Eye className="w-4 h-4 mr-2" />
                      View Details
                    </a>
                  </Button>
                </Link>
              </CardFooter>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
