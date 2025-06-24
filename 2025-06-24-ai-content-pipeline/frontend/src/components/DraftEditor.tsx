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
        <h3 className="text-lg font-semibold">Content Drafts</h3>
        <div className="flex items-center space-x-2">
          {lastSaved && (
            <span className="text-sm text-gray-500">
              Last saved: {lastSaved.toLocaleTimeString()}
            </span>
          )}
          <Button
            onClick={handleSave}
            disabled={isSaving}
            size="sm"
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

      <div className="grid gap-6 md:grid-cols-1">
        {/* Email Draft */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium">
            <Mail className="w-4 h-4" />
            Email Content
          </label>
          <Textarea
            value={currentDraft.email_content}
            onChange={(e) => handleContentChange('email_content', e.target.value)}
            placeholder="Write your email content here..."
            className="min-h-[120px]"
          />
        </div>

        {/* X/Twitter Draft */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium">
            <Twitter className="w-4 h-4" />
            X (Twitter) Content
          </label>
          <Textarea
            value={currentDraft.x_content}
            onChange={(e) => handleContentChange('x_content', e.target.value)}
            placeholder="Write your X post here..."
            className="min-h-[120px]"
          />
        </div>

        {/* LinkedIn Draft */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium">
            <Linkedin className="w-4 h-4" />
            LinkedIn Content
          </label>
          <Textarea
            value={currentDraft.linkedin_content}
            onChange={(e) => handleContentChange('linkedin_content', e.target.value)}
            placeholder="Write your LinkedIn post here..."
            className="min-h-[120px]"
          />
        </div>
      </div>

      {/* Draft History */}
      {drafts.length > 1 && (
        <div className="mt-8">
          <h4 className="text-sm font-medium mb-3">Draft History</h4>
          <div className="space-y-2">
            {drafts.slice(1).map((draft) => (
              <div
                key={draft.id}
                className="text-xs text-gray-500 p-2 bg-gray-50 rounded"
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