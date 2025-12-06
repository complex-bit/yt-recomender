"use client"

import { useState } from "react"
import { ChevronDown, ChevronRight, Film } from "lucide-react"
import { cn } from "@/lib/utils"
import type { GenreTreeNode } from "@/lib/api"

interface GenreNodeProps {
  node: GenreTreeNode
  level?: number
  onSelect?: (node: GenreTreeNode) => void
}

const levelColors = [
  "bg-[#E76F51] text-white", // Primary - Terracotta
  "bg-[#2A9D8F] text-white", // Secondary - Forest green
  "bg-[#E9C46A] text-[#3E2723]", // Accent - Goldenrod
]

export function GenreNode({ node, level = 0, onSelect }: GenreNodeProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const hasChildren = node.children && node.children.length > 0
  const colorClass = levelColors[level % levelColors.length]

  const handleClick = () => {
    if (hasChildren) {
      setIsExpanded(!isExpanded)
    } else if (onSelect) {
      onSelect(node)
    }
  }

  return (
    <div className="relative">
      {/* Node button */}
      <button
        onClick={handleClick}
        className={cn(
          "flex items-center gap-3 px-4 py-3 rounded-full transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-0.5 relative overflow-hidden",
          colorClass,
          "before:content-[''] before:absolute before:inset-0 before:bg-[url('/noise.png')] before:opacity-10 before:pointer-events-none",
        )}
      >
        {hasChildren && (
          <span className="flex-shrink-0">
            {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </span>
        )}

        <Film className="h-5 w-5 flex-shrink-0" />

        <span className="font-semibold text-sm whitespace-nowrap">{node.name}</span>

        {node.percentage !== undefined && <span className="text-xs opacity-90 ml-1">{node.percentage}%</span>}
      </button>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div className="ml-8 mt-3 space-y-3 relative before:content-[''] before:absolute before:left-[-16px] before:top-0 before:bottom-0 before:w-[2px] before:bg-[#D4C5B9]">
          {node.children!.map((child) => (
            <GenreNode key={child.id} node={child} level={level + 1} onSelect={onSelect} />
          ))}
        </div>
      )}
    </div>
  )
}
