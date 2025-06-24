'use client'

import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'next/navigation'
import { supabase, type Video } from '@/lib/supabase'
import { api } from '@/lib/api'
import { DraftEditor } from '@/components/DraftEditor'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Play, Clock, CheckCircle, XCircle, Loader2, Sparkles } from 'lucide-react'

export default function VideoDetailPage() {
  const params = useParams()
  const videoId = params.id as string
  
  const [video, setVideo] = useState<Video | null>(null)
  const [loading, setLoading] = useState(true)
  const [summarizing, setSummarizing] = useState(false)

  const fetchVideo = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .eq('id', videoId)
        .single()

      if (error) {
        console.error('Error fetching video:', error)
        return
      }

      setVideo(data)
    } catch (err) {
      console.error('Error fetching video:', err)
    } finally {
      setLoading(false)
    }
  }, [videoId])

  useEffect(() => {
    fetchVideo()

    // Subscribe to video changes
    const channel = supabase
      .channel(`video-${videoId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'videos',
          filter: `id=eq.${videoId}`
        },
        (payload) => {
          console.log('Video change:', payload)
          fetchVideo()
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [videoId, fetchVideo])

  const handleSummarize = async () => {
    setSummarizing(true)
    try {
      await api.summarizeVideo(videoId)
    } catch (err) {
      console.error('Error triggering summarization:', err)
    } finally {
      setSummarizing(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    )
  }

  if (!video) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Video Not Found</h1>
          <p className="text-gray-600">The video you&apos;re looking for doesn&apos;t exist.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => window.history.back()}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Videos
          </Button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{video.title}</h1>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {formatDuration(video.duration)}
                </span>
                <span>{formatDate(video.created_at)}</span>
                <span className="flex items-center capitalize">
                  {getStatusIcon(video.status)}
                  <span className="ml-1">{video.status}</span>
                </span>
              </div>
            </div>
            
            <div className="flex space-x-2">
              {video.youtube_url && (
                <Button
                  variant="outline"
                  onClick={() => window.open(video.youtube_url, '_blank')}
                >
                  <Play className="w-4 h-4 mr-2" />
                  Watch on YouTube
                </Button>
              )}
              {video.status === 'ready' && !video.summary_points?.length && (
                <Button
                  onClick={handleSummarize}
                  disabled={summarizing}
                >
                  {summarizing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Summarizing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Generate Summary
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Video Summary */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Summary</h2>
            {video.summary_points && video.summary_points.length > 0 ? (
              <ul className="space-y-2">
                {video.summary_points.map((point, index) => (
                  <li key={index} className="flex items-start">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                    <span className="text-gray-700">{point}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-gray-500 text-center py-8">
                {video.status === 'ready' ? (
                  <div>
                    <p>No summary generated yet.</p>
                    <Button
                      onClick={handleSummarize}
                      disabled={summarizing}
                      className="mt-2"
                    >
                      {summarizing ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Summarizing...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          Generate Summary
                        </>
                      )}
                    </Button>
                  </div>
                ) : (
                  <p>Summary will be available once processing is complete.</p>
                )}
              </div>
            )}
          </div>

          {/* Draft Editor */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <DraftEditor videoId={videoId} />
          </div>
        </div>
      </div>
    </div>
  )
} 