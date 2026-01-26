#!/bin/bash
# Vibe4Vets Production Build Startup Script
# Builds and starts backend (FastAPI) and frontend (Next.js production build)

set -e

PROJECT_ROOT="/home/marci/projects/vibe4vets"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PID files for tracking processes
BACKEND_PID_FILE="/tmp/vibe4vets-backend-prod.pid"
FRONTEND_PID_FILE="/tmp/vibe4vets-frontend-prod.pid"
LOG_DIR="/tmp/vibe4vets-logs-prod"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to stop all services
stop_services() {
    log_info "Stopping Vibe4Vets services..."

    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            kill "$BACKEND_PID" 2>/dev/null || true
            log_success "Backend stopped (PID: $BACKEND_PID)"
        fi
        rm -f "$BACKEND_PID_FILE"
    fi

    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            kill "$FRONTEND_PID" 2>/dev/null || true
            log_success "Frontend stopped (PID: $FRONTEND_PID)"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi

    # Also kill any remaining processes on the ports
    fuser -k 8000/tcp 2>/dev/null || true
    fuser -k 3000/tcp 2>/dev/null || true

    log_success "All services stopped"
}

# Function to check if a port is available
wait_for_port() {
    local port=$1
    local name=$2
    local max_wait=60
    local count=0

    log_info "Waiting for $name on port $port..."
    while ! nc -z localhost "$port" 2>/dev/null; do
        sleep 1
        count=$((count + 1))
        if [ $count -ge $max_wait ]; then
            log_error "$name failed to start within ${max_wait}s"
            return 1
        fi
    done
    log_success "$name is ready on port $port"
    return 0
}

# Function to ensure Docker containers are running
ensure_docker() {
    log_info "Checking Docker containers..."

    # Check if docker is available
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    # Check if docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi

    # Check if the db container is running
    if docker compose -f "$PROJECT_ROOT/docker-compose.yml" ps --status running 2>/dev/null | grep -q "db"; then
        log_success "PostgreSQL container is already running"
    else
        log_info "Starting PostgreSQL container..."
        docker compose -f "$PROJECT_ROOT/docker-compose.yml" up -d db

        # Wait for PostgreSQL to be healthy
        local max_wait=30
        local count=0
        log_info "Waiting for PostgreSQL to be ready..."
        while ! docker compose -f "$PROJECT_ROOT/docker-compose.yml" ps --status running 2>/dev/null | grep -q "db.*healthy"; do
            sleep 1
            count=$((count + 1))
            if [ $count -ge $max_wait ]; then
                # Check if it's at least running (healthcheck might not show)
                if docker compose -f "$PROJECT_ROOT/docker-compose.yml" ps --status running 2>/dev/null | grep -q "db"; then
                    log_warn "PostgreSQL running but health status unknown, proceeding..."
                    break
                fi
                log_error "PostgreSQL failed to start within ${max_wait}s"
                docker compose -f "$PROJECT_ROOT/docker-compose.yml" logs db
                exit 1
            fi
        done
        log_success "PostgreSQL container is ready"
    fi
}

# Function to start services
start_services() {
    log_info "Starting Vibe4Vets Production Environment"
    echo ""

    # Ensure Docker containers are running first
    ensure_docker
    echo ""

    # Create log directory
    mkdir -p "$LOG_DIR"

    # Check if ports are in use
    if nc -z localhost 8000 2>/dev/null; then
        log_warn "Port 8000 already in use. Stopping existing process..."
        fuser -k 8000/tcp 2>/dev/null || true
        sleep 2
    fi

    if nc -z localhost 3000 2>/dev/null; then
        log_warn "Port 3000 already in use. Stopping existing process..."
        fuser -k 3000/tcp 2>/dev/null || true
        sleep 2
    fi

    # Start Backend
    log_info "Starting Backend (FastAPI)..."
    cd "$BACKEND_DIR"

    # Activate venv and start uvicorn (no --reload for production)
    source .venv/bin/activate
    nohup uvicorn app.main:app --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    log_info "Backend PID: $(cat $BACKEND_PID_FILE)"

    # Build and Start Frontend
    log_info "Building Frontend (Next.js production build)..."
    cd "$FRONTEND_DIR"

    # Always clear .next cache for fresh production build
    if [ -d ".next" ]; then
        log_info "Clearing .next cache..."
        rm -rf .next
        log_success ".next cache cleared"
    fi

    # Build the production bundle
    log_info "Running npm run build (this may take a moment)..."
    npm run build > "$LOG_DIR/frontend-build.log" 2>&1 || {
        log_error "Frontend build failed! Check logs at $LOG_DIR/frontend-build.log"
        tail -30 "$LOG_DIR/frontend-build.log"
        stop_services
        exit 1
    }
    log_success "Frontend build complete"

    # Start the production server
    log_info "Starting Frontend (Next.js production server)..."
    nohup npm run start > "$LOG_DIR/frontend.log" 2>&1 &
    echo $! > "$FRONTEND_PID_FILE"
    log_info "Frontend PID: $(cat $FRONTEND_PID_FILE)"

    # Wait for services to be ready
    echo ""
    wait_for_port 8000 "Backend" || {
        log_error "Check logs at $LOG_DIR/backend.log"
        echo "--- Last 30 lines of backend.log ---"
        tail -30 "$LOG_DIR/backend.log"
        stop_services
        exit 1
    }
    wait_for_port 3000 "Frontend" || {
        log_error "Check logs at $LOG_DIR/frontend.log"
        stop_services
        exit 1
    }

    echo ""
    log_success "============================================"
    log_success "  Vibe4Vets Production Environment Ready!"
    log_success "============================================"
    echo ""
    echo -e "  Frontend:  ${GREEN}http://localhost:3000${NC}"
    echo -e "  Backend:   ${GREEN}http://localhost:8000${NC}"
    echo -e "  API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "  Logs:      ${BLUE}$LOG_DIR${NC}"
    echo ""
    log_info "Press Ctrl+C to stop all services"
    echo ""

    # Open browser (works on WSL and Linux)
    if command -v wslview &> /dev/null; then
        wslview http://localhost:3000 2>/dev/null &
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000 2>/dev/null &
    fi

    # Wait for interrupt
    trap stop_services EXIT INT TERM

    # Keep script running - tail both logs
    tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log"
}

# Handle command line arguments
case "${1:-start}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    status)
        echo "Checking Vibe4Vets services..."
        # Docker status
        if docker compose -f "$PROJECT_ROOT/docker-compose.yml" ps --status running 2>/dev/null | grep -q "db"; then
            log_success "PostgreSQL container is running"
        else
            log_warn "PostgreSQL container is not running"
        fi
        # Backend status
        if nc -z localhost 8000 2>/dev/null; then
            log_success "Backend is running on port 8000"
        else
            log_warn "Backend is not running"
        fi
        # Frontend status
        if nc -z localhost 3000 2>/dev/null; then
            log_success "Frontend is running on port 3000"
        else
            log_warn "Frontend is not running"
        fi
        ;;
    logs)
        if [ -d "$LOG_DIR" ]; then
            tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log"
        else
            log_error "No log directory found"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
