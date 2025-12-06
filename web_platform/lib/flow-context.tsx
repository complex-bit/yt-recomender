"use client"

import { createContext, useContext, useState, type ReactNode } from "react"
import type { GenreNode } from "./dummy-data"
import type { SemanticSearchResponse, GenreTreeNode } from "./api"

interface ExplorationFlow {
  // Step 1: Channel selection
  acceptedChannels: boolean | null

  // Step 2: Genre/Search selection
  selectedGenrePath: GenreNode[] | GenreTreeNode[]
  searchQuery: string
  semanticSearchResults?: SemanticSearchResponse
  searchType?: 'semantic' | 'simple' | 'genre'
  chatHistory?: any[]

  // Step 3: Video refinement
  refinementValues: {
    length: number[]
    popularity: number[]
    recency: number[]
  }
  videoFeedback: Record<string, "up" | "down">
}

interface FlowContextType {
  flow: ExplorationFlow
  updateFlow: (updates: Partial<ExplorationFlow>) => void
  resetFlow: () => void
}

const FlowContext = createContext<FlowContextType | undefined>(undefined)

const initialFlow: ExplorationFlow = {
  acceptedChannels: null,
  selectedGenrePath: [],
  searchQuery: "",
  refinementValues: {
    length: [0, 100],
    popularity: [0, 100],
    recency: [0, 100],
  },
  videoFeedback: {},
}

export function FlowProvider({ children }: { children: ReactNode }) {
  const [flow, setFlow] = useState<ExplorationFlow>(initialFlow)

  const updateFlow = (updates: Partial<ExplorationFlow>) => {
    setFlow((prev) => ({ ...prev, ...updates }))
  }

  const resetFlow = () => {
    setFlow(initialFlow)
  }

  return <FlowContext.Provider value={{ flow, updateFlow, resetFlow }}>{children}</FlowContext.Provider>
}

export function useFlow() {
  const context = useContext(FlowContext)
  if (!context) {
    throw new Error("useFlow must be used within a FlowProvider")
  }
  return context
}
