'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Loader2, FileText, Copy, Check } from 'lucide-react'

interface TranscriptViewerProps {
  videoId: string
}

export function TranscriptViewer({ videoId }: TranscriptViewerProps) {
  const [transcript, setTranscript] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [copied, setCopied] = useState(false)

  const fetchTranscript = async () => {
    setLoading(true)
    setError('')
    try {
      const transcriptData = await api.getTranscript(videoId)
      setTranscript(transcriptData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load transcript')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(transcript)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy transcript:', err)
    }
  }

  useEffect(() => {
    fetchTranscript()
  }, [videoId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin mr-2" />
        <span>Loading transcript...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500 mb-4">{error}</p>
        <Button onClick={fetchTranscript} variant="outline">
          Try Again
        </Button>
      </div>
    )
  }

  if (!transcript) {
    return (
      <div className="text-center py-8">
        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No transcript available for this video.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Transcript</h3>
        <Button
          onClick={copyToClipboard}
          variant="outline"
          size="sm"
          className="flex items-center"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 mr-2" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 mr-2" />
              Copy
            </>
          )}
        </Button>
      </div>
      
      <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
        <div className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">
          {transcript}
        </div>
      </div>
    </div>
  )
} 