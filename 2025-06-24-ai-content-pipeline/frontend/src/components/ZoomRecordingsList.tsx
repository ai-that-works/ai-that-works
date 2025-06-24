'use client'

import { useState, useEffect } from 'react'
import { api, ZoomMeetingRecordings } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Loader2, Video, Calendar, Clock, FileText } from 'lucide-react'

function getLast3MonthsRange() {
  const to = new Date()
  const from = new Date()
  from.setMonth(from.getMonth() - 3)
  return {
    from_date: from.toISOString().slice(0, 10),
    to_date: to.toISOString().slice(0, 10),
  }
}

export function ZoomRecordingsList() {
  const [meetings, setMeetings] = useState<ZoomMeetingRecordings[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [processing, setProcessing] = useState<string | null>(null)
  
  const fetchRecordings = async () => {
    setLoading(true)
    setError('')
    try {
      const { from_date, to_date } = getLast3MonthsRange()
      const response = await api.getZoomRecordings({ from_date, to_date })
      setMeetings(response.meetings)
    } catch (err) {
      setError('Failed to fetch Zoom recordings')
      console.error('Error fetching recordings:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecordings()
  }, [])

  const formatFileSize = (bytes: number) => {
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(1)} MB`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const formatDuration = (start: string, end: string) => {
    const startTime = new Date(start)
    const endTime = new Date(end)
    const diffMs = endTime.getTime() - startTime.getTime()
    const diffMins = Math.round(diffMs / 60000)
    return `${diffMins} min`
  }

  const getRecordingIcon = (type: string) => {
    switch (type) {
      case 'shared_screen_with_speaker_view':
      case 'shared_screen_with_speaker_view(CC)':
        return <Video className="w-4 h-4 text-blue-600" />
      case 'audio_only':
        return <FileText className="w-4 h-4 text-green-600" />
      case 'audio_transcript':
        return <FileText className="w-4 h-4 text-purple-600" />
      default:
        return <FileText className="w-4 h-4 text-gray-600" />
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <Loader2 className="w-6 h-6 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 mb-4">{error}</div>
        <Button onClick={fetchRecordings}>Retry</Button>
      </div>
    )
  }

  if (meetings.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No Zoom recordings found.
      </div>
    )
  }

  const handleProcess = async (meetingId: string) => {
    setProcessing(meetingId)
    try {
      // Call backend API to process the meeting (replace with actual endpoint if needed)
      await api.importVideo({ zoom_meeting_id: meetingId })
      // Optionally show a success message or update UI
    } catch {
      alert('Failed to process meeting')
    } finally {
      setProcessing(null)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Zoom Recordings</h2>
        <Button onClick={fetchRecordings} variant="outline" size="sm">
          Refresh
        </Button>
      </div>
      {meetings.map((meeting) => (
        <div key={meeting.meeting_id} className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h3 className="font-medium text-gray-900 text-lg">
                {meeting.meeting_title}
              </h3>
              <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                <span className="flex items-center">
                  <Calendar className="w-3 h-3 mr-1" />
                  {formatDate(meeting.recording_start)}
                </span>
                <span className="flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {formatDuration(meeting.recording_start, meeting.recording_end)}
                </span>
              </div>
            </div>
            <span className="text-xs text-gray-400">Meeting ID: {meeting.meeting_id}</span>
          </div>
          <div className="grid gap-2 mb-2">
            {meeting.recordings.map((recording) => (
              <div
                key={recording.recording_id}
                className="flex items-center justify-between border rounded px-3 py-2 bg-gray-50"
              >
                <div className="flex items-center space-x-3 min-w-0">
                  {getRecordingIcon(recording.recording_type)}
                  <span className="truncate text-gray-800 text-sm">
                    {recording.recording_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs text-gray-500">{formatFileSize(recording.file_size)}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    recording.status === 'completed' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {recording.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <Button
            size="sm"
            variant="default"
            className="w-full"
            onClick={() => handleProcess(meeting.meeting_id)}
            disabled={processing === meeting.meeting_id}
          >
            {processing === meeting.meeting_id ? (
              <span className="flex items-center justify-center"><Loader2 className="w-4 h-4 animate-spin mr-2" />Processing...</span>
            ) : (
              'Process'
            )}
          </Button>
        </div>
      ))}
    </div>
  )
} 