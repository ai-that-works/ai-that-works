import { VideoImportForm } from '@/components/VideoImportForm'
import { VideoList } from '@/components/VideoList'

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Content Pipeline
          </h1>
          <p className="text-gray-600">
            Turn your Zoom recordings into YouTube videos and AI-generated content drafts
          </p>
        </div>

        {/* Import Form */}
        <div className="mb-8">
          <VideoImportForm />
        </div>

        {/* Video List */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Your Videos
          </h2>
          <VideoList />
        </div>
      </div>
    </div>
  )
}
