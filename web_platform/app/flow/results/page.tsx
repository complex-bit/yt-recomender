"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { VideoCard } from "@/components/video-card"
import { SearchInput } from "@/components/search-input"
import { CircularSlider } from "@/components/circular-slider"
import { FlowProgress } from "@/components/flow-progress"
import { Button } from "@/components/ui/button"
import { useFlow } from "@/lib/flow-context"
import { dummyWatchHistory } from "@/lib/dummy-data"
import { RotateCcw, Sparkles } from "lucide-react"

export default function ResultsPage() {
  const router = useRouter()
  const { flow, updateFlow, resetFlow } = useFlow()
  const [isRegenerating, setIsRegenerating] = useState(false)

  const [lengthValue, setLengthValue] = useState(flow.refinementValues.length[0] || 50)
  const [popularityValue, setPopularityValue] = useState(flow.refinementValues.popularity[0] || 50)
  const [recencyValue, setRecencyValue] = useState(flow.refinementValues.recency[0] || 50)

  const handleThumbsFeedback = (videoId: string, feedback: "up" | "down") => {
    updateFlow({
      videoFeedback: {
        ...flow.videoFeedback,
        [videoId]: feedback,
      },
    })
  }

  const handleRegenerate = () => {
    updateFlow({
      refinementValues: {
        length: [lengthValue],
        popularity: [popularityValue],
        recency: [recencyValue],
      },
    })
    setIsRegenerating(true)
    setTimeout(() => setIsRegenerating(false), 800)
  }

  const handleRefineSearch = (query: string) => {
    updateFlow({ searchQuery: query })
    handleRegenerate()
  }

  const handleStartOver = () => {
    resetFlow()
    router.push("/")
  }

  const breadcrumb =
    flow.selectedGenrePath.length > 0
      ? flow.selectedGenrePath.map((node) => node.name).join(" → ")
      : flow.searchQuery
        ? `Search: "${flow.searchQuery}"`
        : "All Videos"

  return (
    <>
      <FlowProgress currentStep={2} />

      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-8">
        {/* Left Sidebar - "Not Quite Right" Controls */}
        <aside className="lg:sticky lg:top-6 lg:self-start">
          <div className="bg-[#FFF9F0] rounded-2xl p-6 shadow-lg border-2 border-[#D4C5B9]">
            <div className="mb-6">
              <h3 className="font-['Zilla_Slab',serif] text-xl font-bold text-[#3E2723] mb-2">Not quite right?</h3>
              <p className="text-sm text-[#6B5B55]">Adjust the dials to refine your results</p>
            </div>

            <div className="space-y-8">
              <CircularSlider
                label="Video Length"
                leftLabel="Short"
                rightLabel="Long"
                description="<5 min ↔ 20+ min"
                value={lengthValue}
                onChange={setLengthValue}
              />

              <CircularSlider
                label="Popularity"
                leftLabel="Hidden gems"
                rightLabel="Popular hits"
                description="Under 1K views ↔ Millions of views"
                value={popularityValue}
                onChange={setPopularityValue}
              />

              <CircularSlider
                label="Recency"
                leftLabel="Classic"
                rightLabel="Fresh"
                description="Older videos ↔ Latest uploads"
                value={recencyValue}
                onChange={setRecencyValue}
              />
            </div>

            <Button
              onClick={handleRegenerate}
              className="w-full mt-6 bg-[#E76F51] hover:bg-[#d65a3a] text-white rounded-lg font-semibold py-3"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Regenerate Videos
            </Button>

            <div className="mt-6 pt-6 border-t border-[#D4C5B9]">
              <SearchInput
                placeholder="Or ask anything..."
                onSearch={handleRefineSearch}
                buttonText="Go →"
                value={flow.searchQuery}
                onChange={(value) => updateFlow({ searchQuery: value })}
              />
            </div>
          </div>
        </aside>

        {/* Right Side - Video Results */}
        <section>
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="text-sm text-[#6B5B55] mb-1 font-['Zilla_Slab',serif]">{breadcrumb}</div>
              <p className="text-[#3E2723] text-lg">
                Found <span className="font-bold text-[#E76F51]">{dummyWatchHistory.length}</span> videos matching your
                vibe
              </p>
            </div>
            <Button onClick={handleStartOver} variant="ghost" size="sm" className="text-[#6B5B55] hover:text-[#3E2723]">
              <RotateCcw className="h-4 w-4 mr-2" />
              Start Over
            </Button>
          </div>

          {/* Video Grid */}
          <div
            className={`grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 transition-opacity duration-300 ${
              isRegenerating ? "opacity-50" : "opacity-100"
            }`}
          >
            {dummyWatchHistory.map((video) => (
              <VideoCard
                key={video.videoId}
                video={video}
                onThumbsUp={() => handleThumbsFeedback(video.videoId, "up")}
                onThumbsDown={() => handleThumbsFeedback(video.videoId, "down")}
              />
            ))}
          </div>

          {/* Load More */}
          <div className="text-center mb-8">
            <Button
              variant="outline"
              className="border-2 border-[#E76F51] text-[#E76F51] hover:bg-[#E76F51] hover:text-white rounded-full px-8 py-3 font-semibold bg-transparent"
            >
              Load more...
            </Button>
          </div>

          {/* Back Button */}
          <div className="flex justify-center mt-8">
            <Button
              onClick={() => router.push("/flow/explore")}
              variant="ghost"
              className="text-[#6B5B55] hover:text-[#3E2723]"
            >
              ← Back to Explore
            </Button>
          </div>
        </section>
      </div>
    </>
  )
}
