#!/bin/bash
set -e

# Main deployment script for AWS EC2
# This script orchestrates the entire deployment process

echo "🚀 Starting deployment to AWS EC2..."

# Configuration
EC2_USER="${EC2_USER:-ubuntu}"
EC2_HOST="${EC2_HOST}"
KEY_PATH="${AWS_KEY_PATH}"
PROJECT_NAME="cloud-debugging-task"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

# Check required environment variables
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if [ -z "$EC2_HOST" ]; then
        log_error "EC2_HOST environment variable is not set"
        echo "Please set EC2_HOST to your EC2 instance's public IP or hostname"
        exit 1
    fi
    
    if [ -z "$KEY_PATH" ]; then
        log_error "AWS_KEY_PATH environment variable is not set"
        echo "Please set AWS_KEY_PATH to your EC2 key pair file path"
        exit 1
    fi
    
    if [ ! -f "$KEY_PATH" ]; then
        log_error "Key file not found: $KEY_PATH"
        exit 1
    fi
    
    # Check if we can connect to the instance
    if ! ssh -i "$KEY_PATH" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "echo 'Connection test successful'" > /dev/null 2>&1; then
        log_error "Cannot connect to EC2 instance: $EC2_HOST"
        log_info "Please check your EC2_HOST and AWS_KEY_PATH settings"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create deployment package
create_deployment_package() {
    # Redirect all output to stderr except the final path
    {
        log_info "Creating deployment package..."
        
        # Create temporary directory for deployment files
        TEMP_DIR=$(mktemp -d)
        DEPLOY_DIR="$TEMP_DIR/$PROJECT_NAME"
        
        mkdir -p "$DEPLOY_DIR"
        
        # Get the script's parent directory (project root)
        SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
        PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
        
        # Copy necessary files
        cp -r "$PROJECT_ROOT/service" "$DEPLOY_DIR/"
        
        # Copy CSV file (create from Excel if needed)
        if [ -f "$PROJECT_ROOT/churn_data.csv" ]; then
            cp "$PROJECT_ROOT/churn_data.csv" "$DEPLOY_DIR/"
        elif [ -f "$PROJECT_ROOT/churn-bigml-full.xlsx" ]; then
            log_info "Converting Excel to CSV..."
            python3 -c "import pandas as pd; df = pd.read_excel('$PROJECT_ROOT/churn-bigml-full.xlsx'); df.to_csv('$DEPLOY_DIR/churn_data.csv', index=False)"
            log_success "CSV created from Excel file"
        else
            log_warning "No data file found (churn_data.csv or churn-bigml-full.xlsx)"
        fi
        
        cp -r "$PROJECT_ROOT/deployment" "$DEPLOY_DIR/"
        
        # Copy debug tool
        cp -r "$PROJECT_ROOT/debug_tool" "$DEPLOY_DIR/"
        
        # Copy documentation and examples
        [ -f "$PROJECT_ROOT/README.md" ] && cp "$PROJECT_ROOT/README.md" "$DEPLOY_DIR/"
        [ -d "$PROJECT_ROOT/examples" ] && cp -r "$PROJECT_ROOT/examples" "$DEPLOY_DIR/"
        
        # Copy environment file if it exists
        if [ -f "$PROJECT_ROOT/.env" ]; then
            cp "$PROJECT_ROOT/.env" "$DEPLOY_DIR/"
        fi
        
        # Create production environment file
        cat > "$DEPLOY_DIR/.env.prod" << EOF
ENVIRONMENT=production
LOG_LEVEL=info
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./data/jobs.db
EOF
        
        # Create archive
        cd "$TEMP_DIR"
        tar -czf "${PROJECT_NAME}-deploy.tar.gz" "$PROJECT_NAME"
    } >&2
    
    # Only output the path to stdout
    echo "$TEMP_DIR/${PROJECT_NAME}-deploy.tar.gz"
}

# Upload files to EC2
upload_to_ec2() {
    local package_path=$1
    log_info "Uploading deployment package to EC2..."
    
    # Upload the package
    scp -i "$KEY_PATH" -o StrictHostKeyChecking=no "$package_path" "$EC2_USER@$EC2_HOST:~/"
    
    # Extract on remote server
    ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
        # Remove old deployment if exists
        sudo rm -rf /opt/cloud-debugging-task
        
        # Extract new deployment
        cd ~
        tar -xzf cloud-debugging-task-deploy.tar.gz
        sudo mv cloud-debugging-task /opt/
        sudo chown -R ubuntu:ubuntu /opt/cloud-debugging-task
        
        # Cleanup
        rm cloud-debugging-task-deploy.tar.gz
EOF
    
    log_success "Files uploaded successfully"
}

