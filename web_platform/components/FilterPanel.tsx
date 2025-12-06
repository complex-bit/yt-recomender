"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Slider } from '@/components/ui/slider'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { X, Filter } from 'lucide-react'

interface FilterPanelProps {
  filters: {
    educational_level: string
    min_duration: number
    max_duration: number
    channels: string[]
  }
  onChange: (filters: any) => void
  analytics: {
    top_channels: Record<string, number>
    top_genres: Record<string, Record<string, number>>
  } | null
}

export function FilterPanel({ filters, onChange, analytics }: FilterPanelProps) {
  const updateFilter = (key: string, value: any) => {
    onChange({ ...filters, [key]: value })
  }

  const toggleChannel = (channel: string) => {
    const channels = filters.channels.includes(channel)
      ? filters.channels.filter(c => c !== channel)
      : [...filters.channels, channel]
    updateFilter('channels', channels)
  }

  const clearFilters = () => {
    onChange({
      educational_level: '',
      min_duration: 0,
      max_duration: 3600,
      channels: []
    })
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    if (mins >= 60) {
      const hours = Math.floor(mins / 60)
      const remainingMins = mins % 60
      return `${hours}h ${remainingMins}m`
    }
    return `${mins}m`
  }

  const hasActiveFilters =
    filters.educational_level ||
    filters.min_duration > 0 ||
    filters.max_duration < 3600 ||
    filters.channels.length > 0

  return (
    <Card className="bg-white border-[#E0E0E0] sticky top-6">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="h-8 px-2 text-xs"
            >
              Clear all
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Educational Level */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">Educational Level</Label>
          <Select
            value={filters.educational_level || 'any'}
            onValueChange={(value) => updateFilter('educational_level', value === 'any' ? '' : value)}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Any level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="any">Any level</SelectItem>
              <SelectItem value="Beginner">Beginner</SelectItem>
              <SelectItem value="Intermediate">Intermediate</SelectItem>
              <SelectItem value="Advanced">Advanced</SelectItem>
              <SelectItem value="Academic">Academic</SelectItem>
            </SelectContent>
          </Select>
          {filters.educational_level && filters.educational_level !== 'any' && (
            <Badge
              variant="secondary"
              className="gap-1 cursor-pointer"
              onClick={() => updateFilter('educational_level', '')}
            >
              {filters.educational_level}
              <X className="h-3 w-3" />
            </Badge>
          )}
        </div>

        {/* Duration */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">Duration</Label>

          <div className="space-y-4">
            <div>
              <Label className="text-xs text-[#6B5B55]">Minimum</Label>
              <Slider
                value={[filters.min_duration]}
                onValueChange={([value]) => updateFilter('min_duration', value)}
                max={3600}
                step={300}
                className="w-full"
              />
              <div className="text-xs text-[#6B5B55] mt-1">
                {formatDuration(filters.min_duration)}
              </div>
            </div>

            <div>
              <Label className="text-xs text-[#6B5B55]">Maximum</Label>
              <Slider
                value={[filters.max_duration]}
                onValueChange={([value]) => updateFilter('max_duration', value)}
                min={300}
                max={3600}
                step={300}
                className="w-full"
              />
              <div className="text-xs text-[#6B5B55] mt-1">
                {filters.max_duration >= 3600 ? '1h+' : formatDuration(filters.max_duration)}
              </div>
            </div>
          </div>

          {(filters.min_duration > 0 || filters.max_duration < 3600) && (
            <Badge
              variant="secondary"
              className="gap-1 cursor-pointer"
              onClick={() => {
                updateFilter('min_duration', 0)
                updateFilter('max_duration', 3600)
              }}
            >
              {formatDuration(filters.min_duration)} - {
                filters.max_duration >= 3600 ? '1h+' : formatDuration(filters.max_duration)
              }
              <X className="h-3 w-3" />
            </Badge>
          )}
        </div>

        {/* Preferred Channels */}
        {analytics?.top_channels && Object.keys(analytics.top_channels).length > 0 && (
          <div className="space-y-3">
            <Label className="text-sm font-medium">Your Channels</Label>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {Object.entries(analytics.top_channels).map(([channel, score]) => (
                <div
                  key={channel}
                  className="flex items-center space-x-2 cursor-pointer"
                  onClick={() => toggleChannel(channel)}
                >
                  <Checkbox
                    checked={filters.channels.includes(channel)}
                    onChange={() => toggleChannel(channel)}
                  />
                  <div className="flex-1 min-w-0">
                    <Label className="text-sm cursor-pointer truncate block">
                      {channel}
                    </Label>
                    <div className="text-xs text-[#6B5B55]">
                      {Math.round(score * 100)}% preference
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {filters.channels.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {filters.channels.map((channel) => (
                  <Badge
                    key={channel}
                    variant="secondary"
                    className="gap-1 cursor-pointer max-w-full truncate"
                    onClick={() => toggleChannel(channel)}
                  >
                    <span className="truncate max-w-20">{channel}</span>
                    <X className="h-3 w-3 flex-shrink-0" />
                  </Badge>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Quick Filters */}
        <div className="space-y-3 border-t pt-4">
          <Label className="text-sm font-medium">Quick Filters</Label>
          <div className="grid grid-cols-1 gap-2">
            <Button
              variant="outline"
              size="sm"
              className="justify-start h-8 text-xs"
              onClick={() => {
                updateFilter('educational_level', 'Beginner')
                updateFilter('max_duration', 900) // 15 minutes
              }}
            >
              🌱 Quick & Easy
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="justify-start h-8 text-xs"
              onClick={() => {
                updateFilter('educational_level', 'Advanced')
                updateFilter('min_duration', 1200) // 20 minutes
              }}
            >
              🧠 Deep Dive
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="justify-start h-8 text-xs"
              onClick={() => {
                if (analytics?.top_channels) {
                  const topChannel = Object.keys(analytics.top_channels)[0]
                  if (topChannel) updateFilter('channels', [topChannel])
                }
              }}
            >
              ❤️ Favorites Only
            </Button>
          </div>
        </div>

        {/* Current Filters Summary */}
        {hasActiveFilters && (
          <div className="border-t pt-4">
            <Label className="text-sm font-medium mb-2 block">Active Filters</Label>
            <div className="text-xs text-[#6B5B55] space-y-1">
              {filters.educational_level && (
                <div>• Level: {filters.educational_level}</div>
              )}
              {(filters.min_duration > 0 || filters.max_duration < 3600) && (
                <div>• Duration: {formatDuration(filters.min_duration)} - {
                  filters.max_duration >= 3600 ? '1h+' : formatDuration(filters.max_duration)
                }</div>
              )}
              {filters.channels.length > 0 && (
                <div>• Channels: {filters.channels.length} selected</div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}