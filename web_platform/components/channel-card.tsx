import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import type { TopChannel } from "@/lib/api"

interface ChannelCardProps {
  channel: TopChannel
}

export function ChannelCard({ channel }: ChannelCardProps) {
  const initials = channel.channelTitle
    .split(" ")
    .map((word) => word[0])
    .join("")
    .slice(0, 2)
    .toUpperCase()

  return (
    <div className="flex items-center gap-4 rounded-2xl bg-[#FFF9F0] p-4 shadow-[0_4px_6px_rgba(0,0,0,0.1)] transition-all hover:shadow-[0_6px_12px_rgba(0,0,0,0.15)] hover:-translate-y-1">
      <Avatar className="h-16 w-16 border-2 border-[#D4C5B9]">
        <AvatarImage
          src={`/.jpg?height=64&width=64&query=${channel.channelTitle}`}
          alt={channel.channelTitle}
        />
        <AvatarFallback className="bg-[#E76F51] text-white font-semibold">{initials}</AvatarFallback>
      </Avatar>

      <div className="flex-1">
        <h3 className="font-bold text-[#3E2723] text-lg leading-tight">{channel.channelTitle}</h3>
        <p className="text-sm text-[#6B5B55] mt-1">{channel.watchCount} videos watched</p>
      </div>

      <Badge className="rounded-full bg-[#E76F51] text-white hover:bg-[#d65a3a] px-3 py-1">{channel.category}</Badge>
    </div>
  )
}
