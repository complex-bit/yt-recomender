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
    min_duration: number
    max_duration: number
    popularity: number
    recency: number
    uniqueness: number
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
      min_duration: 0,
      max_duration: 3600,
      popularity: 50,
      recency: 50,
      uniqueness: 50,
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
    filters.min_duration > 0 ||
    filters.max_duration < 3600 ||
    filters.popularity !== 50 ||
    filters.recency !== 50 ||
    filters.uniqueness !== 50 ||
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

        {/* Duration */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">Duration</Label>
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-[#6B5B55]">
              <span>Short</span>
              <span>Long</span>
            </div>
            <Slider
              value={[filters.max_duration]}
              onValueChange={([value]) => updateFilter('max_duration', value)}
              min={300}
              max={3600}
              step={300}
              className="w-full"
            />
            <div className="text-center text-xs text-[#6B5B55] transition-all duration-200 ease-in-out">
              Up to {filters.max_duration >= 3600 ? '1h+' : formatDuration(filters.max_duration)}
            </div>
          </div>
          {filters.max_duration < 3600 && (
            <Badge
              variant="secondary"
              className="gap-1 cursor-pointer"
              onClick={() => updateFilter('max_duration', 3600)}
            >
              Up to {formatDuration(filters.max_duration)}
              <X className="h-3 w-3" />
            </Badge>
          )}
        </div>

        {/* Popularity Slider */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">Popularity</Label>
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-[#6B5B55]">
              <span>Hidden Gems</span>
              <span>Popular Hits</span>
            </div>
            <Slider
              value={[filters.popularity]}
              onValueChange={([value]) => updateFilter('popularity', value)}
              max={100}
              step={1}
              className="w-full"
            />
            <div className="text-center text-xs text-[#6B5B55] transition-all duration-200 ease-in-out">
              {filters.popularity < 30 ? 'Hidden Gems' :
               filters.popularity > 70 ? 'Popular Hits' : 'Mixed Popularity'}
            </div>
          </div>
        </div>

        {/* Recency Slider */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">Recency</Label>
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-[#6B5B55]">
              <span>Classic</span>
              <span>Fresh</span>
            </div>
            <Slider
              value={[filters.recency]}
              onValueChange={([value]) => updateFilter('recency', value)}
              max={100}
              step={1}
              className="w-full"
            />
            <div className="text-center text-xs text-[#6B5B55] transition-all duration-200 ease-in-out">
              {filters.recency < 30 ? 'Classic Videos' :
               filters.recency > 70 ? 'Fresh Content' : 'Mixed Ages'}
            </div>
          </div>
        </div>

        {/* Uniqueness Slider */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">Channel Discovery</Label>
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-[#6B5B55]">
              <span>Familiar</span>
              <span>New Channels</span>
            </div>
            <Slider
              value={[filters.uniqueness]}
              onValueChange={([value]) => updateFilter('uniqueness', value)}
              max={100}
              step={1}
              className="w-full"
            />
            <div className="text-center text-xs text-[#6B5B55] transition-all duration-200 ease-in-out">
              {filters.uniqueness < 30 ? 'Your Channels' :
               filters.uniqueness > 70 ? 'New Channels' : 'Mixed Discovery'}
            </div>
          </div>
        </div>


        {/* Quick Filters */}
        <div className="space-y-3 border-t pt-4">
          <Label className="text-sm font-medium">Quick Filters</Label>
          <div className="grid grid-cols-1 gap-2">
            <Button
              variant="outline"
              size="sm"
              className="justify-start h-8 text-xs"
              onClick={() => {
                updateFilter('max_duration', 900) // 15 minutes
                updateFilter('popularity', 70) // Popular content
              }}
            >
              Quick & Popular
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="justify-start h-8 text-xs"
              onClick={() => {
                updateFilter('max_duration', 3600) // Long form
                updateFilter('popularity', 30) // Hidden gems
              }}
            >
              Long & Hidden
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="justify-start h-8 text-xs"
              onClick={() => {
                updateFilter('recency', 70) // Fresh content
                updateFilter('uniqueness', 70) // New discovery
              }}
            >
              Fresh & New
            </Button>
          </div>
        </div>

        {/* Current Filters Summary */}
        {hasActiveFilters && (
          <div className="border-t pt-4">
            <Label className="text-sm font-medium mb-2 block">Active Filters</Label>
            <div className="text-xs text-[#6B5B55] space-y-1">
              {filters.max_duration < 3600 && (
                <div>• Duration: Up to {formatDuration(filters.max_duration)}</div>
              )}
              {filters.popularity !== 50 && (
                <div>• Popularity: {filters.popularity < 30 ? 'Hidden gems' : filters.popularity > 70 ? 'Popular hits' : 'Mixed'}</div>
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