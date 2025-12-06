"use client"

import { motion } from "framer-motion"
import type { TopChannel } from "@/lib/api"

interface ChannelIconProps {
  channel: TopChannel
  delay?: number
}

export function ChannelIcon({ channel, delay = 0 }: ChannelIconProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0, rotate: -180 }}
      animate={{ opacity: 1, scale: 1, rotate: 0 }}
      transition={{ duration: 0.6, delay, type: "spring", bounce: 0.4 }}
      className="relative group"
    >
      <div className="w-14 h-14 rounded-full shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 cursor-pointer border-2 border-[#8D6E63] overflow-hidden bg-white">
        {channel.channelAvatar ? (
          <img
            src={channel.channelAvatar}
            alt={channel.channelTitle}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-[#6B8E6A] to-[#557153] flex items-center justify-center">
            <span className="text-xl font-bold text-white">{channel.channelTitle.charAt(0)}</span>
          </div>
        )}
      </div>

      {/* Tooltip on hover */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1 bg-[#3E2723] text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
        {channel.channelTitle}
        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-[#3E2723]"></div>
      </div>

      {/* Watch count badge */}
      <div className="absolute -top-1 -right-1 bg-[#E76F51] text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center shadow-md">
        {channel.watchCount}
      </div>
    </motion.div>
  )
}
