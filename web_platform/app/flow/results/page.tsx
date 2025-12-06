"use client"

import { useRouter } from "next/navigation"
import { useState, useEffect } from "react"
import { VideoCard } from "@/components/VideoCard"
import { FilterPanel } from "@/components/FilterPanel"
import { FlowProgress } from "@/components/flow-progress"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useFlow } from "@/lib/flow-context"
import { RotateCcw, RefreshCw } from "lucide-react"

interface Video {
  video_id: string
  title: string
  channel: string
  description: string
  thumbnail: string
  duration: number
  view_count: number
  recommendation_score: number
  match_reasons: string[]
  genres: {
    primary: string
    secondary: string
    sub: string
    content_type: string
    educational_level: string
    target_audience: string
  }
}

interface UserAnalytics {
  top_genres: Record<string, Record<string, number>>
  top_channels: Record<string, number>
  completion_rate: number
  total_watch_time: number
  video_count: number
}

export default function ResultsPage() {
  const router = useRouter()
  const { flow, updateFlow, resetFlow } = useFlow()
  const [recommendations, setRecommendations] = useState<Video[]>([])
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState({
    min_duration: 0,
    max_duration: 3600,
    popularity: 50,
    recency: 50,
    uniqueness: 50,
    channels: [] as string[]
  })

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      params.append('limit', '20')

      if (filters.min_duration > 0) {
        params.append('min_duration', filters.min_duration.toString())
      }
      if (filters.max_duration < 3600) {
        params.append('max_duration', filters.max_duration.toString())
      }
      if (filters.popularity !== 50) {
        params.append('popularity', filters.popularity.toString())
      }
      if (filters.recency !== 50) {
        params.append('recency', filters.recency.toString())
      }
      if (filters.uniqueness !== 50) {
        params.append('uniqueness', filters.uniqueness.toString())
      }
      filters.channels.forEach(channel => {
        params.append('channels', channel)
      })

      // Add genre path from flow context
      if (flow.selectedGenrePath && flow.selectedGenrePath.length > 0) {
        flow.selectedGenrePath.forEach(node => {
          params.append('genre_path', node.name)
        })
      }

      const response = await fetch(`http://localhost:5000/api/recommendations?${params}`)
      const data = await response.json()

      if (data.recommendations) {
        setRecommendations(data.recommendations)
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error)
      setError('Failed to load recommendations')
    } finally {
      setLoading(false)
    }
  }

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/analytics')
      const data = await response.json()
      setAnalytics(data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    }
  }

  useEffect(() => {
    fetchRecommendations()
    fetchAnalytics()
  }, [filters])

  const handleVideoFeedback = async (videoId: string, feedback: 'up' | 'down') => {
    try {
      await fetch(`http://localhost:5000/api/videos/${videoId}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback })
      })
      fetchRecommendations()
    } catch (error) {
      console.error('Error submitting feedback:', error)
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num.toString()
  }

  const breadcrumb =
    flow.selectedGenrePath.length > 0
      ? flow.selectedGenrePath.map((node) => node.name).join(" → ")
      : flow.searchQuery
        ? `Search: "${flow.searchQuery}"`
        : "Personalized Recommendations"

  return (
    <>
      <FlowProgress currentStep={2} />

      <div className="space-y-6">
        {/* Header with selected genre/search */}
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-[#6B5B55] mb-1 font-['Zilla_Slab',serif]">{breadcrumb}</div>
            <h2 className="font-['Zilla_Slab',serif] text-3xl font-bold text-[#3E2723]">
              Your Personalized Recommendations
            </h2>
            {flow.selectedGenrePath.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {flow.selectedGenrePath.map((node, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {node.name}
                  </Badge>
                ))}
              </div>
            )}
          </div>
          <Button onClick={() => router.push("/")} variant="ghost" size="sm" className="text-[#6B5B55] hover:text-[#3E2723]">
            <RotateCcw className="h-4 w-4 mr-2" />
            Start Over
          </Button>
        </div>

        <div className="flex gap-6">
          {/* Filters Sidebar */}
          <div className="w-80 flex-shrink-0">
            <FilterPanel
              filters={filters}
              onChange={setFilters}
              analytics={analytics}
            />
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <div className="flex justify-between items-center mb-6">
              <p className="text-[#6B5B55]">
                {loading ? (
                  "Loading recommendations..."
                ) : error ? (
                  <span className="text-red-500">{error}</span>
                ) : (
                  `${recommendations.length} personalized recommendations`
                )}
              </p>
              <Button
                onClick={fetchRecommendations}
                disabled={loading}
                variant="outline"
                size="sm"
                className="gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg p-4 animate-pulse">
                    <div className="aspect-video bg-gray-200 rounded mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-red-500 text-lg mb-4">{error}</p>
                <Button onClick={fetchRecommendations} variant="outline">
                  Try Again
                </Button>
              </div>
            ) : recommendations.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-[#6B5B55] text-lg mb-4">
                  No recommendations found with current filters.
                </p>
                <Button
                  onClick={() => setFilters({
                    min_duration: 0,
                    max_duration: 3600,
                    popularity: 50,
                    recency: 50,
                    uniqueness: 50,
                    channels: []
                  })}
                  variant="outline"
                >
                  Clear Filters
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recommendations.map((video) => (
                  <VideoCard
                    key={video.video_id}
                    video={video}
                    onFeedback={handleVideoFeedback}
                    formatDuration={formatDuration}
                    formatNumber={formatNumber}
                  />
                ))}
              </div>
            )}

            {/* Back Button */}
            <div className="flex justify-center mt-8">
              <Button
                onClick={() => router.push("/flow/explore")}
                variant="ghost"
                className="text-[#6B5B55] hover:text-[#3E2723]"
              >
                ← Back to Explore
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
