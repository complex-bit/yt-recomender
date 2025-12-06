"use client"

import { ThumbsUp, ThumbsDown, Eye, Heart, MessageCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { WatchHistoryItem } from "@/lib/api"

// Helper functions
function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
  }
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

function formatNumber(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  }
  return num.toString()
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMonths = (now.getFullYear() - date.getFullYear()) * 12 + (now.getMonth() - date.getMonth())

  if (diffInMonths < 1) {
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
    if (diffInDays < 7) {
      return `${diffInDays}d ago`
    }
    return `${Math.floor(diffInDays / 7)}w ago`
  } else if (diffInMonths < 12) {
    return `${diffInMonths}mo ago`
  } else {
    return `${Math.floor(diffInMonths / 12)}y ago`
  }
}

interface VideoCardProps {
  video: WatchHistoryItem
  onThumbsUp?: () => void
  onThumbsDown?: () => void
}

export function VideoCard({ video, onThumbsUp, onThumbsDown }: VideoCardProps) {
  return (
    <div className="group rounded-xl bg-[#FFF9F0] shadow-[0_4px_6px_rgba(0,0,0,0.1)] transition-all hover:shadow-[0_8px_16px_rgba(0,0,0,0.15)] hover:-translate-y-1">
      {/* Polaroid-style thumbnail */}
      <div className="relative p-3 pb-2">
        <div className="relative overflow-hidden rounded-lg aspect-video bg-[#D4C5B9]">
          <img src={video.thumbnail || "/placeholder.svg"} alt={video.title} className="w-full h-full object-cover" />
          {/* Duration badge styled like film timecode */}
          <div className="absolute bottom-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-xs font-mono">
            {formatDuration(video.duration)}
          </div>
        </div>
      </div>

      {/* Video info */}
      <div className="px-4 pb-4 space-y-2">
        <h3 className="font-bold text-[#3E2723] leading-tight line-clamp-2 mb-1">{video.title}</h3>

        <div className="flex items-center justify-between text-sm text-[#6B5B55]">
          <span>{video.channelTitle}</span>
          <span>{formatDate(video.published_at)}</span>
        </div>

        {/* Description preview */}
        {video.description && (
          <p className="text-xs text-[#8D7B73] line-clamp-2 leading-relaxed">
            {video.description}
          </p>
        )}

        {/* Stats row */}
        <div className="flex items-center justify-between text-xs text-[#6B5B55] pt-1">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1">
              <Eye className="h-3 w-3" />
              <span>{formatNumber(video.view_count)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Heart className="h-3 w-3" />
              <span>{formatNumber(video.like_count)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <MessageCircle className="h-3 w-3" />
              <span>{formatNumber(video.comment_count)}</span>
            </div>
          </div>
        </div>

        {/* Tags */}
        {video.tags && video.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {video.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs bg-[#E8DDD4] text-[#6B5B55] rounded-full"
              >
                {tag}
              </span>
            ))}
            {video.tags.length > 3 && (
              <span className="px-2 py-1 text-xs text-[#8D7B73]">
                +{video.tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Interaction buttons */}
        <div className="flex gap-2 pt-2">
          <Button
            size="sm"
            variant="ghost"
            className="flex-1 hover:bg-[#E76F51] hover:text-white transition-colors"
            onClick={onThumbsUp}
          >
            <ThumbsUp className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="flex-1 hover:bg-[#F08080] hover:text-white transition-colors"
            onClick={onThumbsDown}
          >
            <ThumbsDown className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
