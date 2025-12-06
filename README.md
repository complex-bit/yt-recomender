# WhyExplore - YouTube Discovery App

**WhyExplore** is a vintage cinema-themed YouTube discovery app that helps users find new content based on their viewing history. It moves beyond algorithmic recommendations by combining personalized taste analysis with interactive, intentional exploration.

## ✨ Features

### 🎯 **Interactive Genre Wheel**
- **3-Level Hierarchy**: Navigate through main genres → sub-genres → specific topics
- **Visual Design**: Vintage camera dial aesthetic with smooth animations
- **Personalized Categories**: Generated from your actual YouTube watch history
- **Dynamic Selection**: Click to expand genres or select at any level

### 🎭 **Vintage Cinema Aesthetic**
- **Color Palette**: Terracotta (`#C4704F`), forest green (`#4A6741`), goldenrod (`#D4A574`)
- **Typography**: Slab serif headings (Bitter) + clean sans-serif body (Inter)
- **UI Elements**: Film projector inspired design with VHS-style dividers

### 🔍 **Smart Discovery**
- **Natural Language Search**: "ocean videos", "calm music", "space documentaries"
- **Semantic Search**: AI-powered understanding of your intent
- **Refinement Controls**: Length, popularity, and comfort/adventure dials
- **Channel Analysis**: Top channels from your history with scattered display

### 🎨 **User Profile Integration**
- **Watch History Analysis**: Processes your YouTube data (JSON format)
- **Genre Percentages**: Shows distribution of your viewing preferences
- **Top Channels**: Displays your most-watched creators
- **Personalized Tree**: Genre hierarchy based on your actual content

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/get-started) and Docker Compose
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd yt-recomender
```

### 2. Prepare Your Data
The app uses a populated database with YouTube videos and your watch history:

- **Database**: `data/youtube_videos.db` (contains ~1,800 videos with genre classifications)
- **Watch History**: `youtube_watch_history.json` (your personal viewing data)

### 3. Run with Docker
```bash
# Start all services
docker-compose up -d

# Check status
docker ps

# View logs (optional)
docker-compose logs -f
```

### 4. Access the Application
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:5000](http://localhost:5000)
- **Health Check**: [http://localhost:5000/health](http://localhost:5000/health)

### 5. Stop the Application
```bash
# Graceful shutdown
docker-compose down

# Remove all containers and data
docker-compose down -v
```

## 🏗️ Architecture

### **Frontend (Next.js)**
- **Location**: `web_platform/`
- **Port**: 3000
- **Features**: React components, Framer Motion animations, responsive design
- **Key Components**:
  - `GenreWheel`: Interactive genre selection
  - `SemanticSearchChat`: AI-powered search interface
  - `FlowProgress`: Multi-step navigation

### **Backend (Flask)**
- **Location**: `backend/`
- **Port**: 5000
- **Features**: REST API, genre analysis, recommendation engine
- **Key Endpoints**:
  - `GET /api/profile` - User taste profile
  - `POST /api/search` - Video search with filters
  - `POST /api/semantic-search` - AI-powered search

### **Database (SQLite)**
- **Location**: `data/youtube_videos.db`
- **Tables**: `videos`, `video_genres`, `channels`, `genre_hierarchy`
- **Content**: 1,800+ YouTube videos with metadata and classifications

## 🔧 Development

### Local Development (without Docker)

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### Frontend Setup
```bash
cd web_platform
npm install
npm run dev
```

### File Structure
```
yt-recomender/
├── backend/                 # Flask API server
│   ├── app.py              # Main application
│   ├── recommendation_engine.py
│   ├── requirements.txt
│   └── Dockerfile
├── web_platform/           # Next.js frontend
│   ├── app/                # App router pages
│   ├── components/         # React components
│   ├── lib/               # Utilities and API calls
│   ├── package.json
│   └── Dockerfile
├── data/
│   └── youtube_videos.db  # SQLite database
├── youtube_watch_history.json  # User data
├── docker-compose.yml
└── README.md
```

## 📊 Data Format

### Watch History JSON Structure
```json
{
  "user_profile": {
    "interests": ["science", "technology", "education"],
    "preferred_channels": ["Veritasium", "Marques Brownlee"]
  },
  "watch_history": [
    {
      "video_id": "6akmv1bsz1M",
      "title": "Something Strange Happens When You Follow Einstein's Math",
      "channel": "Veritasium",
      "watched_at": "2025-12-05T16:42:33.456Z",
      "watch_time_seconds": 1632,
      "tags": ["veritasium", "science", "physics"]
    }
  ]
}
```

### Genre Tree API Response
```json
{
  "genreTree": [
    {
      "id": "education",
      "name": "Education",
      "percentage": 33,
      "level": 1,
      "children": [
        {
          "id": "education_science",
          "name": "Science",
          "level": 2,
          "children": [
            {"id": "physics", "name": "Physics", "level": 3},
            {"id": "chemistry", "name": "Chemistry", "level": 3}
          ]
        }
      ]
    }
  ]
}
```

## 🔍 API Endpoints

### User Profile
```bash
GET /api/profile?force_new=true
```
Returns user's personalized genre tree, top channels, and viewing statistics.

### Video Search
```bash
POST /api/search
Content-Type: application/json

{
  "query": "ocean videos",
  "genrePath": [{"id": "education", "name": "Education"}],
  "refinements": {
    "length": 50,
    "popularity": 75,
    "recency": 25
  }
}
```

### Semantic Search
```bash
POST /api/semantic-search
Content-Type: application/json

{
  "query": "videos about space exploration",
  "genrePath": [...],
  "limit": 20
}
```

## 🎨 Customization

### Color Scheme
The app uses a vintage cinema palette defined in `web_platform/app/globals.css`:
- **Primary**: `#C4704F` (Terracotta)
- **Secondary**: `#4A6741` (Forest Green)
- **Accent**: `#D4A574` (Goldenrod)
- **Text**: `#3E2723` (Dark Brown)

### Adding New Genres
Update the genre classification logic in `backend/app.py`:
```python
# Add new channel mappings
new_channels = ['Channel Name', 'Another Channel']
new_count = sum(count for channel, count in channel_counts.items()
               if any(new_ch in channel for new_ch in new_channels))
```

## 🐛 Troubleshooting

### Common Issues

#### "Genre tree is empty"
- **Cause**: Database path mismatch or missing video IDs
- **Solution**: Ensure `data/youtube_videos.db` exists and video IDs in `youtube_watch_history.json` match database records

#### Docker networking errors
- **Cause**: Port conflicts or iptables issues
- **Solution**: Use bridge networking mode (already configured)

#### Frontend not loading genre data
- **Cause**: Backend API connection issues
- **Solution**: Check backend health at `http://localhost:5000/health`

### Health Checks
```bash
# Backend status
curl http://localhost:5000/health

# Test genre tree generation
curl http://localhost:5000/api/profile

# Frontend accessibility
curl -I http://localhost:3000
```

### Logs
```bash
# View all logs
docker-compose logs

# Backend only
docker-compose logs backend

# Frontend only
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

## Optional: Data Scraping

To update the video database with fresh data:
```bash
docker-compose --profile scraper up scraper
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test with Docker: `docker-compose up --build`
5. Submit a pull request

## 📝 License

This project is for educational and demonstration purposes.

## 🎬 Vision

WhyExplore transforms passive YouTube consumption into active discovery through tactile, vintage-inspired interactions combined with intelligent personalization. Instead of being fed content by algorithms, users curate their own exploration journey like programming their own film festival.

---

**Happy Exploring!** 🎥✨