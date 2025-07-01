"use client";

import { Loader2, RefreshCw, UploadCloud, VideoOff } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorMessage } from "@/components/shared/error-message";
import { LoadingIndicator } from "@/components/shared/loading-indicator";
import { getRecordingTypeIcon } from "@/components/shared/utils";
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
import {
  formatDate,
  formatFileSize,
  formatDuration as formatMeetingDuration,
} from "@/lib/utils";

// Define a more specific type for Zoom meetings if available from your API
interface ZoomRecordingFile {
  id: string;
  file_type: string;
  file_size: number;
  download_url: string; // Or play_url
  recording_type: string;
}
interface ZoomMeetingRecording {
  uuid: string; // Typically the meeting ID
  topic: string;
  start_time: string;
  end_time?: string; // Optional if meeting is ongoing or data is incomplete
  duration: number; // Duration in minutes
  total_size: number; // Total size of all recording files in bytes
  recording_count: number;
  recording_files: ZoomRecordingFile[];
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
  const [lumaMatches, setLumaMatches] = useState<Record<string, any>>({});
  const [checkingLuma, setCheckingLuma] = useState<Record<string, boolean>>({});

  const fetchRecordings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { from_date, to_date } = getLastNMonthsRange(3); // Fetch last 3 months
      // Ensure your API client handles the response structure correctly.
      // This assumes api.getZoomRecordings returns { meetings: ZoomMeetingRecording[] }
      const response = await api.getZoomRecordings({ from_date, to_date });
      setMeetings(response.meetings || []);
    } catch (err: any) {
      console.error("Error fetching Zoom recordings:", err);
      setError(
        err.message || "Failed to fetch Zoom recordings. Please try again.",
      );
      setMeetings([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecordings();
  }, [fetchRecordings]);

  // Check for Luma matches when meetings are loaded
  useEffect(() => {
    async function checkLumaMatches() {
      for (const meeting of meetings) {
        if (!lumaMatches[meeting.uuid] && !checkingLuma[meeting.uuid]) {
          setCheckingLuma((prev) => ({ ...prev, [meeting.uuid]: true }));
          try {
            const response = await api.getLumaMatch(meeting.uuid);
            setLumaMatches((prev) => ({ ...prev, [meeting.uuid]: response }));
          } catch (error) {
            console.error(
              `Failed to check Luma match for ${meeting.uuid}:`,
              error,
            );
            setLumaMatches((prev) => ({
              ...prev,
              [meeting.uuid]: { matched: false },
            }));
          } finally {
            setCheckingLuma((prev) => ({ ...prev, [meeting.uuid]: false }));
          }
        }
      }
    }

    if (meetings.length > 0) {
      checkLumaMatches();
    }
  }, [meetings, lumaMatches, checkingLuma]);

  const handleProcessMeeting = async (meeting: ZoomMeetingRecording) => {
    const lumaMatch = lumaMatches[meeting.uuid];

    if (!lumaMatch?.matched || !lumaMatch?.event) {
      toast.error(
        "No matching Luma event found. Cannot import this recording.",
      );
      return;
    }

    setProcessingMeetingId(meeting.uuid);

    // Use Luma event title and thumbnail
    const title = lumaMatch.event.title || meeting.topic;
    const thumbnail_url = lumaMatch.event.thumbnail_url || "";

    toast.promise(
      api.importVideo({
        zoom_meeting_id: meeting.uuid,
        title,
        thumbnail_url,
      }),
      {
        loading: `Processing meeting ${meeting.uuid}...`,
        success: () => {
          return `Meeting ${meeting.uuid} processing started!`;
        },
        error: (err) =>
          `Failed to process meeting ${meeting.uuid}: ${err.message || "Unknown error"}`,
        finally: () => setProcessingMeetingId(null),
      },
    );
  };

  const calculateDuration = (start: string, end?: string): string => {
    if (!end) return "N/A";
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();
    const durationInSeconds = Math.floor((endTime - startTime) / 1000);
    return formatMeetingDuration(durationInSeconds);
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
        <h2 className="text-2xl font-semibold">
          Zoom Recordings (Last 3 Months)
        </h2>
        <Button onClick={fetchRecordings} variant="outline" disabled={loading}>
          <RefreshCw
            className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {meetings.map((meeting) => (
          <Card key={meeting.uuid} className="flex flex-col">
            <CardHeader>
              <CardTitle className="text-lg line-clamp-2">
                {lumaMatches[meeting.uuid]?.matched &&
                lumaMatches[meeting.uuid]?.event
                  ? lumaMatches[meeting.uuid].event.title
                  : `Zoom Meeting ${meeting.uuid}`}
              </CardTitle>
              <CardDescription>
                {formatDate(meeting.start_time, {
                  dateStyle: "medium",
                  timeStyle: "short",
                })}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-grow space-y-3">
              <div className="text-sm text-muted-foreground space-y-1">
                <p>
                  Duration:{" "}
                  {meeting.duration
                    ? `${meeting.duration} min`
                    : calculateDuration(meeting.start_time, meeting.end_time)}
                </p>
                <p>Size: {formatFileSize(meeting.total_size)}</p>
                <p>Files: {meeting.recording_count}</p>
              </div>
              {meeting.recording_files &&
                meeting.recording_files.length > 0 && (
                  <div>
                    <h4 className="text-xs font-medium uppercase text-muted-foreground mb-1">
                      Recording Types:
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {meeting.recording_files.map((file) => (
                        <Badge
                          variant="secondary"
                          key={file.id}
                          className="text-xs"
                        >
                          {getRecordingTypeIcon(file.recording_type)}
                          <span className="ml-1">
                            {file.recording_type.replace(/_/g, " ")}
                          </span>
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
            </CardContent>
            <CardFooter className="flex flex-col gap-2">
              {checkingLuma[meeting.uuid] && (
                <div className="text-sm text-muted-foreground flex items-center">
                  <Loader2 className="h-3 w-3 animate-spin mr-2" />
                  Checking for Luma event...
                </div>
              )}

              {lumaMatches[meeting.uuid] &&
                !lumaMatches[meeting.uuid].matched && (
                  <div className="text-sm text-muted-foreground">
                    No matching Luma event found
                  </div>
                )}

              {lumaMatches[meeting.uuid]?.matched &&
                lumaMatches[meeting.uuid]?.event && (
                  <div className="text-sm text-green-600 dark:text-green-400">
                    ✓ Matched: {lumaMatches[meeting.uuid].event.title}
                  </div>
                )}

              <Button
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
                onClick={() => handleProcessMeeting(meeting)}
                disabled={
                  processingMeetingId === meeting.uuid ||
                  checkingLuma[meeting.uuid] ||
                  !lumaMatches[meeting.uuid]?.matched
                }
              >
                {processingMeetingId === meeting.uuid ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <UploadCloud className="w-4 h-4 mr-2" />
                )}
                {processingMeetingId === meeting.uuid
                  ? "Processing..."
                  : !lumaMatches[meeting.uuid]?.matched
                    ? "No Luma Event"
                    : "Import & Process"}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
