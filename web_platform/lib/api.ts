const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

export interface GenreTreeNode {
  id: string
  name: string
  percentage?: number
  children?: GenreTreeNode[]
  count?: number
}

export interface UserProfile {
  topChannels: TopChannel[]
  genrePercentages: Record<string, number>
  genreTree: GenreTreeNode[]
  totalVideos: number
}

export interface TopChannel {
  channelId: string
  channelTitle: string
  channelAvatar?: string
  watchCount: number
  category: string
}

export interface SearchParams {
  query?: string
  genrePath?: Array<{ id: string; name: string }>
  refinements?: {
    length?: number
    popularity?: number
    recency?: number
  }
}

export interface SearchResponse {
  videos: WatchHistoryItem[]
  total: number
  query?: string
  genrePath?: Array<{ id: string; name: string }>
}

export interface SemanticSearchParams {
  query: string
  genrePath?: GenreTreeNode[]
  chatHistory?: Array<{
    id: string
    type: 'user' | 'system'
    content: string
    timestamp: Date
    genrePath?: GenreTreeNode[]
  }>
  limit?: number
}

export interface SemanticSearchResponse {
  videos: (WatchHistoryItem & {
    similarity_score?: number
    match_reasons?: string[]
  })[]
  total: number
  query: string
  search_type: 'semantic' | 'keyword'
  genre_context?: string
}

export interface WatchHistoryItem {
  videoId: string
  title: string
  description: string
  channelId: string
  channelTitle: string
  channelAvatar?: string
  published_at: string
  duration: number
  view_count: number
  like_count: number
  comment_count: number
  thumbnail: string
  tags: string[]
  categories: string[]
  scraped_at: string
}

export async function getUserProfile(forceNew: boolean = false): Promise<UserProfile> {
  try {
    const url = `${API_BASE}/api/profile${forceNew ? '?force_new=true' : ''}`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching user profile:', error)
    throw error
  }
}

export async function searchVideos(params: SearchParams): Promise<SearchResponse> {
  try {
    const response = await fetch(`${API_BASE}/api/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Error searching videos:', error)
    throw error
  }
}

export async function submitVideoFeedback(videoId: string, feedback: 'up' | 'down'): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/api/videos/${videoId}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ feedback }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
  } catch (error) {
    console.error('Error submitting video feedback:', error)
    throw error
  }
}

export async function semanticSearch(params: SemanticSearchParams): Promise<SemanticSearchResponse> {
  try {
    const response = await fetch(`${API_BASE}/api/semantic-search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: params.query,
        genrePath: params.genrePath?.map(node => ({ id: node.id, name: node.name })),
        chatHistory: params.chatHistory?.map(msg => ({
          ...msg,
          timestamp: msg.timestamp.toISOString()
        })),
        limit: params.limit || 20
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Error performing semantic search:', error)
    throw error
  }
}

export async function checkApiHealth(): Promise<{ status: string; videos_loaded: number }> {
  try {
    const response = await fetch(`${API_BASE}/health`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Error checking API health:', error)
    throw error
  }
}