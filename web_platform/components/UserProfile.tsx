"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import {
  User,
  Clock,
  PlayCircle,
  TrendingUp,
  BookOpen,
  Heart,
  Settings,
  Download
} from 'lucide-react'

interface UserAnalytics {
  top_genres: Record<string, Record<string, number>>
  top_channels: Record<string, number>
  completion_rate: number
  total_watch_time: number
  video_count: number
}

interface UserProfileProps {
  analytics: UserAnalytics | null
}

export function UserProfile({ analytics }: UserProfileProps) {
  if (!analytics) {
    return (
      <div className="space-y-6">
        <Card className="bg-white">
          <CardContent className="p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const formatWatchTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    }
    return `${minutes}m`
  }

  const getViewerType = () => {
    const avgCompletion = analytics.completion_rate
    const avgVideoLength = analytics.total_watch_time / analytics.video_count

    if (avgCompletion > 0.8 && avgVideoLength > 1200) {
      return { type: 'Deep Learner', icon: '🧠', description: 'You love in-depth, educational content' }
    }
    if (avgCompletion > 0.7) {
      return { type: 'Focused Viewer', icon: '🎯', description: 'You watch videos from start to finish' }
    }
    if (analytics.video_count > 20) {
      return { type: 'Content Explorer', icon: '🔍', description: 'You enjoy discovering new topics' }
    }
    if (avgVideoLength < 600) {
      return { type: 'Quick Learner', icon: '⚡', description: 'You prefer bite-sized content' }
    }
    return { type: 'Casual Viewer', icon: '😊', description: 'You enjoy a variety of content' }
  }

  const viewerProfile = getViewerType()

  // Get top interests
  const topInterests = Object.entries(analytics.top_genres)
    .flatMap(([category, genres]) =>
      Object.entries(genres).map(([genre, score]) => ({
        name: genre,
        category,
        score: score
      }))
    )
    .sort((a, b) => b.score - a.score)
    .slice(0, 6)

  const topChannels = Object.entries(analytics.top_channels)
    .slice(0, 5)
    .map(([name, score]) => ({ name, score }))

  const profileStrength = Math.min(
    (analytics.video_count / 20) * 0.3 +
    (analytics.completion_rate) * 0.4 +
    (Object.keys(analytics.top_channels).length / 5) * 0.3,
    1
  )

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <Card className="bg-gradient-to-br from-[#E76F51] to-[#F4A261] text-white border-0">
        <CardContent className="p-8">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center text-4xl">
                {viewerProfile.icon}
              </div>
              <div>
                <h2 className="text-3xl font-bold mb-2">Science Enthusiast</h2>
                <p className="text-white/80 text-lg mb-1">{viewerProfile.type}</p>
                <p className="text-white/70 text-sm">{viewerProfile.description}</p>
              </div>
            </div>
            <Button variant="secondary" size="sm" className="gap-2">
              <Settings className="h-4 w-4" />
              Edit Profile
            </Button>
          </div>

          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <PlayCircle className="h-6 w-6 mx-auto mb-1" />
              <div className="text-2xl font-bold">{analytics.video_count}</div>
              <div className="text-white/70 text-sm">Videos Watched</div>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <Clock className="h-6 w-6 mx-auto mb-1" />
              <div className="text-2xl font-bold">{formatWatchTime(analytics.total_watch_time)}</div>
              <div className="text-white/70 text-sm">Total Time</div>
            </div>
            <div className="bg-white/10 rounded-lg p-3 text-center">
              <TrendingUp className="h-6 w-6 mx-auto mb-1" />
              <div className="text-2xl font-bold">{Math.round(analytics.completion_rate * 100)}%</div>
              <div className="text-white/70 text-sm">Completion</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Interests */}
        <Card className="bg-white border-[#E0E0E0]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Your Interests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topInterests.map((interest, index) => (
                <div key={interest.name} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{interest.name}</span>
                      <Badge variant="outline" className="text-xs">
                        {interest.category}
                      </Badge>
                    </div>
                    <span className="text-sm text-[#6B5B55]">
                      {Math.round(interest.score * 100)}%
                    </span>
                  </div>
                  <Progress
                    value={interest.score * 100}
                    className="h-2"
                  />
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-[#FAF3E0] rounded-lg">
              <p className="text-sm text-[#6B5B55]">
                <strong>Profile Strength:</strong> {Math.round(profileStrength * 100)}%
              </p>
              <Progress value={profileStrength * 100} className="h-2 mt-2" />
              <p className="text-xs text-[#6B5B55] mt-2">
                {profileStrength > 0.8
                  ? 'Your profile is very detailed! Recommendations will be highly personalized.'
                  : profileStrength > 0.5
                  ? 'Good profile data. Watch more videos to improve recommendations.'
                  : 'Keep watching videos to build a stronger preference profile.'
                }
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Favorite Channels */}
        <Card className="bg-white border-[#E0E0E0]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5" />
              Favorite Channels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topChannels.map((channel, index) => (
                <div key={channel.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-[#E76F51] rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{channel.name}</p>
                      <p className="text-sm text-[#6B5B55]">
                        {Math.round(channel.score * 100)}% preference
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    View Channel
                  </Button>
                </div>
              ))}
            </div>

            {topChannels.length === 0 && (
              <div className="text-center py-8 text-[#6B5B55]">
                <User className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No channel preferences yet</p>
                <p className="text-sm">Watch more videos to see your favorite channels</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recommendations Settings */}
      <Card className="bg-white border-[#E0E0E0]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Recommendation Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-[#E0E0E0] rounded-lg">
              <h4 className="font-medium mb-2">Discovery Mode</h4>
              <p className="text-sm text-[#6B5B55] mb-3">
                Explore content outside your usual preferences
              </p>
              <Button variant="outline" size="sm" className="w-full">
                Enable Discovery
              </Button>
            </div>

            <div className="p-4 border border-[#E0E0E0] rounded-lg">
              <h4 className="font-medium mb-2">Focus Mode</h4>
              <p className="text-sm text-[#6B5B55] mb-3">
                Only show content from your top interests
              </p>
              <Button variant="outline" size="sm" className="w-full">
                Enable Focus
              </Button>
            </div>

            <div className="p-4 border border-[#E0E0E0] rounded-lg">
              <h4 className="font-medium mb-2">Export Data</h4>
              <p className="text-sm text-[#6B5B55] mb-3">
                Download your viewing analytics
              </p>
              <Button variant="outline" size="sm" className="w-full gap-2">
                <Download className="h-4 w-4" />
                Export
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Viewing Achievements */}
      <Card className="bg-white border-[#E0E0E0]">
        <CardHeader>
          <CardTitle>Viewing Achievements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gradient-to-br from-yellow-100 to-yellow-200 rounded-lg">
              <div className="text-3xl mb-2">🏆</div>
              <div className="font-medium text-sm">Knowledge Seeker</div>
              <div className="text-xs text-gray-600">10+ educational videos</div>
            </div>

            <div className="text-center p-4 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg">
              <div className="text-3xl mb-2">🎯</div>
              <div className="font-medium text-sm">Focused Viewer</div>
              <div className="text-xs text-gray-600">80%+ completion rate</div>
            </div>

            <div className="text-center p-4 bg-gradient-to-br from-green-100 to-green-200 rounded-lg">
              <div className="text-3xl mb-2">⏰</div>
              <div className="font-medium text-sm">Time Well Spent</div>
              <div className="text-xs text-gray-600">{formatWatchTime(analytics.total_watch_time)} watched</div>
            </div>

            <div className="text-center p-4 bg-gradient-to-br from-purple-100 to-purple-200 rounded-lg">
              <div className="text-3xl mb-2">🔍</div>
              <div className="font-medium text-sm">Explorer</div>
              <div className="text-xs text-gray-600">{Object.keys(analytics.top_genres).length}+ topics</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}