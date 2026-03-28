#!/bin/bash
set -e

# EC2 instance setup script
# This script sets up the EC2 instance with all required dependencies

echo "🔧 Setting up EC2 instance for Cloud Debugging Task..."

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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Update system packages
update_system() {
    log_info "Updating system packages..."
    sudo apt-get update
    sudo apt-get upgrade -y
    log_success "System updated"
}

# Install Docker
install_docker() {
    log_info "Installing Docker..."
    
    # Remove any old versions
    sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Install prerequisites
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker ubuntu
    
    # Enable and start Docker
    sudo systemctl enable docker
    sudo systemctl start docker
    
    log_success "Docker installed"
}

# Install Docker Compose (standalone)
install_docker_compose() {
    log_info "Installing Docker Compose..."
    
    # Get latest version
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    # Download and install
    sudo curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Verify installation
    docker-compose --version
    
    log_success "Docker Compose installed"
}

# Install Python (if needed for debugging)
install_python() {
    log_info "Installing Python and pip..."
    
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev
    
    # Update pip
    python3 -m pip install --upgrade pip
    
    log_success "Python installed"
}

# Install additional tools
install_tools() {
    log_info "Installing additional tools..."
    
    sudo apt-get install -y \
        curl \
        wget \
        git \
        htop \
        tree \
        jq \
        unzip \
        vim \
        nano \
        net-tools
    
    log_success "Additional tools installed"
}

# Configure firewall
configure_firewall() {
    log_info "Configuring firewall..."
    
    # Install ufw if not present
    sudo apt-get install -y ufw
    
    # Reset to defaults
    sudo ufw --force reset
    
    # Default policies
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Allow SSH (port 22)
    sudo ufw allow ssh
    
    # Allow HTTP (port 80) - for potential reverse proxy
    sudo ufw allow 80/tcp
    
    # Allow HTTPS (port 443) - for potential SSL
    sudo ufw allow 443/tcp
    
    # Allow our application port (8000)
    sudo ufw allow 8000/tcp
    
    # Enable firewall
    sudo ufw --force enable
    
    # Show status
    sudo ufw status
    
    log_success "Firewall configured"
}

# Create application directory structure
setup_directories() {
    log_info "Setting up directory structure..."
    
    # Create application directories
    sudo mkdir -p /opt/cloud-debugging-task
    sudo mkdir -p /var/log/cloud-debugging-task
    sudo mkdir -p /var/lib/cloud-debugging-task
    
    # Set ownership
    sudo chown -R ubuntu:ubuntu /opt/cloud-debugging-task
    sudo chown -R ubuntu:ubuntu /var/log/cloud-debugging-task
    sudo chown -R ubuntu:ubuntu /var/lib/cloud-debugging-task
    
    # Create symlinks for easier access
    ln -sf /opt/cloud-debugging-task ~/app
    ln -sf /var/log/cloud-debugging-task ~/logs
    
    log_success "Directory structure created"
}

# Configure log rotation
setup_log_rotation() {
    log_info "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/cloud-debugging-task > /dev/null << EOF
/var/log/cloud-debugging-task/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    postrotate
        /usr/bin/docker exec cloud-debugging-task_data-processing-service_1 killall -USR1 uvicorn 2>/dev/null || true
    endscript
}
EOF
    
    log_success "Log rotation configured"
}

# Setup system monitoring
setup_monitoring() {
    log_info "Setting up basic monitoring..."
    
    # Create monitoring script
    sudo tee /usr/local/bin/app-monitor.sh > /dev/null << 'EOF'
#!/bin/bash
# Simple application monitoring script

APP_URL="http://localhost:8000/health"
LOG_FILE="/var/log/cloud-debugging-task/monitor.log"

check_app() {
    if curl -f -s "$APP_URL" > /dev/null; then
        echo "$(date): Application is healthy" >> "$LOG_FILE"
    else
        echo "$(date): Application health check failed" >> "$LOG_FILE"
        # Could add alerting here
    fi
}

check_app
EOF
    
    sudo chmod +x /usr/local/bin/app-monitor.sh
    
    # Add cron job for monitoring (every 5 minutes)
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/app-monitor.sh") | crontab -
    
    log_success "Basic monitoring setup completed"
}

# Create systemd service (optional, for non-Docker deployment)
create_systemd_service() {
    log_info "Creating systemd service..."
    
    sudo tee /etc/systemd/system/cloud-debugging-task.service > /dev/null << EOF
[Unit]
Description=Cloud Debugging Task API Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/cloud-debugging-task
ExecStart=/usr/local/bin/docker-compose -f deployment/docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f deployment/docker-compose.prod.yml down
User=ubuntu
Group=ubuntu

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable cloud-debugging-task.service
    
    log_success "Systemd service created"
}

# Optimize system for the application
optimize_system() {
    log_info "Optimizing system settings..."
    
    # Increase file descriptor limits
    sudo tee -a /etc/security/limits.conf > /dev/null << EOF
ubuntu soft nofile 65536
ubuntu hard nofile 65536
ubuntu soft nproc 4096
ubuntu hard nproc 4096
EOF
    
    # Configure sysctl for better network performance
    sudo tee /etc/sysctl.d/99-app-optimization.conf > /dev/null << EOF
# Network optimizations
net.core.somaxconn = 1024
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 1024
net.ipv4.tcp_slow_start_after_idle = 0

# Memory management
vm.swappiness = 10
vm.overcommit_memory = 1
EOF
    
    sudo sysctl -p /etc/sysctl.d/99-app-optimization.conf
    
    log_success "System optimizations applied"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    # Check Docker
    if ! docker --version > /dev/null 2>&1; then
        log_error "Docker installation failed"
        return 1
    fi
    
    # Check Docker Compose
    if ! docker-compose --version > /dev/null 2>&1; then
        log_error "Docker Compose installation failed"
        return 1
    fi
    
    # Check Python
    if ! python3 --version > /dev/null 2>&1; then
        log_error "Python installation failed"
        return 1
    fi
    
    # Check directories
    if [ ! -d "/opt/cloud-debugging-task" ]; then
        log_error "Application directory not created"
        return 1
    fi
    
    log_success "All components verified successfully"
    
    # Display versions
    echo ""
    echo "Installed versions:"
    echo "Docker: $(docker --version)"
    echo "Docker Compose: $(docker-compose --version)"
    echo "Python: $(python3 --version)"
    echo ""
}

# Main setup function
main() {
    log_info "Starting EC2 setup for Cloud Debugging Task"
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        log_error "Please run this script as ubuntu user, not root"
        exit 1
    fi
    
    # Run setup steps
    update_system
    install_docker
    install_docker_compose
    install_python
    install_tools
    configure_firewall
    setup_directories
    setup_log_rotation
    setup_monitoring
    create_systemd_service
    optimize_system
    verify_installation
    
    log_success "EC2 setup completed successfully! 🎉"
    
    echo ""
    echo "Next steps:"
    echo "1. The application will be deployed to /opt/cloud-debugging-task"
    echo "2. Logs will be available in /var/log/cloud-debugging-task"
    echo "3. Use 'sudo systemctl start cloud-debugging-task' to start via systemd"
    echo "4. Or use docker-compose in /opt/cloud-debugging-task/"
    echo ""
    echo "Monitoring:"
    echo "- Health checks run every 5 minutes"
    echo "- Log rotation configured for daily rotation"
    echo "- Basic system optimizations applied"
    echo ""
    
    log_warning "Please log out and back in for Docker group membership to take effect"
}

# Run main function
main "$@"