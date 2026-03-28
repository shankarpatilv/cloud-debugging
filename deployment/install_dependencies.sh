#!/bin/bash
set -e

# Dependencies installation script for Cloud Debugging Task
# This script can be run separately if needed

echo "📦 Installing dependencies for Cloud Debugging Task..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Install Python dependencies for the service
install_service_deps() {
    log_info "Installing service dependencies..."
    
    if [ -f "service/requirements.txt" ]; then
        cd service
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        log_success "Service dependencies installed"
        cd ..
    else
        log_error "service/requirements.txt not found"
        return 1
    fi
}

# Install debug tool dependencies
install_debug_tool_deps() {
    log_info "Installing debug tool dependencies..."
    
    if [ -f "debug_tool/requirements.txt" ]; then
        cd debug_tool
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        log_success "Debug tool dependencies installed"
        cd ..
    else
        log_error "debug_tool/requirements.txt not found"
        return 1
    fi
}

# Install system dependencies (if running locally)
install_system_deps() {
    log_info "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            python3-dev \
            build-essential \
            curl \
            git
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum update -y
        sudo yum install -y \
            python3 \
            python3-pip \
            python3-devel \
            gcc \
            gcc-c++ \
            curl \
            git
    elif command -v brew &> /dev/null; then
        # macOS
        brew install python3 curl git
    else
        log_error "Unsupported package manager. Please install Python 3, curl, and git manually."
        return 1
    fi
    
    log_success "System dependencies installed"
}

# Install Docker (if not present)
install_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_info "Docker not found, installing..."
        
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian Docker installation
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
        else
            log_error "Please install Docker manually for your system"
            return 1
        fi
        
        log_success "Docker installed"
    else
        log_success "Docker already installed"
    fi
}

# Install Docker Compose (if not present)
install_docker_compose() {
    log_info "Checking Docker Compose installation..."
    
    if ! command -v docker-compose &> /dev/null; then
        log_info "Docker Compose not found, installing..."
        
        # Get latest version
        DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
        
        # Download and install
        sudo curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        log_success "Docker Compose installed"
    else
        log_success "Docker Compose already installed"
    fi
}

# Verify installations
verify_installation() {
    log_info "Verifying installations..."
    
    # Check Python
    if python3 --version > /dev/null 2>&1; then
        echo "✅ Python: $(python3 --version)"
    else
        echo "❌ Python not found"
        return 1
    fi
    
    # Check pip
    if python3 -m pip --version > /dev/null 2>&1; then
        echo "✅ pip: $(python3 -m pip --version)"
    else
        echo "❌ pip not found"
        return 1
    fi
    
    # Check service dependencies
    if [ -d "service/venv" ]; then
        echo "✅ Service virtual environment created"
    else
        echo "❌ Service virtual environment not found"
    fi
    
    # Check debug tool dependencies
    if [ -d "debug_tool/venv" ]; then
        echo "✅ Debug tool virtual environment created"
    else
        echo "❌ Debug tool virtual environment not found"
    fi
    
    # Check Docker (if requested)
    if [ "$INSTALL_DOCKER" = "true" ]; then
        if docker --version > /dev/null 2>&1; then
            echo "✅ Docker: $(docker --version)"
        else
            echo "❌ Docker not found"
            return 1
        fi
        
        if docker-compose --version > /dev/null 2>&1; then
            echo "✅ Docker Compose: $(docker-compose --version)"
        else
            echo "❌ Docker Compose not found"
            return 1
        fi
    fi
    
    log_success "All verifications passed"
}

# Usage information
show_usage() {
    echo "Dependencies Installation Script"
    echo "================================"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --all               Install all dependencies (default)"
    echo "  --service-only      Install only service dependencies"
    echo "  --debug-only        Install only debug tool dependencies"
    echo "  --system-deps       Install system dependencies"
    echo "  --docker            Install Docker and Docker Compose"
    echo "  --no-system         Skip system dependencies"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Install all dependencies"
    echo "  $0 --service-only   # Install only service dependencies"
    echo "  $0 --docker         # Install Docker and Docker Compose"
    echo ""
}

# Parse command line arguments
INSTALL_ALL=true
INSTALL_SERVICE=false
INSTALL_DEBUG=false
INSTALL_SYSTEM=true
INSTALL_DOCKER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            INSTALL_ALL=true
            shift
            ;;
        --service-only)
            INSTALL_ALL=false
            INSTALL_SERVICE=true
            INSTALL_SYSTEM=false
            shift
            ;;
        --debug-only)
            INSTALL_ALL=false
            INSTALL_DEBUG=true
            INSTALL_SYSTEM=false
            shift
            ;;
        --system-deps)
            INSTALL_SYSTEM=true
            shift
            ;;
        --docker)
            INSTALL_DOCKER=true
            shift
            ;;
        --no-system)
            INSTALL_SYSTEM=false
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_info "Starting dependency installation..."
    
    # Install system dependencies if requested
    if [ "$INSTALL_SYSTEM" = "true" ]; then
        install_system_deps
    fi
    
    # Install Docker if requested
    if [ "$INSTALL_DOCKER" = "true" ]; then
        install_docker
        install_docker_compose
    fi
    
    # Install Python dependencies
    if [ "$INSTALL_ALL" = "true" ]; then
        install_service_deps
        install_debug_tool_deps
    elif [ "$INSTALL_SERVICE" = "true" ]; then
        install_service_deps
    elif [ "$INSTALL_DEBUG" = "true" ]; then
        install_debug_tool_deps
    fi
    
    # Verify installation
    verify_installation
    
    log_success "Dependencies installation completed! 🎉"
    
    echo ""
    echo "Next steps:"
    echo "1. Activate service environment: cd service && source venv/bin/activate"
    echo "2. Activate debug tool environment: cd debug_tool && source venv/bin/activate"
    echo "3. Set up your environment variables (API keys, etc.)"
    echo "4. Run the services or use Docker Compose"
    echo ""
    
    if [ "$INSTALL_DOCKER" = "true" ] && groups | grep -q docker; then
        echo "Note: Log out and back in for Docker group membership to take effect"
    fi
}

# Run main function
main