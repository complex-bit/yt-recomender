"use client"

import { ThumbsUp, ThumbsDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { WatchHistoryItem } from "@/lib/dummy-data"
import { formatDuration } from "@/lib/dummy-data"

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
      <div className="px-4 pb-4">
        <h3 className="font-bold text-[#3E2723] leading-tight line-clamp-2 mb-1">{video.title}</h3>
        <p className="text-sm text-[#6B5B55] mb-3">{video.channelTitle}</p>

        {/* Interaction buttons */}
        <div className="flex gap-2">
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
