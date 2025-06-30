"use client";

import { Loader2, Video } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { api } from "@/lib/api";

export function VideoImportForm() {
  const [zoomMeetingId, setZoomMeetingId] = useState("");
  const [title, setTitle] = useState("");
  const [thumbnailUrl, setThumbnailUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!zoomMeetingId.trim() || !title.trim() || !thumbnailUrl.trim()) return;

    setIsLoading(true);
    setError("");

    try {
      const result = await api.importVideo({
        zoom_meeting_id: zoomMeetingId,
        title: title.trim(),
        thumbnail_url: thumbnailUrl.trim(),
      });
      console.log("Video import result:", result);
      setZoomMeetingId("");
      setTitle("");
      setThumbnailUrl("");
      // The frontend will automatically update via Supabase real-time subscription
    } catch (err) {
      setError("Failed to import video. Please try again.");
      console.error("Import error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Video className="w-5 h-5" />
        Import Zoom Recording
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="zoomMeetingId"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Zoom Meeting ID
          </label>
          <Textarea
            id="zoomMeetingId"
            value={zoomMeetingId}
            onChange={(e) => setZoomMeetingId(e.target.value)}
            placeholder="Enter Zoom meeting ID (e.g., 123456789)"
            className="min-h-[60px]"
            disabled={isLoading}
          />
        </div>

        {error && <div className="text-red-600 text-sm">{error}</div>}

        <Button
          type="submit"
          disabled={isLoading || !zoomMeetingId.trim()}
          className="w-full"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Importing...
            </>
          ) : (
            "Import Video"
          )}
        </Button>
      </form>
    </div>
  );
}
