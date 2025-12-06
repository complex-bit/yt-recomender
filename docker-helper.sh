#!/bin/bash

# WhyExplore Docker Helper Script
# Makes it easy to manage the Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Create data directory if it doesn't exist
setup_data_dir() {
    if [ ! -d "./data" ]; then
        log_info "Creating data directory..."
        mkdir -p ./data
        log_success "Data directory created"
    fi
}

# Show help
show_help() {
    echo -e "${BLUE}WhyExplore Docker Helper${NC}"
    echo ""
    echo "Usage: ./docker-helper.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Start the application (frontend + backend)"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  build           Build all Docker images"
    echo "  logs            Show logs for all services"
    echo "  logs-backend    Show backend logs"
    echo "  logs-frontend   Show frontend logs"
    echo "  scrape          Run the YouTube scraper"
    echo "  status          Show container status"
    echo "  shell-backend   Open shell in backend container"
    echo "  shell-frontend  Open shell in frontend container"
    echo "  db-stats        Show database statistics"
    echo "  backup-db       Backup the database"
    echo "  clean           Remove all containers and volumes"
    echo "  dev             Start in development mode"
    echo "  help            Show this help message"
    echo ""
}

# Main commands
case "${1:-help}" in
    "start")
        check_docker
        setup_data_dir
        log_info "Starting WhyExplore application..."
        docker-compose up -d --build
        log_success "Application started!"
        log_info "Frontend: http://localhost:3000"
        log_info "Backend: http://localhost:5000"
        ;;

    "stop")
        check_docker
        log_info "Stopping all services..."
        docker-compose down
        log_success "All services stopped"
        ;;

    "restart")
        check_docker
        log_info "Restarting all services..."
        docker-compose down
        docker-compose up -d --build
        log_success "All services restarted"
        ;;

    "build")
        check_docker
        log_info "Building Docker images..."
        docker-compose build --no-cache
        log_success "Images built successfully"
        ;;

    "logs")
        check_docker
        docker-compose logs -f
        ;;

    "logs-backend")
        check_docker
        docker-compose logs -f backend
        ;;

    "logs-frontend")
        check_docker
        docker-compose logs -f frontend
        ;;

    "scrape")
        check_docker
        setup_data_dir
        log_info "Running YouTube scraper..."
        docker-compose --profile scraper up scraper
        log_success "Scraping completed"
        ;;

    "status")
        check_docker
        docker-compose ps
        ;;

    "shell-backend")
        check_docker
        log_info "Opening shell in backend container..."
        docker-compose exec backend bash
        ;;

    "shell-frontend")
        check_docker
        log_info "Opening shell in frontend container..."
        docker-compose exec frontend sh
        ;;

    "db-stats")
        check_docker
        log_info "Fetching database statistics..."
        docker-compose exec backend python yt_dlp_scraper.py --stats
        ;;

    "backup-db")
        check_docker
        setup_data_dir
        BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).db"
        log_info "Creating database backup: $BACKUP_NAME"
        docker-compose exec backend cp /app/data/youtube_videos.db "/app/data/$BACKUP_NAME"
        log_success "Database backed up to ./data/$BACKUP_NAME"
        ;;

    "clean")
        check_docker
        log_warning "This will remove all containers, networks, and volumes!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker system prune -f
            log_success "Cleanup completed"
        else
            log_info "Cleanup cancelled"
        fi
        ;;

    "dev")
        check_docker
        setup_data_dir
        log_info "Starting in development mode..."
        log_warning "This will use local files instead of containers for development"
        # Kill any existing containers
        docker-compose down 2>/dev/null || true
        log_info "Start your development servers manually:"
        log_info "Backend: cd backend && source venv/bin/activate && python app.py"
        log_info "Frontend: cd web_platform && npm run dev"
        ;;

    "help"|*)
        show_help
        ;;
esac