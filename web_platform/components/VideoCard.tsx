"use client"

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  ThumbsUp,
  ThumbsDown,
  Play,
  Clock,
  Eye,
  ExternalLink
} from 'lucide-react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

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

interface VideoCardProps {
  video: Video
  onFeedback: (videoId: string, feedback: 'up' | 'down') => void
  formatDuration: (seconds: number) => string
  formatNumber: (num: number) => string
}

export function VideoCard({ video, onFeedback, formatDuration, formatNumber }: VideoCardProps) {
  const [feedbackGiven, setFeedbackGiven] = useState<'up' | 'down' | null>(null)

  const handleFeedback = (feedback: 'up' | 'down') => {
    setFeedbackGiven(feedback)
    onFeedback(video.video_id, feedback)
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'bg-green-100 text-green-800'
    if (score >= 0.4) return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }

  const getEducationalLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-800'
      case 'intermediate': return 'bg-blue-100 text-blue-800'
      case 'advanced': return 'bg-purple-100 text-purple-800'
      case 'academic': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const openVideo = () => {
    window.open(`https://youtube.com/watch?v=${video.video_id}`, '_blank')
  }

  return (
    <Card className="bg-white border-[#E0E0E0] hover:shadow-lg transition-shadow duration-200 overflow-hidden group">
      <div className="relative">
        {/* Thumbnail */}
        <div
          className="aspect-video bg-gray-200 cursor-pointer relative overflow-hidden"
          onClick={openVideo}
        >
          {video.thumbnail ? (
            <img
              src={video.thumbnail}
              alt={video.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
            />
          ) : (
            <div className="flex items-center justify-center h-full bg-gray-100">
              <Play className="h-12 w-12 text-gray-400" />
            </div>
          )}

          {/* Play overlay */}
          <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
            <Play className="h-12 w-12 text-white fill-white" />
          </div>

          {/* Duration badge */}
          {video.duration > 0 && (
            <div className="absolute bottom-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-xs">
              {formatDuration(video.duration)}
            </div>
          )}

          {/* Recommendation score */}
          <div className="absolute top-2 left-2">
            <Badge className={getScoreColor(video.recommendation_score)}>
              {Math.round(video.recommendation_score * 100)}% match
            </Badge>
          </div>
        </div>
      </div>

      <CardContent className="p-4">
        {/* Title and Channel */}
        <div className="mb-3">
          <h3
            className="font-semibold text-[#3E2723] line-clamp-2 cursor-pointer hover:text-[#E76F51] transition-colors"
            onClick={openVideo}
            title={video.title}
          >
            {video.title}
          </h3>
          <p className="text-sm text-[#6B5B55] mt-1">{video.channel}</p>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 text-xs text-[#6B5B55] mb-3">
          {video.view_count > 0 && (
            <div className="flex items-center gap-1">
              <Eye className="h-3 w-3" />
              {formatNumber(video.view_count)} views
            </div>
          )}
          {video.duration > 0 && (
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatDuration(video.duration)}
            </div>
          )}
        </div>

        {/* Genres */}
        <div className="flex flex-wrap gap-1 mb-3">
          {video.genres?.primary && (
            <Badge variant="secondary" className="text-xs">
              {video.genres.primary}
            </Badge>
          )}
          {video.genres?.secondary && video.genres.secondary !== video.genres.primary && (
            <Badge variant="outline" className="text-xs">
              {video.genres.secondary}
            </Badge>
          )}
          {video.genres?.educational_level && (
            <Badge className={`text-xs ${getEducationalLevelColor(video.genres.educational_level)}`}>
              {video.genres.educational_level}
            </Badge>
          )}
        </div>

        {/* Match reasons */}
        {video.match_reasons && video.match_reasons.length > 0 && (
          <div className="mb-3">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <p className="text-xs text-[#6B5B55] cursor-help truncate">
                    💡 {video.match_reasons[0]}
                  </p>
                </TooltipTrigger>
                <TooltipContent>
                  <div className="max-w-xs">
                    {video.match_reasons.map((reason, i) => (
                      <p key={i} className="text-xs">• {reason}</p>
                    ))}
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between items-center">
          <div className="flex gap-2">
            <Button
              size="sm"
              variant={feedbackGiven === 'up' ? 'default' : 'outline'}
              onClick={() => handleFeedback('up')}
              className="h-8 px-2"
            >
              <ThumbsUp className="h-3 w-3" />
            </Button>
            <Button
              size="sm"
              variant={feedbackGiven === 'down' ? 'default' : 'outline'}
              onClick={() => handleFeedback('down')}
              className="h-8 px-2"
            >
              <ThumbsDown className="h-3 w-3" />
            </Button>
          </div>

          <Button
            size="sm"
            variant="ghost"
            onClick={openVideo}
            className="h-8 px-2 text-[#E76F51] hover:text-[#E76F51] hover:bg-[#E76F51]/10"
          >
            <ExternalLink className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}