# Setup EC2 instance
setup_ec2() {
    log_info "Setting up EC2 instance..."
    
    ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
        cd /opt/cloud-debugging-task
        chmod +x deployment/setup_ec2.sh
        ./deployment/setup_ec2.sh
EOF
    
    log_success "EC2 instance setup completed"
}

# Deploy the application
deploy_application() {
    log_info "Deploying application..."
    
    ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
        cd /opt/cloud-debugging-task
        
        # Stop existing containers
        sudo docker-compose -f deployment/docker-compose.prod.yml down || true
        
        # Build and start the application
        sudo docker-compose -f deployment/docker-compose.prod.yml up --build -d
        
        # Wait for the service to be ready
        echo "Waiting for service to start..."
        sleep 30
EOF
    
    log_success "Application deployed"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Wait a bit more for the service to fully initialize
    sleep 10
    
    # Test the health endpoint
    if curl -f -s "http://$EC2_HOST:8000/health" > /dev/null; then
        log_success "Health check passed - service is running"
        
        # Display service information
        echo ""
        echo "🎉 Deployment successful!"
        echo "Service URL: http://$EC2_HOST:8000"
        echo "Health check: http://$EC2_HOST:8000/health"
        echo "API Documentation: http://$EC2_HOST:8000/docs"
        echo ""
        echo "Test the service:"
        echo "curl http://$EC2_HOST:8000/health"
        echo ""
    else
        log_error "Health check failed - service may not be running properly"
        
        echo "Checking container logs..."
        ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
            cd /opt/cloud-debugging-task
            sudo docker-compose -f deployment/docker-compose.prod.yml logs --tail=50
EOF
        exit 1
    fi
}

# Rollback function
rollback() {
    log_warning "Rolling back deployment..."
    
    ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
        cd /opt/cloud-debugging-task
        sudo docker-compose -f deployment/docker-compose.prod.yml down
EOF
    
    log_info "Rollback completed"
}

# Main deployment flow
main() {
    local skip_upload=false
    local skip_setup=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-upload)
                skip_upload=true
                shift
                ;;
            --skip-setup)
                skip_setup=true
                shift
                ;;
            --rollback)
                rollback
                exit 0
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --skip-upload    Skip file upload step"
                echo "  --skip-setup     Skip EC2 setup step"
                echo "  --rollback       Rollback the deployment"
                echo "  --help           Show this help message"
                echo ""
                echo "Environment variables required:"
                echo "  EC2_HOST         EC2 instance public IP or hostname"
                echo "  AWS_KEY_PATH     Path to EC2 key pair file"
                echo "  EC2_USER         EC2 username (default: ubuntu)"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Trap errors and provide rollback option
    trap 'log_error "Deployment failed. Run with --rollback to clean up."; exit 1' ERR
    
    check_prerequisites
    
    if [ "$skip_upload" = false ]; then
        package_path=$(create_deployment_package)
        log_success "Deployment package created"
        upload_to_ec2 "$package_path"
        rm -rf "$(dirname "$package_path")"
    fi
    
    if [ "$skip_setup" = false ]; then
        setup_ec2
    fi
    
    deploy_application
    health_check
    
    log_success "Deployment completed successfully! 🎉"
}

# Show usage if no EC2_HOST is provided
if [ -z "$EC2_HOST" ] && [ "$1" != "--help" ]; then
    echo "Cloud Debugging Task - AWS EC2 Deployment"
    echo "========================================="
    echo ""
    echo "Before running this script, set the required environment variables:"
    echo ""
    echo "export EC2_HOST=\"your-ec2-instance-ip\""
    echo "export AWS_KEY_PATH=\"/path/to/your/keypair.pem\""
    echo ""
    echo "Example:"
    echo "export EC2_HOST=\"54.123.45.67\""
    echo "export AWS_KEY_PATH=\"~/.ssh/my-keypair.pem\""
    echo ""
    echo "Then run: ./deploy.sh"
    echo ""
    echo "Use --help for more options"
    exit 1
fi

# Run main function with all arguments
main "$@"