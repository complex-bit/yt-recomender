"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import {
  TrendingUp,
  Clock,
  PlayCircle,
  Target,
  Brain,
  Star
} from 'lucide-react'

interface UserAnalytics {
  top_genres: Record<string, Record<string, number>>
  top_channels: Record<string, number>
  completion_rate: number
  total_watch_time: number
  video_count: number
}

interface AnalyticsDashboardProps {
  analytics: UserAnalytics | null
}

export function AnalyticsDashboard({ analytics }: AnalyticsDashboardProps) {
  if (!analytics) {
    return (
      <div className="space-y-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="bg-white">
            <CardContent className="p-6">
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                <div className="h-32 bg-gray-200 rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
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

  const getCompletionRateColor = (rate: number) => {
    if (rate >= 0.8) return 'text-green-600'
    if (rate >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getCompletionRateLabel = (rate: number) => {
    if (rate >= 0.8) return 'Excellent'
    if (rate >= 0.6) return 'Good'
    if (rate >= 0.4) return 'Average'
    return 'Low'
  }

  // Prepare chart data
  const channelData = Object.entries(analytics.top_channels)
    .slice(0, 5)
    .map(([name, score]) => ({
      name: name.length > 15 ? name.substring(0, 12) + '...' : name,
      fullName: name,
      score: Math.round(score * 100)
    }))

  const genreData = Object.entries(analytics.top_genres)
    .flatMap(([category, genres]) =>
      Object.entries(genres).map(([genre, score]) => ({
        name: genre,
        category,
        score: Math.round(score * 100)
      }))
    )
    .sort((a, b) => b.score - a.score)
    .slice(0, 8)

  const pieColors = [
    '#E76F51', '#F4A261', '#E9C46A', '#2A9D8F',
    '#264653', '#E63946', '#F77F00', '#FCBF49'
  ]

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-white border-[#E0E0E0]">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[#6B5B55]">Total Watch Time</p>
                <p className="text-2xl font-bold text-[#3E2723]">
                  {formatWatchTime(analytics.total_watch_time)}
                </p>
              </div>
              <Clock className="h-8 w-8 text-[#E76F51]" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-[#E0E0E0]">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[#6B5B55]">Videos Watched</p>
                <p className="text-2xl font-bold text-[#3E2723]">
                  {analytics.video_count}
                </p>
              </div>
              <PlayCircle className="h-8 w-8 text-[#E76F51]" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-[#E0E0E0]">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[#6B5B55]">Completion Rate</p>
                <p className={`text-2xl font-bold ${getCompletionRateColor(analytics.completion_rate)}`}>
                  {Math.round(analytics.completion_rate * 100)}%
                </p>
                <p className="text-xs text-[#6B5B55]">
                  {getCompletionRateLabel(analytics.completion_rate)}
                </p>
              </div>
              <Target className="h-8 w-8 text-[#E76F51]" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-[#E0E0E0]">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[#6B5B55]">Avg per Video</p>
                <p className="text-2xl font-bold text-[#3E2723]">
                  {formatWatchTime(analytics.total_watch_time / analytics.video_count || 0)}
                </p>
              </div>
              <Star className="h-8 w-8 text-[#E76F51]" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Channel Preferences */}
        <Card className="bg-white border-[#E0E0E0]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Top Channels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={channelData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 12 }}
                  stroke="#6B5B55"
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  stroke="#6B5B55"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E0E0E0',
                    borderRadius: '8px'
                  }}
                  formatter={(value, name, props) => [
                    `${value}%`,
                    `Preference Score`
                  ]}
                  labelFormatter={(label, payload) => {
                    const item = payload?.[0]?.payload
                    return item?.fullName || label
                  }}
                />
                <Bar dataKey="score" fill="#E76F51" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Genre Distribution */}
        <Card className="bg-white border-[#E0E0E0]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Interest Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={genreData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={2}
                  dataKey="score"
                >
                  {genreData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={pieColors[index % pieColors.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E0E0E0',
                    borderRadius: '8px'
                  }}
                  formatter={(value) => [`${value}%`, 'Interest Score']}
                />
              </PieChart>
            </ResponsiveContainer>

            {/* Legend */}
            <div className="mt-4 space-y-2">
              {genreData.slice(0, 6).map((item, index) => (
                <div key={item.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: pieColors[index % pieColors.length] }}
                    />
                    <span>{item.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {item.category}
                    </Badge>
                  </div>
                  <span className="text-[#6B5B55]">{item.score}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Breakdown */}
      <Card className="bg-white border-[#E0E0E0]">
        <CardHeader>
          <CardTitle>Viewing Patterns</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Completion Rate Progress */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Video Completion Rate</span>
              <span className="text-sm text-[#6B5B55]">
                {Math.round(analytics.completion_rate * 100)}%
              </span>
            </div>
            <Progress
              value={analytics.completion_rate * 100}
              className="h-2"
            />
            <p className="text-xs text-[#6B5B55] mt-1">
              You typically watch {Math.round(analytics.completion_rate * 100)}% of each video
            </p>
          </div>

          {/* Insights */}
          <div className="bg-[#FAF3E0] p-4 rounded-lg">
            <h4 className="font-medium text-[#3E2723] mb-2">Personalization Insights</h4>
            <div className="space-y-1 text-sm text-[#6B5B55]">
              <p>• You prefer {Object.keys(analytics.top_channels)[0]} content</p>
              <p>• Your completion rate of {Math.round(analytics.completion_rate * 100)}% is {
                analytics.completion_rate > 0.7 ? 'above' : 'below'
              } average</p>
              <p>• You've watched {analytics.video_count} videos totaling {formatWatchTime(analytics.total_watch_time)}</p>
              {genreData[0] && (
                <p>• Your strongest interest is in {genreData[0].name} ({genreData[0].score}%)</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}