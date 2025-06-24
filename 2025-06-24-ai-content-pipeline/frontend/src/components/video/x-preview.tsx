"use client"

import { useState } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Eye, Edit3, Heart, MessageCircle, Repeat2, Share, MoreHorizontal } from "lucide-react"
import { cn } from "@/lib/utils"

interface XDraft {
  tweets: string[]
  hashtags: string[]
}

interface XPreviewProps {
  draft: XDraft | null
  onChange: (draft: XDraft) => void
  className?: string
  readOnly?: boolean
}

export function XPreview({ draft, onChange, className, readOnly = false }: XPreviewProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    tweets: [''],
    hashtags: ['']
  })

  // Initialize form when switching to edit mode
  const startEditing = () => {
    setFormData({
      tweets: draft?.tweets?.length ? draft.tweets : [''],
      hashtags: draft?.hashtags?.length ? draft.hashtags : ['']
    })
    setIsEditing(true)
  }

  // Save form data directly as JSON
  const saveEdit = () => {
    onChange({
      tweets: formData.tweets.filter(tweet => tweet.trim()),
      hashtags: formData.hashtags.filter(tag => tag.trim())
    })
    setIsEditing(false)
  }

  // Add/remove tweet functions
  const addTweet = () => {
    setFormData(prev => ({
      ...prev,
      tweets: [...prev.tweets, '']
    }))
  }

  const removeTweet = (index: number) => {
    setFormData(prev => ({
      ...prev,
      tweets: prev.tweets.filter((_, i) => i !== index)
    }))
  }

  const updateTweet = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      tweets: prev.tweets.map((tweet, i) => i === index ? value : tweet)
    }))
  }

  const updateHashtags = (value: string) => {
    const hashtags = value.split(' ').filter(tag => tag.trim())
    setFormData(prev => ({
      ...prev,
      hashtags
    }))
  }

  const tweets = draft?.tweets || []
  const hashtags = draft?.hashtags || []

  if (isEditing) {
    return (
      <div className={cn("space-y-4", className)}>
        <div className="flex justify-between items-center">
          <h3 className="macos-text-title3 text-foreground">Edit X Thread</h3>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={saveEdit}
            >
              Save
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(false)}
            >
              Cancel
            </Button>
          </div>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Tweets</label>
            {formData.tweets.map((tweet, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <div className="flex-1">
                  <Textarea
                    placeholder={`Tweet ${index + 1}...`}
                    value={tweet}
                    onChange={(e) => updateTweet(index, e.target.value)}
                    rows={2}
                    className="macos-text-body"
                  />
                  <div className="text-xs text-muted-foreground mt-1">
                    {tweet.length}/280 characters
                  </div>
                </div>
                {formData.tweets.length > 1 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => removeTweet(index)}
                    className="self-start"
                  >
                    ×
                  </Button>
                )}
              </div>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={addTweet}
              className="mt-2"
            >
              + Add Tweet
            </Button>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Hashtags</label>
            <input
              type="text"
              placeholder="#hashtag1 #hashtag2"
              value={formData.hashtags.join(' ')}
              onChange={(e) => updateHashtags(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring macos-text-body"
            />
            <div className="text-xs text-muted-foreground mt-1">
              Separate hashtags with spaces
            </div>
          </div>
        </div>
        <p className="macos-text-caption1 text-muted-foreground text-right">
          {formData.tweets.reduce((total, tweet) => total + tweet.length, 0)} characters across {formData.tweets.length} tweets
        </p>
      </div>
    )
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex justify-between items-center">
        <h3 className="macos-text-title3 text-foreground">X Thread Preview</h3>
        {!readOnly && (
          <Button
            variant="outline"
            size="sm"
            onClick={startEditing}
          >
            <Edit3 className="w-4 h-4 mr-1" />
            Edit
          </Button>
        )}
      </div>
      
      {/* X/Twitter Thread - Authentic Design */}
      <div className="bg-white dark:bg-black border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif' }}>
        {tweets.length > 0 ? tweets.map((tweet, index) => (
          <div key={index} className="relative">
            {/* Thread connector line */}
            {index > 0 && (
              <div className="absolute left-6 -top-3 w-0.5 h-3 bg-gray-200 dark:bg-gray-700"></div>
            )}
            {tweets.length > 1 && index < tweets.length - 1 && (
              <div className="absolute left-6 bottom-0 w-0.5 h-3 bg-gray-200 dark:bg-gray-700"></div>
            )}
            
            <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50/50 dark:hover:bg-gray-950/50 transition-colors">
              <div className="flex gap-3">
                {/* Profile Picture */}
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-white">V</span>
                  </div>
                </div>
                
                {/* Tweet Content */}
                <div className="flex-1 min-w-0">
                  {/* Header */}
                  <div className="flex items-center gap-1 mb-1">
                    <span className="font-bold text-black dark:text-white text-[15px] hover:underline cursor-pointer">HelloVAI</span>
                    <svg className="w-[18px] h-[18px] text-[#1d9bf0] ml-1" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M22.25 12c0-1.43-.88-2.67-2.19-3.34.46-1.39.2-2.9-.81-3.91s-2.52-1.27-3.91-.81c-.66-1.31-1.91-2.19-3.34-2.19s-2.67.88-3.33 2.19c-1.4-.46-2.91-.2-3.92.81s-1.26 2.52-.8 3.91c-1.31.67-2.2 1.91-2.2 3.34s.89 2.67 2.2 3.34c-.46 1.39-.21 2.9.8 3.91s2.52 1.27 3.91.81c.67 1.31 1.91 2.19 3.34 2.19s2.68-.88 3.34-2.19c1.39.46 2.9.2 3.91-.81s1.27-2.52.81-3.91c1.31-.67 2.19-1.91 2.19-3.34zm-11.71 4.2L6.8 12.46l1.41-1.42 2.26 2.26 4.8-5.23 1.47 1.36-6.2 6.77z"/>
                    </svg>
                    <span className="text-gray-500 dark:text-gray-400 text-[15px]">@hellovai</span>
                    <span className="text-gray-500 dark:text-gray-400 text-[15px]">·</span>
                    <span className="text-gray-500 dark:text-gray-400 text-[15px] hover:underline cursor-pointer">now</span>
                    <div className="ml-auto">
                      <button className="w-[34.75px] h-[34.75px] rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center justify-center group">
                        <MoreHorizontal className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Tweet Text */}
                  <div className="text-black dark:text-white text-[15px] leading-5 mb-3 whitespace-pre-wrap break-words">
                    {tweet.split(' ').map((word, i) => {
                      if (word.startsWith('#')) {
                        return <span key={i} className="text-[#1d9bf0] hover:underline cursor-pointer">{word} </span>
                      }
                      if (word.startsWith('@')) {
                        return <span key={i} className="text-[#1d9bf0] hover:underline cursor-pointer">{word} </span>
                      }
                      return word + ' '
                    })}
                  </div>
                  
                  {/* Thread indicator */}
                  {tweets.length > 1 && (
                    <div className="text-[#1d9bf0] text-[15px] mb-3 hover:underline cursor-pointer">
                      {index === 0 ? `Show this thread` : `${index + 1}/${tweets.length}`}
                    </div>
                  )}
                  
                  {/* Action Buttons */}
                  <div className="flex items-center justify-between max-w-[425px] mt-3">
                    <button className="flex items-center group">
                      <div className="w-[34.75px] h-[34.75px] rounded-full group-hover:bg-[#1d9bf0]/10 flex items-center justify-center">
                        <MessageCircle className="w-[18px] h-[18px] text-gray-500 dark:text-gray-400 group-hover:text-[#1d9bf0]" />
                      </div>
                      <span className="text-gray-500 dark:text-gray-400 text-[13px] ml-1 group-hover:text-[#1d9bf0]">12</span>
                    </button>
                    
                    <button className="flex items-center group">
                      <div className="w-[34.75px] h-[34.75px] rounded-full group-hover:bg-[#00ba7c]/10 flex items-center justify-center">
                        <Repeat2 className="w-[18px] h-[18px] text-gray-500 dark:text-gray-400 group-hover:text-[#00ba7c]" />
                      </div>
                      <span className="text-gray-500 dark:text-gray-400 text-[13px] ml-1 group-hover:text-[#00ba7c]">34</span>
                    </button>
                    
                    <button className="flex items-center group">
                      <div className="w-[34.75px] h-[34.75px] rounded-full group-hover:bg-[#f91880]/10 flex items-center justify-center">
                        <Heart className="w-[18px] h-[18px] text-gray-500 dark:text-gray-400 group-hover:text-[#f91880]" />
                      </div>
                      <span className="text-gray-500 dark:text-gray-400 text-[13px] ml-1 group-hover:text-[#f91880]">89</span>
                    </button>
                    
                    <button className="group">
                      <div className="w-[34.75px] h-[34.75px] rounded-full group-hover:bg-[#1d9bf0]/10 flex items-center justify-center">
                        <Share className="w-[18px] h-[18px] text-gray-500 dark:text-gray-400 group-hover:text-[#1d9bf0]" />
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )) : (
          <div className="px-4 py-12 text-center border-b border-gray-100 dark:border-gray-800">
            <div className="text-gray-500 dark:text-gray-400 text-[15px]">
              Your X thread will appear here...
            </div>
          </div>
        )}
        
        {/* X Footer */}
        <div className="px-4 py-2 bg-gray-50/50 dark:bg-gray-900/50 text-center">
          <span className="text-gray-400 text-[13px]">X post preview • Click Edit to modify</span>
        </div>
      </div>
    </div>
  )
}