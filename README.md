# YouTube Recommender

A YouTube video recommendation system that analyzes your watch history and suggests new content based on your preferences.

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd yt-recomender
   ```

2. Start the application:
   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Services

- **Frontend**: Next.js web application for the user interface
- **Backend**: Flask API for recommendations and data processing
- **Database**: SQLite database with pre-populated YouTube video data

## Optional: Data Scraping

To update the video database with fresh data:
```bash
docker-compose --profile scraper up scraper
```

## Stopping the Application

```bash
docker-compose down
```

## Requirements

- Docker
- Docker Compose