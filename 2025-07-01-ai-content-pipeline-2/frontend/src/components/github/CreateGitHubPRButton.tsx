"use client"

import { useState } from "react"
import { Github, Loader2 } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { apiClient } from "@/lib/apiClient"

interface CreateGitHubPRButtonProps {
  video: {
    id: string
    youtube_url: string | null
    transcript: string | null
    summary: any | null
    github_pr_url?: string | null
  }
  onSuccess?: (prUrl: string) => void
}

export function CreateGitHubPRButton({ video, onSuccess }: CreateGitHubPRButtonProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [nextEpisodeSummary, setNextEpisodeSummary] = useState("")
  const [nextEpisodeLumaLink, setNextEpisodeLumaLink] = useState("")
  const [showForm, setShowForm] = useState(false)
  
  // Check if all required data is available
  const canCreatePR = video.youtube_url && video.transcript && video.summary
  
  const missingItems = []
  if (!video.youtube_url) missingItems.push("YouTube URL")
  if (!video.transcript) missingItems.push("Transcript")
  if (!video.summary) missingItems.push("Summary")
  
  const handleCreatePR = async () => {
    if (!nextEpisodeSummary || !nextEpisodeLumaLink) {
      toast.error("Please provide next episode details")
      return
    }
    
    setIsLoading(true)
    try {
      const data = await apiClient.createGitHubPR(
        video.id,
        nextEpisodeSummary,
        nextEpisodeLumaLink
      )
      
      toast.success('GitHub PR created successfully!')
      onSuccess?.(data.pr_url)
      setShowForm(false)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create GitHub PR')
    } finally {
      setIsLoading(false)
    }
  }
  
  if (!canCreatePR) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button disabled variant="outline" size="sm">
              <Github className="mr-2 h-4 w-4" />
              Create GitHub Draft
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Missing: {missingItems.join(', ')}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    )
  }
  
  return (
    <>
      <Button 
        onClick={() => setShowForm(true)} 
        variant="outline"
        size="sm"
        disabled={video.github_pr_url !== null && video.github_pr_url !== undefined}
      >
        <Github className="mr-2 h-4 w-4" />
        {video.github_pr_url ? 'PR Created' : 'Create GitHub Draft'}
      </Button>
      
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Create GitHub PR</DialogTitle>
            <DialogDescription>
              Provide details for the next episode to update the repository
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="next-summary">Next Episode Summary</Label>
              <Textarea
                id="next-summary"
                value={nextEpisodeSummary}
                onChange={(e) => setNextEpisodeSummary(e.target.value)}
                placeholder="Brief description of the next episode..."
                rows={3}
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="luma-link">Next Episode Luma Link</Label>
              <Input
                id="luma-link"
                type="url"
                value={nextEpisodeLumaLink}
                onChange={(e) => setNextEpisodeLumaLink(e.target.value)}
                placeholder="https://lu.ma/..."
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleCreatePR} 
              disabled={isLoading || !nextEpisodeSummary || !nextEpisodeLumaLink}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create PR'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}