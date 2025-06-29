"use client"

import { useState, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { api } from "@/lib/apiClient" // Assuming apiClient.ts
import { supabase, type Draft, type EmailDraft, type XDraft, type LinkedInDraft } from "@/lib/supabase" // Assuming supabase.ts
import { Mail, MessageSquareText, LinkedinIcon, History, Eye } from "lucide-react" // Using MessageSquareText for X/Twitter
import { toast } from "sonner"
import { formatDate } from "@/lib/utils"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { LoadingIndicator } from "@/components/shared/loading-indicator"
import { EmailPreview } from "./email-preview"
import { XPreview } from "./x-preview"
import { LinkedInPreview } from "./linkedin-preview"

interface DraftEditorProps {
  videoId: string
}

// Types now imported from BAML-generated types via supabase.ts

interface CurrentDraftState {
  email_draft: EmailDraft | null
  x_draft: XDraft | null
  linkedin_draft: LinkedInDraft | null
}

export function DraftEditor({ videoId }: DraftEditorProps) {
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [currentDraft, setCurrentDraft] = useState<CurrentDraftState>({
    email_draft: null,
    x_draft: null,
    linkedin_draft: null,
  })
  const [selectedHistoricalDraft, setSelectedHistoricalDraft] = useState<Draft | null>(null)
  const [isLoadingDrafts, setIsLoadingDrafts] = useState(true)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)

  const fetchDrafts = useCallback(async () => {
    setIsLoadingDrafts(true)
    try {
      const { data, error } = await supabase
        .from("drafts")
        .select("*")
        .eq("video_id", videoId)
        .order("created_at", { ascending: false })

      if (error) throw error

      setDrafts(data || [])
      if (data && data.length > 0) {
        const latest = data[0]
        setCurrentDraft({
          email_draft: latest.email_draft || null,
          x_draft: latest.x_draft || null,
          linkedin_draft: latest.linkedin_draft || null,
        })
        try {
          setLastSaved(new Date(latest.created_at))
        } catch {
          setLastSaved(new Date())
        }
      } else {
        // Reset if no drafts found
        setCurrentDraft({ email_draft: null, x_draft: null, linkedin_draft: null })
        setLastSaved(null)
      }
    } catch (err: any) {
      console.error("Error fetching drafts:", err)
      toast.error(`Failed to fetch drafts: ${err.message}`)
    } finally {
      setIsLoadingDrafts(false)
    }
  }, [videoId])

  useEffect(() => {
    if (videoId) {
      fetchDrafts()

      // Note: Real-time updates for drafts are handled by the parent video page
      // to avoid multiple subscriptions and reduce timeout issues
      console.log(`📡 Draft real-time updates handled by parent page for ${videoId}`)
      
      // Set up a custom event listener for draft updates from parent
      const handleDraftUpdate = () => {
        fetchDrafts()
      }
      
      window.addEventListener(`draft-update-${videoId}`, handleDraftUpdate)
      
      return () => {
        window.removeEventListener(`draft-update-${videoId}`, handleDraftUpdate)
      }
    }
  }, [videoId, fetchDrafts])

  const handleSaveDraft = async (updatedDraft: CurrentDraftState) => {
    console.log('💾 Saving draft:', updatedDraft)
    
    toast.promise(
      api.saveDraft(videoId, updatedDraft),
      {
        loading: "Saving draft...",
        success: (savedDraft: Draft) => {
          console.log('✅ Draft saved successfully:', savedDraft)
          setLastSaved(new Date())
          // Update current draft to reflect saved state
          setCurrentDraft(updatedDraft)
          return "Draft saved successfully!"
        },
        error: (err) => {
          console.error('❌ Draft save failed:', err)
          return `Failed to save draft: ${err.message || "Unknown error"}`
        },
      },
    )
  }

  // Handle content refinement with feedback
  const handleRefineContent = async (contentType: "email" | "x" | "linkedin", feedback: string) => {
    console.log(`🎨 Refining ${contentType} content with feedback:`, feedback)
    
    let currentContentDraft = null
    if (contentType === "email" && currentDraft.email_draft) {
      currentContentDraft = currentDraft.email_draft
    } else if (contentType === "x" && currentDraft.x_draft) {
      currentContentDraft = currentDraft.x_draft
    } else if (contentType === "linkedin" && currentDraft.linkedin_draft) {
      currentContentDraft = currentDraft.linkedin_draft
    }
    
    if (!currentContentDraft) {
      toast.error(`No existing ${contentType} content to refine`)
      return
    }
    
    try {
      await api.refineContent(videoId, feedback, contentType, currentContentDraft)
      console.log(`✅ ${contentType} refinement request sent successfully`)
      toast.success(`${contentType} refinement started! You'll see the updated content shortly.`)
    } catch (err: any) {
      console.error(`❌ ${contentType} content refinement request failed:`, err)
      toast.error(`Failed to start ${contentType} refinement: ${err.message || "Unknown error"}`)
    }
  }


  const viewHistoricalDraft = (draft: Draft) => {
    setSelectedHistoricalDraft(draft)
  }

  if (isLoadingDrafts) {
    return <LoadingIndicator text="Loading drafts..." />
  }

  return (
    <div className="space-y-6">
      <Tabs defaultValue="email" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="email">
            <Mail className="w-4 h-4 mr-2 inline-block" />
            Email
          </TabsTrigger>
          <TabsTrigger value="x">
            <MessageSquareText className="w-4 h-4 mr-2 inline-block" />X (Twitter)
          </TabsTrigger>
          <TabsTrigger value="linkedin">
            <LinkedinIcon className="w-4 h-4 mr-2 inline-block" />
            LinkedIn
          </TabsTrigger>
        </TabsList>
        <TabsContent value="email" className="mt-4">
          <EmailPreview
            draft={currentDraft.email_draft}
            onChange={(draft) => {
              console.log('📧 Email draft updated:', draft)
              const updatedDraft = { ...currentDraft, email_draft: draft }
              handleSaveDraft(updatedDraft)
            }}
            onRefine={(feedback) => handleRefineContent("email", feedback)}
          />
        </TabsContent>
        <TabsContent value="x" className="mt-4">
          <XPreview
            draft={currentDraft.x_draft}
            onChange={(draft) => {
              console.log('🐦 X draft updated:', draft)
              const updatedDraft = { ...currentDraft, x_draft: draft }
              handleSaveDraft(updatedDraft)
            }}
          />
        </TabsContent>
        <TabsContent value="linkedin" className="mt-4">
          <LinkedInPreview
            draft={currentDraft.linkedin_draft}
            onChange={(draft) => {
              console.log('💼 LinkedIn draft updated:', draft)
              const updatedDraft = { ...currentDraft, linkedin_draft: draft }
              handleSaveDraft(updatedDraft)
            }}
          />
        </TabsContent>
      </Tabs>

      {lastSaved && (
        <div className="text-center">
          <p className="macos-text-callout text-muted-foreground">Last saved: {formatDate(lastSaved.toISOString())}</p>
        </div>
      )}

      {drafts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="macos-text-title3 flex items-center">
              <History className="w-5 h-5 mr-2" />
              Draft History
            </CardTitle>
            <CardDescription>Review previous versions of your drafts. The most recent is at the top.</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-48">
              <div className="space-y-2">
                {drafts.map((draft) => (
                  <div
                    key={draft.id}
                    className="flex justify-between items-center macos-text-callout p-3 bg-muted/50 border rounded-md"
                  >
                    <div>
                      <span className="font-medium text-foreground">Version {draft.version}</span>
                      <span className="text-muted-foreground ml-2">- {formatDate(draft.created_at)}</span>
                    </div>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="ghost" size="sm" onClick={() => viewHistoricalDraft(draft)}>
                          <Eye className="w-4 h-4 mr-1" /> View
                        </Button>
                      </DialogTrigger>
                      {selectedHistoricalDraft && selectedHistoricalDraft.id === draft.id && (
                        <DialogContent className="sm:max-w-4xl max-w-[90vw]">
                          <DialogHeader>
                            <DialogTitle className="flex items-center gap-2">
                              <History className="w-5 h-5" />
                              Draft Version {selectedHistoricalDraft.version} (Read-Only)
                            </DialogTitle>
                            <DialogDescription>
                              Created on {formatDate(selectedHistoricalDraft.created_at)}. This is a historical version and cannot be edited.
                            </DialogDescription>
                          </DialogHeader>
                          <ScrollArea className="max-h-[70vh] mt-4">
                            <Tabs defaultValue="email" className="w-full">
                              <TabsList className="grid w-full grid-cols-3">
                                <TabsTrigger value="email">
                                  <Mail className="w-4 h-4 mr-2 inline-block" />
                                  Email
                                </TabsTrigger>
                                <TabsTrigger value="x">
                                  <MessageSquareText className="w-4 h-4 mr-2 inline-block" />X (Twitter)
                                </TabsTrigger>
                                <TabsTrigger value="linkedin">
                                  <LinkedinIcon className="w-4 h-4 mr-2 inline-block" />
                                  LinkedIn
                                </TabsTrigger>
                              </TabsList>
                              <TabsContent value="email" className="mt-4">
                                {selectedHistoricalDraft.email_draft ? (
                                  <EmailPreview
                                    draft={selectedHistoricalDraft.email_draft}
                                    onChange={() => {}} // Read-only for historical view
                                    readOnly={true} // Disable editing for historical view
                                  />
                                ) : (
                                  <div className="text-center py-8 text-muted-foreground">
                                    No email content in this version
                                  </div>
                                )}
                              </TabsContent>
                              <TabsContent value="x" className="mt-4">
                                {selectedHistoricalDraft.x_draft ? (
                                  <XPreview
                                    draft={selectedHistoricalDraft.x_draft}
                                    onChange={() => {}} // Read-only for historical view
                                    readOnly={true} // Disable editing for historical view
                                  />
                                ) : (
                                  <div className="text-center py-8 text-muted-foreground">
                                    No X content in this version
                                  </div>
                                )}
                              </TabsContent>
                              <TabsContent value="linkedin" className="mt-4">
                                {selectedHistoricalDraft.linkedin_draft ? (
                                  <LinkedInPreview
                                    draft={selectedHistoricalDraft.linkedin_draft}
                                    onChange={() => {}} // Read-only for historical view
                                    readOnly={true} // Disable editing for historical view
                                  />
                                ) : (
                                  <div className="text-center py-8 text-muted-foreground">
                                    No LinkedIn content in this version
                                  </div>
                                )}
                              </TabsContent>
                            </Tabs>
                          </ScrollArea>
                          <DialogFooter>
                            <DialogClose asChild>
                              <Button type="button" variant="outline">
                                Close
                              </Button>
                            </DialogClose>
                          </DialogFooter>
                        </DialogContent>
                      )}
                    </Dialog>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
