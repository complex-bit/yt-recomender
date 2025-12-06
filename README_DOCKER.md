# WhyExplore - Docker Setup

Complete Docker containerization for the WhyExplore YouTube discovery platform.

## 🐳 **Container Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Scraper      │
│   (Next.js)     │◄──►│    (Flask)      │    │   (yt-dlp)      │
│   Port: 3000    │    │   Port: 5000    │    │   (Optional)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │   (Volume)      │
                       └─────────────────┘
```

## 🚀 **Quick Start**

### 1. Prerequisites
```bash
# Install Docker and Docker Compose
# On Ubuntu/Debian:
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin

# On macOS:
brew install docker docker-compose

# On Windows: Install Docker Desktop
```

### 2. Build and Run
```bash
# Clone and navigate to project
cd yt-recomender

# Build and start the main application
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## 📋 **Available Commands**

### Main Application
```bash
# Build and run everything
docker-compose up --build

# Run in background (detached)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### YouTube Scraper
```bash
# Run the YouTube scraper
docker-compose --profile scraper up scraper

# Run scraper with main app
docker-compose --profile scraper up --build

# Run scraper in background
docker-compose --profile scraper up -d scraper
```

### Development Commands
```bash
# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Run specific service
docker-compose up backend
docker-compose up frontend

# Execute commands in running container
docker-compose exec backend python yt_dlp_scraper.py --stats
docker-compose exec backend bash

# View container logs
docker-compose logs backend
docker-compose logs frontend
```

## 🔧 **Configuration**

### Environment Variables

**Backend (.env or docker-compose.yml):**
```env
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DATABASE_PATH=/app/data/youtube_videos.db
CORS_ORIGINS=http://localhost:3000
```

**Frontend:**
```env
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_TELEMETRY_DISABLED=1
```

### Volume Mounts

- `./data:/app/data` - SQLite database and scraped data
- `./backend/channels_list.txt:/app/channels_list.txt` - Channel list for scraper

## 📊 **Services Overview**

### 🖥️ **Frontend (Next.js)**
- **Port**: 3000
- **Health Check**: Automatic
- **Build**: Multi-stage optimized build
- **Features**: Standalone output for minimal image size

### ⚙️ **Backend (Flask)**
- **Port**: 5000
- **Health Check**: `/health` endpoint
- **Database**: SQLite with volume persistence
- **API**: CORS-enabled for frontend communication

### 🔍 **Scraper (yt-dlp)**
- **Purpose**: YouTube channel scraping
- **Profiles**: Only runs when explicitly requested
- **Output**: Populates SQLite database
- **Configuration**: Via `channels_list.txt`

## 🗃️ **Data Persistence**

### SQLite Database
```bash
# Database location (inside container)
/app/data/youtube_videos.db

# Host location (mounted volume)
./data/youtube_videos.db

# Backup database
docker-compose exec backend cp /app/data/youtube_videos.db /app/data/backup.db
```

### Exported Data
```bash
# JSON export location
./data/scraped_data.json

# Manual export
docker-compose exec backend python yt_dlp_scraper.py --export /app/data/manual_export.json
```

## 🎯 **Production Deployment**

### 1. Environment Setup
```bash
# Create production environment file
cat > .env.production << EOF
FLASK_ENV=production
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://your-domain.com/api
DATABASE_PATH=/app/data/youtube_videos.db
EOF
```

### 2. Production Compose File
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: whyexplore-backend:latest
    environment:
      - FLASK_ENV=production
    restart: always

  frontend:
    image: whyexplore-frontend:latest
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://your-domain.com/api
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
```

### 3. Deploy
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## 🐛 **Troubleshooting**

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using the port
sudo lsof -i :3000
sudo lsof -i :5000

# Stop conflicting services
docker-compose down
```

**2. Database Permission Issues**
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./data/

# Or run with specific user
docker-compose exec --user root backend chown -R app:app /app/data/
```

**3. Build Failures**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Docker space
docker system df
```

**4. Container Logs**
```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Debug container
docker-compose exec backend bash
```

### Health Checks

**Backend Health:**
```bash
curl http://localhost:5000/health
# Should return: {"status": "healthy"}
```

**Frontend Health:**
```bash
curl http://localhost:3000
# Should return HTML content
```

**Database Health:**
```bash
docker-compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('/app/data/youtube_videos.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM videos')
print(f'Videos in database: {cursor.fetchone()[0]}')
conn.close()
"
```

## 🔄 **CI/CD Integration**

### GitHub Actions Example
```yaml
# .github/workflows/docker.yml
name: Docker Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker images
        run: docker-compose build

      - name: Run tests
        run: |
          docker-compose up -d
          docker-compose exec backend python -m pytest
          docker-compose down
```

## 📈 **Monitoring & Logs**

### Log Management
```bash
# Configure log rotation in docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Monitoring
```bash
# Container resource usage
docker stats

# Service health
docker-compose ps

# System resources
docker system df
```

## 🚀 **Performance Optimization**

### Multi-stage Builds
- Frontend: Uses optimized Node.js Alpine image
- Backend: Minimal Python dependencies
- Layer caching for faster rebuilds

### Resource Limits
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

This Docker setup provides a complete, production-ready containerization of your WhyExplore platform! 🎉