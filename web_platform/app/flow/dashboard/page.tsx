"use client"

import { useEffect, useState } from 'react'
import { VideoCard } from '@/components/VideoCard'
import { FilterPanel } from '@/components/FilterPanel'
import { UserProfile } from '@/components/UserProfile'
import { AnalyticsDashboard } from '@/components/AnalyticsDashboard'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { RefreshCw } from 'lucide-react'

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

export default function Dashboard() {
  const [recommendations, setRecommendations] = useState<Video[]>([])
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    educational_level: '',
    min_duration: 0,
    max_duration: 3600,
    channels: [] as string[]
  })

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      params.append('limit', '20')

      if (filters.educational_level) {
        params.append('educational_level', filters.educational_level)
      }
      if (filters.min_duration > 0) {
        params.append('min_duration', filters.min_duration.toString())
      }
      if (filters.max_duration < 3600) {
        params.append('max_duration', filters.max_duration.toString())
      }
      filters.channels.forEach(channel => {
        params.append('channels', channel)
      })

      const response = await fetch(`http://localhost:5000/api/recommendations?${params}`)
      const data = await response.json()

      if (data.recommendations) {
        setRecommendations(data.recommendations)
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error)
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

      // Optionally refresh recommendations after feedback
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

  return (
    <div className="min-h-screen bg-[#FAF3E0] p-6">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-[#3E2723] mb-2">Your Recommendations</h1>
          <p className="text-[#6B5B55]">Personalized videos based on your watch history</p>
        </header>

        <Tabs defaultValue="recommendations" className="space-y-6">
          <TabsList className="bg-white border border-[#E0E0E0]">
            <TabsTrigger value="recommendations">For You</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="profile">Profile</TabsTrigger>
          </TabsList>

          <TabsContent value="recommendations" className="space-y-6">
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
                    {recommendations.length} recommendations found
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

                {!loading && recommendations.length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-[#6B5B55] text-lg">
                      No recommendations found with current filters.
                    </p>
                    <Button
                      onClick={() => setFilters({
                        educational_level: '',
                        min_duration: 0,
                        max_duration: 3600,
                        channels: []
                      })}
                      variant="outline"
                      className="mt-4"
                    >
                      Clear Filters
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="analytics">
            <AnalyticsDashboard analytics={analytics} />
          </TabsContent>

          <TabsContent value="profile">
            <UserProfile analytics={analytics} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}