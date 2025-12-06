"use client"

import { useRouter } from "next/navigation"
import { useState, useEffect } from "react"
import { SearchInput } from "@/components/search-input"
import { VhsDivider } from "@/components/vhs-divider"
import { FlowProgress } from "@/components/flow-progress"
import { Button } from "@/components/ui/button"
import { useFlow } from "@/lib/flow-context"
import { GenreWheel } from "@/components/genre-wheel"
import { ChannelIcon } from "@/components/channel-icon"
import { getUserProfile, type TopChannel, type GenreTreeNode } from "@/lib/api"

export default function ExplorePage() {
  const router = useRouter()
  const { flow, updateFlow } = useFlow()
  const [localSearch, setLocalSearch] = useState(flow.searchQuery)
  const [topChannels, setTopChannels] = useState<TopChannel[]>([])
  const [genreTree, setGenreTree] = useState<GenreTreeNode[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const profile = await getUserProfile()
        setTopChannels(profile.topChannels)
        setGenreTree(profile.genreTree)
      } catch (err) {
        setError('Failed to load profile data')
        console.error('Profile load error:', err)
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [])

  const handleGenreSelect = (node: GenreTreeNode, path: GenreTreeNode[]) => {
    updateFlow({ selectedGenrePath: path })
    router.push("/flow/results")
  }

  const handleSearch = (query: string) => {
    updateFlow({ searchQuery: query })
    router.push("/flow/results")
  }

  const scatteredPositions = [
    { left: "8%", top: "15%" },
    { left: "18%", top: "8%" },
    { left: "28%", top: "18%" },
    { left: "72%", top: "10%" },
    { left: "82%", top: "20%" },
  ]

  return (
    <>
      <FlowProgress currentStep={1} />

      <section>
        <div className="mb-12">
          <h2 className="font-['Zilla_Slab',serif] text-4xl font-bold text-[#3E2723] mb-6 text-center">
            What do you want to explore?
          </h2>

          <div className="relative h-40 mt-8">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-[#6B5B55]">Loading your top channels...</div>
              </div>
            ) : error ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-red-500">{error}</div>
              </div>
            ) : (
              topChannels.map((channel, index) => (
                <div
                  key={channel.channelId}
                  className="absolute"
                  style={{
                    left: scatteredPositions[index]?.left || "50%",
                    top: scatteredPositions[index]?.top || "50%",
                  }}
                >
                  <ChannelIcon channel={channel} delay={index * 0.1} />
                </div>
              ))
            )}
          </div>

          <p className="text-center text-base text-[#6B5B55] font-['Zilla_Slab',serif] mt-6">
            We saw what you liked and we think this describes you:
          </p>
        </div>

        <div className="bg-[#FFF9F0] rounded-2xl p-8 shadow-lg mb-8 min-h-[700px] flex items-center justify-center">
          {loading ? (
            <div className="text-[#6B5B55]">Loading your personalized genre tree...</div>
          ) : error ? (
            <div className="text-red-500">{error}</div>
          ) : (
            <GenreWheel genres={genreTree} onSelect={handleGenreSelect} />
          )}
        </div>

        <VhsDivider text="OR" />

        <SearchInput
          placeholder="Describe what you want (e.g., 'I want underwater videos')"
          onSearch={handleSearch}
          value={localSearch}
          onChange={setLocalSearch}
        />

        <div className="flex justify-center mt-8">
          <Button onClick={() => router.push("/")} variant="ghost" className="text-[#6B5B55] hover:text-[#3E2723]">
            ← Back
          </Button>
        </div>
      </section>
    </>
  )
}
