"use client";

import {
  Edit3,
  MessageSquare,
  MoreHorizontal,
  Repeat2,
  Send,
  ThumbsUp,
} from "lucide-react";
import { useState } from "react";
import type { LinkedInPost } from "@/baml_client/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type LinkedInDraft = LinkedInPost;

interface LinkedInPreviewProps {
  draft: LinkedInDraft | null;
  onChange: (draft: LinkedInDraft) => void;
  className?: string;
  readOnly?: boolean;
}

export function LinkedInPreview({
  draft,
  onChange,
  className,
  readOnly = false,
}: LinkedInPreviewProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    content: "",
    hashtags: [""],
  });

  // Initialize form when switching to edit mode
  const startEditing = () => {
    setFormData({
      content: draft?.content || "",
      hashtags: draft?.hashtags?.length ? draft.hashtags : [""],
    });
    setIsEditing(true);
  };

  // Save form data directly as JSON
  const saveEdit = () => {
    onChange({
      content: formData.content.trim(),
      hashtags: formData.hashtags.filter((tag) => tag.trim()),
    });
    setIsEditing(false);
  };

  const updateHashtags = (value: string) => {
    const hashtags = value.split(" ").filter((tag) => tag.trim());
    setFormData((prev) => ({
      ...prev,
      hashtags,
    }));
  };

  const mainContent = draft?.content || "";
  const hashtags = draft?.hashtags || [];

  if (isEditing) {
    return (
      <div className={cn("space-y-4", className)}>
        <div className="flex justify-between items-center">
          <h3 className="macos-text-title3 text-foreground">
            Edit LinkedIn Post
          </h3>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={saveEdit}>
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
            <label className="block text-sm font-medium mb-2">
              Post Content
            </label>
            <Textarea
              placeholder="Write your LinkedIn post content here..."
              value={formData.content}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, content: e.target.value }))
              }
              rows={8}
              className="macos-text-body"
            />
            <div className="text-xs text-muted-foreground mt-1">
              {formData.content.length} characters
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Hashtags</label>
            <input
              type="text"
              placeholder="#linkedin #networking #professional"
              value={formData.hashtags.join(" ")}
              onChange={(e) => updateHashtags(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring macos-text-body"
            />
            <div className="text-xs text-muted-foreground mt-1">
              Separate hashtags with spaces
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex justify-between items-center">
        <h3 className="macos-text-title3 text-foreground">
          LinkedIn Post Preview
        </h3>
        {!readOnly && (
          <Button variant="outline" size="sm" onClick={startEditing}>
            <Edit3 className="w-4 h-4 mr-1" />
            Edit
          </Button>
        )}
      </div>

      {/* LinkedIn Post - Authentic Design */}
      <div
        className="bg-white dark:bg-[#1b1f23] border border-[#e0e0e0] dark:border-[#38434f] rounded-lg shadow-sm overflow-hidden"
        style={{
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
        }}
      >
        {/* Post Header */}
        <div className="p-3">
          <div className="flex items-start gap-2">
            {/* Profile Photo - Square with rounded corners like LinkedIn */}
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">V</span>
              </div>
            </div>

            <div className="flex-1 min-w-0">
              {/* Name and Title */}
              <div className="mb-1">
                <button className="text-[#000000] dark:text-white font-semibold text-sm hover:underline hover:text-[#0077b5] dark:hover:text-[#70b7f7]">
                  Vai Gup
                </button>
                <span className="text-[#666666] dark:text-[#b0b0b0] text-xs">
                  {" "}
                  •{" "}
                </span>
                <span className="text-[#666666] dark:text-[#b0b0b0] text-xs">
                  You
                </span>
              </div>
              <div className="text-[#666666] dark:text-[#b0b0b0] text-xs mb-1">
                Founder & CEO at HelloVAI | AI & Automation Expert
              </div>
              <div className="flex items-center text-[#666666] dark:text-[#b0b0b0] text-xs">
                <span>1m</span>
                <span className="mx-1">•</span>
                <svg className="w-3 h-3 fill-current" viewBox="0 0 16 16">
                  <path d="M8 16A8 8 0 1 1 8 0a8 8 0 0 1 0 16ZM8 2a6 6 0 1 0 0 12A6 6 0 0 0 8 2Z" />
                  <path d="M8 6a2 2 0 1 1 0-4 2 2 0 0 1 0 4ZM5 9a1 1 0 0 1 1-1h4a1 1 0 1 1 0 2H6a1 1 0 0 1-1-1Z" />
                </svg>
              </div>
            </div>

            {/* More Options */}
            <button className="w-8 h-8 rounded-full hover:bg-[#f3f2ef] dark:hover:bg-[#2f3237] flex items-center justify-center">
              <MoreHorizontal className="w-4 h-4 text-[#666666] dark:text-[#b0b0b0]" />
            </button>
          </div>
        </div>

        {/* Post Content */}
        <div className="px-3 pb-3">
          {mainContent ? (
            <div className="text-[#000000] dark:text-white text-sm leading-5 whitespace-pre-wrap mb-2">
              {mainContent}
              {hashtags.length > 0 && (
                <div className="mt-2">
                  {hashtags.map((tag, i) => (
                    <span
                      key={i}
                      className="text-[#0077b5] dark:text-[#70b7f7] hover:underline cursor-pointer font-medium mr-1"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-[#666666] dark:text-[#b0b0b0] text-sm italic">
              Your LinkedIn post content will appear here...
            </div>
          )}
        </div>

        {/* Engagement Stats */}
        <div className="px-3 py-2 border-t border-[#e0e0e0] dark:border-[#38434f]">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-1">
              <div className="flex -space-x-1">
                <div className="w-4 h-4 bg-[#0077b5] rounded-full flex items-center justify-center border border-white dark:border-[#1b1f23]">
                  <ThumbsUp className="w-2.5 h-2.5 text-white" />
                </div>
                <div className="w-4 h-4 bg-[#057642] rounded-full flex items-center justify-center border border-white dark:border-[#1b1f23]">
                  <span className="text-white text-[8px]">👏</span>
                </div>
                <div className="w-4 h-4 bg-[#8f5849] rounded-full flex items-center justify-center border border-white dark:border-[#1b1f23]">
                  <span className="text-white text-[8px]">❤️</span>
                </div>
              </div>
              <span className="text-[#666666] dark:text-[#b0b0b0] ml-1 hover:underline cursor-pointer hover:text-[#0077b5] dark:hover:text-[#70b7f7]">
                42 reactions
              </span>
            </div>
            <div className="flex items-center gap-3 text-[#666666] dark:text-[#b0b0b0]">
              <span className="hover:underline cursor-pointer hover:text-[#0077b5] dark:hover:text-[#70b7f7]">
                8 comments
              </span>
              <span className="hover:underline cursor-pointer hover:text-[#0077b5] dark:hover:text-[#70b7f7]">
                12 reposts
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="border-t border-[#e0e0e0] dark:border-[#38434f]">
          <div className="flex">
            <button className="flex-1 flex items-center justify-center py-2.5 hover:bg-[#f3f2ef] dark:hover:bg-[#2f3237] group">
              <ThumbsUp className="w-5 h-5 text-[#666666] dark:text-[#b0b0b0] group-hover:text-[#0077b5] mr-2" />
              <span className="text-[#666666] dark:text-[#b0b0b0] group-hover:text-[#0077b5] text-sm font-medium">
                Like
              </span>
            </button>
            <button className="flex-1 flex items-center justify-center py-2.5 hover:bg-[#f3f2ef] dark:hover:bg-[#2f3237] group">
              <MessageSquare className="w-5 h-5 text-[#666666] dark:text-[#b0b0b0] group-hover:text-[#0077b5] mr-2" />
              <span className="text-[#666666] dark:text-[#b0b0b0] group-hover:text-[#0077b5] text-sm font-medium">
                Comment
              </span>
            </button>
            <button className="flex-1 flex items-center justify-center py-2.5 hover:bg-[#f3f2ef] dark:hover:bg-[#2f3237] group">
              <Repeat2 className="w-5 h-5 text-[#666666] dark:text-[#b0b0b0] group-hover:text-[#0077b5] mr-2" />
              <span className="text-[#666666] dark:text-[#b0b0b0] group-hover:text-[#0077b5] text-sm font-medium">
                Repost
              </span>
            </button>
            <button className="flex-1 flex items-center justify-center py-2.5 hover:bg-[#f3f2ef] dark:hover:bg-[#2f3237] group">
              <Send className="w-5 h-5 text-[#666666] dark:text-[#b0b0b0] group-hover:text-[#0077b5] mr-2" />
              <span className="text-[#666666] dark:text-[#b0b0b0] group-hover:text-[#0077b5] text-sm font-medium">
                Send
              </span>
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-[#f9fafb] dark:bg-[#2f3237] px-3 py-2 text-center border-t border-[#e0e0e0] dark:border-[#38434f]">
          <span className="text-[#666666] dark:text-[#b0b0b0] text-xs">
            LinkedIn post preview • Click Edit to modify
          </span>
        </div>
      </div>
    </div>
  );
}
