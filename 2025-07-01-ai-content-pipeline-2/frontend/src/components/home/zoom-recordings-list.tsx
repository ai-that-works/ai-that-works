"use client";

import { Loader2, RefreshCw, UploadCloud, VideoOff } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorMessage } from "@/components/shared/error-message";
import { LoadingIndicator } from "@/components/shared/loading-indicator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api } from "@/lib/apiClient"; // Assuming apiClient.ts
import { formatDate, formatDuration, formatFileSize } from "@/lib/utils";
import { getRecordingTypeIcon } from "../shared/utils";

// Backend-matching types for Zoom meetings
interface ZoomRecording {
  meeting_id: string;
  meeting_title: string;
  recording_id: string;
  recording_type: string;
  file_size: number;
  recording_start?: string;
  recording_end?: string;
  download_url?: string;
  file_extension: string;
  status: string;
  duration?: number;
}

interface ZoomMeetingRecording {
  meeting_id: string;
  meeting_title: string;
  recording_start: string;
  recording_end: string;
  recordings: ZoomRecording[];
  luma_event?: {
    event_id: string;
    title: string;
    thumbnail_url?: string;
    description?: string;
    url?: string;
  };
}

function getLastNMonthsRange(months: number) {
  const to = new Date();
  const from = new Date();
  from.setMonth(from.getMonth() - months);
  return {
    from_date: from.toISOString().slice(0, 10),
    to_date: to.toISOString().slice(0, 10),
  };
}

export function ZoomRecordingsList() {
  const [meetings, setMeetings] = useState<ZoomMeetingRecording[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingMeetingId, setProcessingMeetingId] = useState<string | null>(
    null,
  );

  const fetchRecordings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { from_date, to_date } = getLastNMonthsRange(3); // Fetch last 3 months
      // Ensure your API client handles the response structure correctly.
      // This assumes api.getZoomRecordings returns { meetings: ZoomMeetingRecording[] }
      const response = await api.getZoomRecordings({ from_date, to_date });
      const meetings = response.meetings || [];

      // Check for Luma matches for each meeting
      const meetingsWithLuma = await Promise.all(
        meetings.map(async (meeting) => {
          try {
            const lumaMatch = await api.getLumaMatch(meeting.meeting_id);
            if (lumaMatch.matched && lumaMatch.event) {
              return { ...meeting, luma_event: lumaMatch.event };
            }
            // Check if there's an error message indicating missing API key
            if (lumaMatch.error) {
              console.warn(
                `Luma API issue for ${meeting.meeting_id}: ${lumaMatch.error}`,
              );
            }
          } catch (err) {
            console.error(
              `Error checking Luma match for ${meeting.meeting_id}:`,
              err,
            );
          }
          return meeting;
        }),
      );

      setMeetings(meetingsWithLuma);
    } catch (err) {
      console.error("Error fetching Zoom recordings:", err);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to fetch Zoom recordings. Please try again.",
      );
      setMeetings([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecordings();
  }, [fetchRecordings]);

  const handleProcessMeeting = async (meeting: ZoomMeetingRecording) => {
    if (!meeting.luma_event) {
      toast.error(
        "No Luma event found for this recording. Cannot process without event details.",
      );
      return;
    }

    setProcessingMeetingId(meeting.meeting_id);
    toast.promise(
      api.importVideo({
        zoom_meeting_id: meeting.meeting_id,
        title: meeting.luma_event.title,
        thumbnail_url: meeting.luma_event.thumbnail_url || "",
      }),
      {
        loading: `Processing "${meeting.luma_event.title}"...`,
        success: () => {
          return `Started processing "${meeting.luma_event.title}"!`;
        },
        error: (err) => `Failed to process: ${err.message || "Unknown error"}`,
        finally: () => setProcessingMeetingId(null),
      },
    );
  };

  const calculateDuration = (start: string, end: string): string => {
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();
    const durationInSeconds = Math.floor((endTime - startTime) / 1000);
    return formatDuration(durationInSeconds);
  };

  if (loading) {
    return <LoadingIndicator text="Fetching Zoom recordings..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        title="Could not load recordings"
        message={error}
        onRetry={fetchRecordings}
      />
    );
  }

  if (meetings.length === 0) {
    return (
      <EmptyState
        Icon={VideoOff}
        title="No Zoom Recordings Found"
        description="We couldn't find any Zoom recordings from the last 3 months."
        action={
          <Button onClick={fetchRecordings} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        }
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="macos-text-title1 text-foreground font-semibold">
          Zoom Recordings (Last 3 Months)
        </h2>
        <Button onClick={fetchRecordings} variant="outline" disabled={loading}>
          <RefreshCw
            className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        {meetings.map((meeting) => {
          const totalSize = meeting.recordings.reduce(
            (sum, rec) => sum + rec.file_size,
            0,
          );
          const duration = calculateDuration(
            meeting.recording_start,
            meeting.recording_end,
          );

          return (
            <Card
              key={meeting.meeting_id}
              className={`flex flex-col macos-hover ${meeting.luma_event ? "border-green-500" : "border-orange-500"}`}
            >
              {meeting.luma_event?.thumbnail_url && (
                <div className="relative h-48 w-full overflow-hidden rounded-t-lg">
                  <img
                    src={meeting.luma_event.thumbnail_url}
                    alt={meeting.luma_event.title}
                    className="h-full w-full object-cover"
                  />
                </div>
              )}
              <CardHeader>
                <CardTitle className="macos-text-title3 line-clamp-2">
                  {meeting.luma_event
                    ? meeting.luma_event.title
                    : meeting.meeting_title}
                </CardTitle>
                <CardDescription>
                  {formatDate(meeting.recording_start, {
                    dateStyle: "medium",
                    timeStyle: "short",
                  })}
                  {meeting.luma_event && (
                    <Badge variant="outline" className="ml-2 text-green-600">
                      Luma Event Matched
                    </Badge>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-grow space-y-3">
                <div className="macos-text-callout text-muted-foreground space-y-1">
                  <p>Duration: {duration}</p>
                  <p>Size: {formatFileSize(totalSize)}</p>
                  <p>Files: {meeting.recordings.length}</p>
                </div>
                {meeting.recordings && meeting.recordings.length > 0 && (
                  <div>
                    <h4 className="macos-text-caption2 font-medium uppercase text-muted-foreground mb-1">
                      Recording Types:
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {meeting.recordings.map((recording: ZoomRecording) => (
                        <Badge
                          variant="secondary"
                          key={recording.recording_id}
                          className="macos-text-caption1"
                        >
                          {getRecordingTypeIcon(recording.recording_type)}
                          <span className="ml-1">
                            {recording.recording_type.replace(/_/g, " ")}
                          </span>
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
              <CardFooter>
                {!meeting.luma_event && (
                  <div className="w-full text-center text-sm text-orange-600 mb-2">
                    No matching Luma event found
                  </div>
                )}
                <Button
                  className="w-full"
                  variant={meeting.luma_event ? "default" : "secondary"}
                  onClick={() => handleProcessMeeting(meeting)}
                  disabled={
                    processingMeetingId === meeting.meeting_id ||
                    !meeting.luma_event
                  }
                >
                  {processingMeetingId === meeting.meeting_id ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <UploadCloud className="w-4 h-4 mr-2" />
                  )}
                  {processingMeetingId === meeting.meeting_id
                    ? "Processing..."
                    : !meeting.luma_event
                      ? "Luma Event Required"
                      : "Import & Process"}
                </Button>
              </CardFooter>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
