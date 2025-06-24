'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { api } from '@/lib/api'
import { supabase, type Draft } from '@/lib/supabase'
import { Save, Loader2, Mail, Twitter, Linkedin } from 'lucide-react'

interface DraftEditorProps {
  videoId: string
}

export function DraftEditor({ videoId }: DraftEditorProps) {
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [currentDraft, setCurrentDraft] = useState({
    email_content: '',
    x_content: '',
    linkedin_content: ''
  })
  const [isSaving, setIsSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)

  const fetchDrafts = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('drafts')
        .select('*')
        .eq('video_id', videoId)
        .order('created_at', { ascending: false })

      if (error) {
        console.error('Error fetching drafts:', error)
        return
      }

      setDrafts(data || [])
      
      // Load the latest draft into the editor
      if (data && data.length > 0) {
        const latest = data[0]
        setCurrentDraft({
          email_content: latest.email_content,
          x_content: latest.x_content,
          linkedin_content: latest.linkedin_content
        })
      }
    } catch (err) {
      console.error('Error fetching drafts:', err)
    }
  }, [videoId])

  useEffect(() => {
    fetchDrafts()

    // Subscribe to draft changes
    const channel = supabase
      .channel(`drafts-${videoId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'drafts',
          filter: `video_id=eq.${videoId}`
        },
        (payload) => {
          console.log('Draft change:', payload)
          fetchDrafts()
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [videoId, fetchDrafts])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await api.saveDraft(videoId, currentDraft)
      setLastSaved(new Date())
    } catch (err) {
      console.error('Error saving draft:', err)
    } finally {
      setIsSaving(false)
    }
  }

  const handleContentChange = (field: keyof typeof currentDraft, value: string) => {
    setCurrentDraft(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-900">Content Drafts</h3>
        <div className="flex items-center space-x-3">
          {lastSaved && (
            <span className="text-sm text-gray-500 font-medium">
              Last saved: {lastSaved.toLocaleTimeString()}
            </span>
          )}
          <Button
            onClick={handleSave}
            disabled={isSaving}
            size="sm"
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isSaving ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Draft
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="space-y-6">
        {/* Email Draft */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <label className="flex items-center gap-2 text-sm font-semibold text-blue-900 mb-3">
            <Mail className="w-4 h-4" />
            Email Content
          </label>
          <Textarea
            value={currentDraft.email_content}
            onChange={(e) => handleContentChange('email_content', e.target.value)}
            placeholder="Write your email content here..."
            className="min-h-[120px] border-blue-200 focus:border-blue-500 bg-white"
          />
        </div>

        {/* X/Twitter Draft */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <label className="flex items-center gap-2 text-sm font-semibold text-gray-900 mb-3">
            <Twitter className="w-4 h-4" />
            X (Twitter) Content
          </label>
          <Textarea
            value={currentDraft.x_content}
            onChange={(e) => handleContentChange('x_content', e.target.value)}
            placeholder="Write your X post here..."
            className="min-h-[120px] border-gray-200 focus:border-gray-500 bg-white"
          />
        </div>

        {/* LinkedIn Draft */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <label className="flex items-center gap-2 text-sm font-semibold text-blue-900 mb-3">
            <Linkedin className="w-4 h-4" />
            LinkedIn Content
          </label>
          <Textarea
            value={currentDraft.linkedin_content}
            onChange={(e) => handleContentChange('linkedin_content', e.target.value)}
            placeholder="Write your LinkedIn post here..."
            className="min-h-[120px] border-blue-200 focus:border-blue-500 bg-white"
          />
        </div>
      </div>

      {/* Draft History */}
      {drafts.length > 1 && (
        <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Draft History</h4>
          <div className="space-y-2">
            {drafts.slice(1).map((draft) => (
              <div
                key={draft.id}
                className="text-xs text-gray-600 p-3 bg-white border border-gray-200 rounded font-medium"
              >
                Version {draft.version} - {new Date(draft.created_at).toLocaleString()}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 