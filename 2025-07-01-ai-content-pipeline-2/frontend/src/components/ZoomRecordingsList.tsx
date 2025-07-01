"use client";

import { Calendar, Clock, FileText, Loader2, Video } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { api, type ZoomMeetingRecordings } from "@/lib/api";

function getLast3MonthsRange() {
  const to = new Date();
  const from = new Date();
  from.setMonth(from.getMonth() - 3);
  return {
    from_date: from.toISOString().slice(0, 10),
    to_date: to.toISOString().slice(0, 10),
  };
}

export function ZoomRecordingsList() {
  const [meetings, setMeetings] = useState<ZoomMeetingRecordings[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [processing, setProcessing] = useState<string | null>(null);

  const fetchRecordings = async () => {
    setLoading(true);
    setError("");
    try {
      const { from_date, to_date } = getLast3MonthsRange();
      const response = await api.getZoomRecordings({ from_date, to_date });
      setMeetings(response.meetings);
    } catch (err) {
      setError("Failed to fetch Zoom recordings");
      console.error("Error fetching recordings:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecordings();
  }, [fetchRecordings]);

  const formatFileSize = (bytes: number) => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatDuration = (start: string, end: string) => {
    const startTime = new Date(start);
    const endTime = new Date(end);
    const diffMs = endTime.getTime() - startTime.getTime();
    const diffMins = Math.round(diffMs / 60000);
    return `${diffMins} min`;
  };

  const getRecordingIcon = (type: string) => {
    switch (type) {
      case "shared_screen_with_speaker_view":
      case "shared_screen_with_speaker_view(CC)":
        return <Video className="w-4 h-4 text-blue-600" />;
      case "audio_only":
        return <FileText className="w-4 h-4 text-green-600" />;
      case "audio_transcript":
        return <FileText className="w-4 h-4 text-purple-600" />;
      default:
        return <FileText className="w-4 h-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32 bg-white rounded-xl shadow-sm">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 bg-white rounded-xl shadow-sm">
        <div className="text-red-600 mb-4 font-medium">{error}</div>
        <Button
          onClick={fetchRecordings}
          className="bg-blue-600 hover:bg-blue-700"
        >
          Retry
        </Button>
      </div>
    );
  }

  if (meetings.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-xl shadow-sm">
        <div className="text-gray-400 mb-4">
          <Video className="w-12 h-12 mx-auto" />
        </div>
        <p className="text-gray-500 text-lg">No Zoom recordings found</p>
        <Button onClick={fetchRecordings} variant="outline" className="mt-4">
          Refresh
        </Button>
      </div>
    );
  }

  const handleProcess = async (meetingId: string) => {
    setProcessing(meetingId);
    try {
      await api.importVideo({ zoom_meeting_id: meetingId });
      alert("Processing started for this meeting!");
    } catch {
      alert("Failed to process meeting");
    } finally {
      setProcessing(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">
          Zoom Recordings
        </h2>
        <Button
          onClick={fetchRecordings}
          variant="outline"
          size="sm"
          className="border-gray-300"
        >
          Refresh
        </Button>
      </div>
      {meetings.map((meeting) => (
        <div
          key={meeting.meeting_id}
          className="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 p-6 border border-gray-100"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="min-w-0 flex-1">
              <h3 className="font-semibold text-gray-900 text-lg mb-2 truncate">
                {meeting.meeting_title}
              </h3>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span className="flex items-center">
                  <Calendar className="w-3 h-3 mr-1" />
                  {formatDate(meeting.recording_start)}
                </span>
                <span className="flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {formatDuration(
                    meeting.recording_start,
                    meeting.recording_end,
                  )}
                </span>
              </div>
            </div>
            <span className="text-xs text-gray-400 font-mono bg-gray-50 px-2 py-1 rounded">
              ID: {meeting.meeting_id}
            </span>
          </div>
          <Button
            size="sm"
            className="w-full mb-4 bg-green-600 hover:bg-green-700 text-white font-medium"
            onClick={() => handleProcess(meeting.meeting_id)}
            disabled={processing === meeting.meeting_id}
          >
            {processing === meeting.meeting_id ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Processing...
              </>
            ) : (
              "Process Recording"
            )}
          </Button>
          <div className="grid gap-3">
            {meeting.recordings.map((recording) => (
              <div
                key={recording.recording_id}
                className="flex items-center justify-between border border-gray-200 rounded-lg px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-3 min-w-0 flex-1">
                  {getRecordingIcon(recording.recording_type)}
                  <div className="min-w-0 flex-1">
                    <span className="text-gray-800 text-sm font-medium capitalize block truncate">
                      {recording.recording_type.replace(/_/g, " ")}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatFileSize(recording.file_size)}
                    </span>
                  </div>
                </div>
                <span
                  className={`px-3 py-1 text-xs rounded-full font-medium ${
                    recording.status === "completed"
                      ? "bg-green-100 text-green-800"
                      : "bg-yellow-100 text-yellow-800"
                  }`}
                >
                  {recording.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
