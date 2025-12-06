// Dummy data based on the provided JSON structure

export interface WatchHistoryItem {
  videoId: string
  title: string
  channelId: string
  channelTitle: string
  watchedAt: string
  duration: number
  category: string
  tags: string[]
  thumbnail: string
}

export interface TopChannel {
  channelId: string
  channelTitle: string
  watchCount: number
  category: string
}

export interface GenreNode {
  id: string
  name: string
  percentage?: number
  children?: GenreNode[]
}

export const dummyTopChannels: TopChannel[] = [
  {
    channelId: "UCwmZiChSryoWQCZMIQezgTg",
    channelTitle: "BBC Earth",
    watchCount: 45,
    category: "Documentary",
  },
  {
    channelId: "UCHnyfMqiRRG1u-2MsSQLbXA",
    channelTitle: "Veritasium",
    watchCount: 38,
    category: "Science & Technology",
  },
  {
    channelId: "UCsooa4yRKGN_zEE8iknghZA",
    channelTitle: "TED-Ed",
    watchCount: 32,
    category: "Education",
  },
  {
    channelId: "UCX6OQ3DkcsbYNE6H8uQQuVA",
    channelTitle: "MrBeast",
    watchCount: 28,
    category: "Entertainment",
  },
  {
    channelId: "UC1DTYW241WD64ah5BFWn4JA",
    channelTitle: "Kurzgesagt",
    watchCount: 25,
    category: "Science & Technology",
  },
]

export const dummyWatchHistory: WatchHistoryItem[] = [
  {
    videoId: "dQw4w9WgXcQ",
    title: "The Secret Life of Plankton",
    channelId: "UCwmZiChSryoWQCZMIQezgTg",
    channelTitle: "BBC Earth",
    watchedAt: "2024-03-15T14:23:45Z",
    duration: 934,
    category: "Science & Technology",
    tags: ["nature", "documentary", "ocean", "plankton"],
    thumbnail: "/plankton-underwater.jpg",
  },
  {
    videoId: "abc123def45",
    title: "How Quantum Computers Break Encryption",
    channelId: "UCHnyfMqiRRG1u-2MsSQLbXA",
    channelTitle: "Veritasium",
    watchedAt: "2024-03-14T09:12:33Z",
    duration: 1245,
    category: "Science & Technology",
    tags: ["quantum", "encryption", "technology", "science"],
    thumbnail: "/quantum-computer.jpg",
  },
  {
    videoId: "xyz789ghi01",
    title: "The Evolution of Camera Technology",
    channelId: "UCsooa4yRKGN_zEE8iknghZA",
    channelTitle: "TED-Ed",
    watchedAt: "2024-03-13T18:45:22Z",
    duration: 678,
    category: "Education",
    tags: ["camera", "technology", "history", "photography"],
    thumbnail: "/vintage-camera.png",
  },
  {
    videoId: "mno456pqr78",
    title: "Exploring the Deep Ocean",
    channelId: "UCwmZiChSryoWQCZMIQezgTg",
    channelTitle: "BBC Earth",
    watchedAt: "2024-03-12T21:12:33Z",
    duration: 1567,
    category: "Documentary",
    tags: ["ocean", "nature", "underwater", "exploration"],
    thumbnail: "/deep-ocean-exploration.jpg",
  },
  {
    videoId: "stu901vwx23",
    title: "What If Everyone Jumped At Once?",
    channelId: "UC1DTYW241WD64ah5BFWn4JA",
    channelTitle: "Kurzgesagt",
    watchedAt: "2024-03-11T15:30:45Z",
    duration: 445,
    category: "Science & Technology",
    tags: ["physics", "science", "animation", "educational"],
    thumbnail: "/earth-from-space.png",
  },
]

export const genreTree: GenreNode[] = [
  {
    id: "documentary",
    name: "Documentary",
    percentage: 35,
    children: [
      {
        id: "nature",
        name: "Nature",
        children: [
          { id: "wildlife", name: "Wildlife" },
          { id: "ocean", name: "Ocean/Underwater" },
          { id: "forests", name: "Forests" },
          { id: "space", name: "Space" },
        ],
      },
      {
        id: "science",
        name: "Science",
        children: [
          { id: "physics", name: "Physics" },
          { id: "biology", name: "Biology" },
          { id: "technology", name: "Technology" },
        ],
      },
      {
        id: "history",
        name: "History",
        children: [
          { id: "ancient", name: "Ancient" },
          { id: "modern", name: "Modern" },
          { id: "war", name: "War" },
        ],
      },
      { id: "true-crime", name: "True Crime" },
      { id: "art-culture", name: "Art & Culture" },
    ],
  },
  {
    id: "gaming",
    name: "Gaming",
    percentage: 25,
    children: [
      { id: "lets-plays", name: "Let's Plays" },
      { id: "speedruns", name: "Speedruns" },
      { id: "reviews", name: "Reviews" },
      { id: "walkthroughs", name: "Walkthroughs" },
    ],
  },
  {
    id: "tech",
    name: "Tech",
    percentage: 20,
    children: [
      { id: "tech-reviews", name: "Reviews" },
      { id: "tutorials", name: "Tutorials" },
      { id: "tech-news", name: "News" },
      { id: "builds", name: "Builds" },
    ],
  },
  {
    id: "education",
    name: "Education",
    percentage: 15,
    children: [
      { id: "math", name: "Math" },
      { id: "languages", name: "Languages" },
      { id: "philosophy", name: "Philosophy" },
    ],
  },
  {
    id: "entertainment",
    name: "Entertainment",
    percentage: 5,
    children: [
      { id: "comedy", name: "Comedy" },
      { id: "vlogs", name: "Vlogs" },
      { id: "music", name: "Music" },
    ],
  },
]

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60

  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return `${hours}:${remainingMinutes.toString().padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`
  }

  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`
}
