"use client"

import { useState } from "react"
import { VideoList } from "@/components/home/video-list"
import { ZoomRecordingsList } from "@/components/home/zoom-recordings-list"

type FilterType = "all" | "processing" | "ready" | "failed"

export default function HomePage() {
  const [selectedFilter, setSelectedFilter] = useState<FilterType>("all")
  
  const filters = [
    { id: "all" as FilterType, label: "All Videos", color: "bg-primary", count: null },
    { id: "processing" as FilterType, label: "Processing", color: "bg-orange-500", count: null },
    { id: "ready" as FilterType, label: "Ready", color: "bg-green-500", count: null },
    { id: "failed" as FilterType, label: "Failed", color: "bg-red-500", count: null }
  ]

  return (
    <div className="min-h-screen flex bg-background">
      {/* Native macOS Sidebar */}
      <div className="macos-sidebar macos-material-sidebar border-r border-border flex flex-col">
        {/* Sidebar Header */}
        <div className="p-4 border-b border-border">
          <h1 className="macos-text-title2 text-foreground font-semibold">
            AI Content Pipeline
          </h1>
          <p className="macos-text-callout text-muted-foreground mt-1">
            Video Processing
          </p>
        </div>
        
        {/* Sidebar Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {filters.map((filter) => (
            <button
              key={filter.id}
              onClick={() => setSelectedFilter(filter.id)}
              className={`macos-list-item w-full text-left transition-all duration-150 macos-focus ${
                selectedFilter === filter.id ? "selected" : ""
              }`}
            >
              <div className="flex items-center gap-2">
                <div className={`w-4 h-4 ${filter.color} rounded-sm`}></div>
                <span className="macos-text-body">{filter.label}</span>
              </div>
            </button>
          ))}
        </nav>
        
        {/* Sidebar Footer */}
        <div className="p-4 border-t border-border">
          <p className="macos-text-caption1 text-muted-foreground">
            {new Date().getFullYear()} AI Content Pipeline
          </p>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Native macOS Toolbar */}
        <div className="macos-material-toolbar p-4 flex items-center justify-between">
          <div>
            <h2 className="macos-text-title1 text-foreground">Content Library</h2>
            <p className="macos-text-callout text-muted-foreground">
              Manage your video content and Zoom recordings
            </p>
          </div>
        </div>

        {/* Content Area with native spacing */}
        <main className="flex-1 p-6 overflow-auto macos-scroll-area macos-scroll-fade">
          <div className="max-w-none space-y-8">
            {/* Main Content Grid */}
            <div className="grid gap-6 lg:grid-cols-2 items-start">
              {/* Processed Videos Section */}
              <section aria-labelledby="your-videos-heading" className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="macos-text-title2 text-foreground">
                    {selectedFilter === "all" ? "Your Processed Videos" : 
                     `${selectedFilter.charAt(0).toUpperCase() + selectedFilter.slice(1)} Videos`}
                  </h3>
                  <span className="macos-text-callout text-muted-foreground">Recently updated</span>
                </div>
                <VideoList filter={selectedFilter} />
              </section>

              {/* Zoom Recordings Section */}
              <section aria-labelledby="zoom-recordings-heading" className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="macos-text-title2 text-foreground">Available Zoom Recordings</h3>
                  <span className="macos-text-callout text-muted-foreground">Last 3 months</span>
                </div>
                <ZoomRecordingsList />
              </section>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
