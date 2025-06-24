"use client"

import { cn } from "@/lib/utils"

interface YouTubeEmbedProps {
  url: string
  className?: string
  title?: string
  size?: "small" | "medium" | "large"
}

function extractVideoId(url: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
    /youtube\.com\/v\/([^&\n?#]+)/,
    /youtube\.com\/watch\?.*v=([^&\n?#]+)/
  ]
  
  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match) {
      return match[1]
    }
  }
  return null
}

export function YouTubeEmbed({ url, className, title = "YouTube Video", size = "medium" }: YouTubeEmbedProps) {
  const videoId = extractVideoId(url)
  
  if (!videoId) {
    return (
      <div className={cn("flex items-center justify-center bg-muted rounded-lg", className)}>
        <span className="macos-text-callout text-muted-foreground">Invalid YouTube URL</span>
      </div>
    )
  }

  const sizeClasses = {
    small: "aspect-video w-full max-w-xs",
    medium: "aspect-video w-full max-w-md", 
    large: "aspect-video w-full"
  }

  const embedUrl = `https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1&showinfo=0`

  return (
    <div className={cn("macos-material-content overflow-hidden", sizeClasses[size], className)}>
      <iframe
        src={embedUrl}
        title={title}
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        className="w-full h-full border-0"
        loading="lazy"
      />
    </div>
  )
}