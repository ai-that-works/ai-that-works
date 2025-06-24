'use client'

import { useEffect, useState, useCallback } from 'react'
import { supabase, type Video } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Play, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react'

export function VideoList() {
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState(true)

  const fetchVideos = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .order('created_at', { ascending: false })

      if (error) {
        console.error('Error fetching videos:', error)
        return
      }

      setVideos(data || [])
    } catch (err) {
      console.error('Error fetching videos:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // Initial fetch
    fetchVideos()

    // Set up real-time subscription
    const channel = supabase
      .channel('videos')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'videos'
        },
        (payload) => {
          console.log('Video change:', payload)
          fetchVideos() // Refresh the list
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [fetchVideos])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32 bg-white rounded-xl shadow-sm">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    )
  }

  if (videos.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-xl shadow-sm">
        <div className="text-gray-400 mb-4">
          <Play className="w-12 h-12 mx-auto" />
        </div>
        <p className="text-gray-500 text-lg">No videos yet</p>
        <p className="text-gray-400 text-sm">Import your first Zoom recording to get started</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {videos.map((video) => (
        <div
          key={video.id}
          className="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 p-6 border border-gray-100"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                {getStatusIcon(video.status)}
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="font-semibold text-gray-900 text-lg truncate">{video.title}</h3>
                <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                  <span className="flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {formatDuration(video.duration)}
                  </span>
                  <span>{formatDate(video.created_at)}</span>
                  <span className="px-2 py-1 bg-gray-100 rounded-full text-xs capitalize font-medium">
                    {video.status}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex space-x-2 flex-shrink-0">
              {video.youtube_url && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.open(video.youtube_url!, '_blank')}
                  className="text-red-600 border-red-200 hover:bg-red-50"
                >
                  <Play className="w-3 h-3 mr-1" />
                  Watch
                </Button>
              )}
              <Button
                size="sm"
                onClick={() => window.location.href = `/videos/${video.id}`}
                className="bg-blue-600 hover:bg-blue-700"
              >
                View Details
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
} 