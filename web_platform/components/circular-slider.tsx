"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"

interface CircularSliderProps {
  label: string
  leftLabel: string
  rightLabel: string
  description: string
  value: number
  onChange: (value: number) => void
}

export function CircularSlider({ label, leftLabel, rightLabel, description, value, onChange }: CircularSliderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const trackRef = useRef<HTMLDivElement>(null)

  const handleMove = (clientX: number) => {
    if (!trackRef.current) return

    const rect = trackRef.current.getBoundingClientRect()
    const x = clientX - rect.left
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100))
    onChange(Math.round(percentage))
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    handleMove(e.clientX)
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      handleMove(e.clientX)
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      window.addEventListener("mousemove", handleMouseMove)
      window.addEventListener("mouseup", handleMouseUp)
      return () => {
        window.removeEventListener("mousemove", handleMouseMove)
        window.removeEventListener("mouseup", handleMouseUp)
      }
    }
  }, [isDragging])

  return (
    <div className="space-y-3 select-none">
      <div className="text-sm font-semibold text-[#3E2723] font-['Zilla_Slab',serif]">{label}</div>

      <div className="relative pt-8 pb-6">
        {/* Track */}
        <div
          ref={trackRef}
          className="relative h-1 bg-[#D4C5B9] rounded-full cursor-pointer"
          onMouseDown={handleMouseDown}
        >
          {/* Progress fill */}
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#E76F51] to-[#D4A574] rounded-full"
            style={{ width: `${value}%` }}
          />

          {/* Draggable knob */}
          <motion.div
            className="absolute top-1/2 -translate-y-1/2 cursor-grab active:cursor-grabbing"
            style={{ left: `${value}%` }}
            animate={{ scale: isDragging ? 1.2 : 1 }}
            transition={{ duration: 0.15 }}
          >
            <div className="relative -translate-x-1/2">
              {/* Outer glow */}
              <div className="absolute inset-0 w-8 h-8 bg-[#E76F51] rounded-full blur-md opacity-50" />

              {/* Knob circle */}
              <div className="relative w-8 h-8 bg-[#E76F51] border-3 border-white shadow-lg rounded-full flex items-center justify-center">
                {/* Inner highlight */}
                <div className="w-3 h-3 bg-white rounded-full opacity-60" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Labels */}
        <div className="flex justify-between mt-2 text-xs text-[#6B5B55]">
          <span>{leftLabel}</span>
          <span>{rightLabel}</span>
        </div>
      </div>

      <p className="text-xs text-[#6B5B55] text-center">{description}</p>
    </div>
  )
}
