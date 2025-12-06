"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { SearchInput } from "@/components/search-input"
import { VhsDivider } from "@/components/vhs-divider"
import { FlowProgress } from "@/components/flow-progress"
import { Button } from "@/components/ui/button"
import { useFlow } from "@/lib/flow-context"
import { genreTree, dummyTopChannels } from "@/lib/dummy-data"
import type { GenreNode as GenreNodeType } from "@/lib/dummy-data"
import { GenreWheel } from "@/components/genre-wheel"
import { ChannelIcon } from "@/components/channel-icon"

export default function ExplorePage() {
  const router = useRouter()
  const { flow, updateFlow } = useFlow()
  const [localSearch, setLocalSearch] = useState(flow.searchQuery)

  const handleGenreSelect = (node: GenreNodeType, path: GenreNodeType[]) => {
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
            {dummyTopChannels.map((channel, index) => (
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
            ))}
          </div>

          <p className="text-center text-base text-[#6B5B55] font-['Zilla_Slab',serif] mt-6">
            We saw what you liked and we think this describes you:
          </p>
        </div>

        <div className="bg-[#FFF9F0] rounded-2xl p-8 shadow-lg mb-8 min-h-[700px] flex items-center justify-center">
          <GenreWheel genres={genreTree} onSelect={handleGenreSelect} />
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
