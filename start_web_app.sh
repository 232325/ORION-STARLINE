#!/bin/bash

# Orion Starline - Full-Stack Web Application Startup Script
# Usage: ./start_web_app.sh [option]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    🚀 Orion Starline Trading Platform"
    echo "         Full-Stack Web Application"
    echo "=================================================="
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is required but not installed."
        exit 1
    fi
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.template .env
        print_warning "Please edit .env file with your configuration before running."
        read -p "Press Enter to continue after editing .env file..."
    fi
    
    print_status "Dependencies check passed ✓"
}

setup_environment() {
    print_status "Setting up environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_status "Environment setup complete ✓"
}

start_backend() {
    print_status "Starting FastAPI backend server..."
    source venv/bin/activate
    cd backend && python web_app_backend.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend_pid
    print_status "Backend server started on port 8000 (PID: $BACKEND_PID)"
}

start_frontend() {
    print_status "Starting Streamlit frontend..."
    source venv/bin/activate
    cd frontend && streamlit run web_app.py --server.port 8501 --server.address 0.0.0.0 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > .frontend_pid
    print_status "Frontend server started on port 8501 (PID: $FRONTEND_PID)"
}

start_with_docker() {
    print_status "Starting with Docker Compose..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is required but not installed."
        exit 1
    fi
    
    docker-compose -f docker-compose.web-app.yml up -d
    
    print_status "Docker containers started successfully!"
    print_status "Frontend: http://localhost:8501"
    print_status "Backend API: http://localhost:8000"
    print_status "Grafana: http://localhost:3000"
    print_status "Prometheus: http://localhost:9090"
}

stop_services() {
    print_status "Stopping services..."
    
    # Stop backend
    if [ -f ".backend_pid" ]; then
        BACKEND_PID=$(cat .backend_pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm .backend_pid
    fi
    
    # Stop frontend
    if [ -f ".frontend_pid" ]; then
        FRONTEND_PID=$(cat .frontend_pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm .frontend_pid
    fi
    
    # Kill any remaining Python processes
    pkill -f "web_app_backend.py" 2>/dev/null || true
    pkill -f "streamlit.*web_app.py" 2>/dev/null || true
    
    print_status "Services stopped ✓"
}

show_logs() {
    print_status "Showing application logs..."
    echo "=================================================="
    echo "Backend Logs:"
    echo "=================================================="
    if [ -d "logs" ]; then
        tail -f logs/backend.log 2>/dev/null || echo "No backend logs found"
    else
        echo "No logs directory found"
    fi
    
    echo ""
    echo "=================================================="
    echo "Frontend Logs:"
    echo "=================================================="
    tail -f logs/frontend.log 2>/dev/null || echo "No frontend logs found"
}

show_status() {
    print_status "Application status..."
    
    echo ""
    echo "Backend Status:"
    if curl -f http://localhost:8000/health &>/dev/null; then
        echo -e "  ${GREEN}✓ Backend is running${NC}"
    else
        echo -e "  ${RED}✗ Backend is not running${NC}"
    fi
    
    echo ""
    echo "Frontend Status:"
    if curl -f http://localhost:8501 &>/dev/null; then
        echo -e "  ${GREEN}✓ Frontend is running${NC}"
    else
        echo -e "  ${RED}✗ Frontend is not running${NC}"
    fi
}

show_urls() {
    print_status "Application URLs:"
    echo ""
    echo "🌐 Frontend (Streamlit): http://localhost:8501"
    echo "🔌 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "📊 Health Check: http://localhost:8000/health"
    echo ""
    echo "💡 Additional Services (if using Docker):"
    echo "📈 Grafana Dashboard: http://localhost:3000"
    echo "📊 Prometheus: http://localhost:9090"
    echo "🗄️  Redis: localhost:6379"
    echo "🗃️  PostgreSQL: localhost:5432"
}

# Main script logic
case "${1:-start}" in
    "start")
        print_header
        check_dependencies
        setup_environment
        stop_services  # Stop any existing services
        start_backend
        start_frontend
        echo ""
        print_status "Application started successfully!"
        show_urls
        ;;
    
    "start-docker")
        print_header
        check_dependencies
        start_with_docker
        show_urls
        ;;
    
    "stop")
        stop_services
        print_status "Application stopped"
        ;;
    
    "restart")
        stop_services
        sleep 2
        $0 start
        ;;
    
    "logs")
        show_logs
        ;;
    
    "status")
        show_status
        ;;
    
    "setup")
        print_header
        check_dependencies
        setup_environment
        print_status "Setup completed! Run './start_web_app.sh start' to begin."
        ;;
    
    "help"|"-h"|"--help")
        print_header
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  start        Start the application (default)"
        echo "  start-docker Start with Docker Compose"
        echo "  stop         Stop all services"
        echo "  restart      Restart the application"
        echo "  logs         Show application logs"
        echo "  status       Show application status"
        echo "  setup        Setup environment and dependencies"
        echo "  help         Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start         # Start normally"
        echo "  $0 start-docker  # Start with Docker"
        echo "  $0 logs          # View logs"
        echo "  $0 status        # Check status"
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Run '$0 help' for available commands."
        exit 1
        ;;
esac