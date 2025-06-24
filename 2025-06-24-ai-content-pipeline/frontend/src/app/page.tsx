import { VideoList } from '@/components/VideoList'
import { ZoomRecordingsList } from '@/components/ZoomRecordingsList'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-4 tracking-tight">
            AI Content Pipeline
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Transform your Zoom recordings into YouTube videos and AI-generated content drafts
          </p>
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Video List Section */}
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-gray-900 flex items-center">
              Your Videos
            </h2>
            <VideoList />
          </div>

          {/* Zoom Recordings Section */}
          <div className="space-y-6">
            <ZoomRecordingsList />
          </div>
        </div>
      </div>
    </div>
  )
}
