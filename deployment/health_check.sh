#!/bin/bash
set -e

# Health check script for the Cloud Debugging Task service
# This script performs comprehensive health checks on the deployed service

echo "🏥 Performing health checks on Cloud Debugging Task service..."

# Configuration
SERVICE_HOST="${SERVICE_HOST:-localhost}"
SERVICE_PORT="${SERVICE_PORT:-8000}"
BASE_URL="http://$SERVICE_HOST:$SERVICE_PORT"
TIMEOUT=30
MAX_RETRIES=5
RETRY_INTERVAL=10

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

# Health check functions
check_basic_connectivity() {
    log_info "Checking basic connectivity..."
    
    if curl -f -s --connect-timeout $TIMEOUT "$BASE_URL/health" > /dev/null; then
        log_success "Basic connectivity: OK"
        return 0
    else
        log_error "Basic connectivity: FAILED"
        return 1
    fi
}

check_health_endpoint() {
    log_info "Checking health endpoint..."
    
    local response=$(curl -s --connect-timeout $TIMEOUT "$BASE_URL/health" 2>/dev/null)
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$BASE_URL/health" 2>/dev/null)
    
    if [ "$http_code" = "200" ]; then
        log_success "Health endpoint: HTTP $http_code"
        echo "Response: $response"
        
        # Check if response contains expected fields
        if echo "$response" | jq -e '.status' > /dev/null 2>&1; then
            local status=$(echo "$response" | jq -r '.status')
            log_success "Service status: $status"
        else
            log_warning "Health response doesn't contain expected status field"
        fi
        
        return 0
    else
        log_error "Health endpoint: HTTP $http_code"
        return 1
    fi
}

check_api_endpoints() {
    log_info "Checking API endpoints..."
    
    local endpoints=(
        "/health"
        "/status" 
        "/jobs"
        "/docs"
    )
    
    local failed_count=0
    
    for endpoint in "${endpoints[@]}"; do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$BASE_URL$endpoint" 2>/dev/null)
        
        if [ "$http_code" = "200" ]; then
            log_success "Endpoint $endpoint: HTTP $http_code"
        elif [ "$http_code" = "404" ] && [ "$endpoint" = "/docs" ]; then
            log_warning "Endpoint $endpoint: HTTP $http_code (docs may be disabled in production)"
        else
            log_error "Endpoint $endpoint: HTTP $http_code"
            ((failed_count++))
        fi
    done
    
    if [ $failed_count -eq 0 ]; then
        log_success "All API endpoints accessible"
        return 0
    else
        log_error "$failed_count API endpoints failed"
        return 1
    fi
}

check_database_connectivity() {
    log_info "Checking database connectivity..."
    
    # Test by trying to get jobs list (which requires database)
    local response=$(curl -s --connect-timeout $TIMEOUT "$BASE_URL/jobs" 2>/dev/null)
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$BASE_URL/jobs" 2>/dev/null)
    
    if [ "$http_code" = "200" ]; then
        log_success "Database connectivity: OK"
        
        # Check if we get a valid jobs response
        if echo "$response" | jq -e '.jobs' > /dev/null 2>&1; then
            local job_count=$(echo "$response" | jq -r '.jobs | length')
            log_info "Current jobs in database: $job_count"
        fi
        
        return 0
    else
        log_error "Database connectivity: FAILED (HTTP $http_code)"
        return 1
    fi
}

test_data_processing() {
    log_info "Testing data processing capabilities..."
    
    # Test a simple filter operation
    local test_request='{"column": "State", "operator": "==", "value": "CA"}'
    local response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$test_request" \
        --connect-timeout $TIMEOUT \
        "$BASE_URL/jobs/filter" 2>/dev/null)
    
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$test_request" \
        --connect-timeout $TIMEOUT \
        "$BASE_URL/jobs/filter" 2>/dev/null)
    
    if [ "$http_code" = "200" ]; then
        log_success "Data processing: OK"
        
        # Extract job ID if available
        if echo "$response" | jq -e '.job_id' > /dev/null 2>&1; then
            local job_id=$(echo "$response" | jq -r '.job_id')
            log_info "Test job created with ID: $job_id"
            
            # Try to retrieve the job
            local job_response=$(curl -s --connect-timeout $TIMEOUT "$BASE_URL/jobs/$job_id" 2>/dev/null)
            local job_http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$BASE_URL/jobs/$job_id" 2>/dev/null)
            
            if [ "$job_http_code" = "200" ]; then
                log_success "Job retrieval: OK"
                
                # Check job status
                if echo "$job_response" | jq -e '.status' > /dev/null 2>&1; then
                    local job_status=$(echo "$job_response" | jq -r '.status')
                    log_info "Test job status: $job_status"
                fi
            else
                log_warning "Job retrieval: FAILED (HTTP $job_http_code)"
            fi
        fi
        
        return 0
    else
        log_error "Data processing: FAILED (HTTP $http_code)"
        echo "Response: $response"
        return 1
    fi
}

check_system_resources() {
    log_info "Checking system resources..."
    
    if [ "$SERVICE_HOST" = "localhost" ] || [ "$SERVICE_HOST" = "127.0.0.1" ]; then
        # Local system check
        log_info "Memory usage: $(free -h | grep '^Mem:' | awk '{print $3 "/" $2}')"
        log_info "Disk usage: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
        log_info "CPU load: $(uptime | awk -F'load average:' '{print $2}')"
        
        # Check if Docker containers are running
        if command -v docker > /dev/null 2>&1; then
            local container_count=$(docker ps | grep -c cloud-debugging-task || echo "0")
            log_info "Running containers: $container_count"
        fi
        
        log_success "System resources: Checked"
    else
        log_info "Skipping system resource check for remote host"
    fi
}

check_logs() {
    log_info "Checking application logs..."
    
    if [ "$SERVICE_HOST" = "localhost" ] || [ "$SERVICE_HOST" = "127.0.0.1" ]; then
        # Check for recent errors in logs
        local log_files=(
            "/var/log/cloud-debugging-task/app.log"
            "./service/logs/app.log"
            "./logs/app.log"
        )
        
        local log_found=false
        for log_file in "${log_files[@]}"; do
            if [ -f "$log_file" ]; then
                log_found=true
                local error_count=$(grep -c "ERROR" "$log_file" 2>/dev/null || echo "0")
                local warning_count=$(grep -c "WARNING" "$log_file" 2>/dev/null || echo "0")
                
                log_info "Log file: $log_file"
                log_info "Recent errors: $error_count, warnings: $warning_count"
                
                # Show recent errors if any
                if [ "$error_count" -gt 0 ]; then
                    log_warning "Recent errors found:"
                    tail -20 "$log_file" | grep "ERROR" | tail -5
                fi
                break
            fi
        done
        
        if [ "$log_found" = false ]; then
            log_warning "No log files found in expected locations"
        fi
    else
        log_info "Skipping log check for remote host"
    fi
}

# Comprehensive health check with retries
perform_health_check() {
    local retry_count=0
    local failed_checks=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log_info "Health check attempt $((retry_count + 1))/$MAX_RETRIES"
        failed_checks=0
        
        # Run all health checks
        check_basic_connectivity || ((failed_checks++))
        check_health_endpoint || ((failed_checks++))
        check_api_endpoints || ((failed_checks++))
        check_database_connectivity || ((failed_checks++))
        test_data_processing || ((failed_checks++))
        check_system_resources
        check_logs
        
        if [ $failed_checks -eq 0 ]; then
            log_success "All health checks passed! 🎉"
            return 0
        else
            log_warning "$failed_checks health checks failed"
            
            if [ $retry_count -lt $((MAX_RETRIES - 1)) ]; then
                log_info "Retrying in $RETRY_INTERVAL seconds..."
                sleep $RETRY_INTERVAL
            fi
        fi
        
        ((retry_count++))
    done
    
    log_error "Health checks failed after $MAX_RETRIES attempts"
    return 1
}

# Quick health check (single attempt)
quick_health_check() {
    log_info "Performing quick health check..."
    
    if check_basic_connectivity && check_health_endpoint; then
        log_success "Quick health check passed! ✅"
        return 0
    else
        log_error "Quick health check failed! ❌"
        return 1
    fi
}

# Show service information
show_service_info() {
    log_info "Service Information"
    echo "===================="
    echo "Service URL: $BASE_URL"
    echo "Health endpoint: $BASE_URL/health"
    echo "API docs: $BASE_URL/docs"
    echo "Jobs endpoint: $BASE_URL/jobs"
    echo "Status endpoint: $BASE_URL/status"
    echo ""
}

# Usage information
show_usage() {
    echo "Health Check Script for Cloud Debugging Task"
    echo "============================================="
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --quick             Perform quick health check only"
    echo "  --full              Perform comprehensive health check (default)"
    echo "  --host HOST         Service host (default: localhost)"
    echo "  --port PORT         Service port (default: 8000)"
    echo "  --timeout SECONDS   Request timeout (default: 30)"
    echo "  --retries COUNT     Max retry attempts (default: 5)"
    echo "  --info              Show service information and exit"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                              # Full health check on localhost:8000"
    echo "  $0 --quick                      # Quick health check"
    echo "  $0 --host 54.123.45.67         # Check remote EC2 instance"
    echo "  $0 --host example.com --port 80 # Check custom host/port"
    echo ""
    echo "Environment variables:"
    echo "  SERVICE_HOST        Service hostname/IP"
    echo "  SERVICE_PORT        Service port"
    echo ""
}

# Parse command line arguments
QUICK_CHECK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_CHECK=true
            shift
            ;;
        --full)
            QUICK_CHECK=false
            shift
            ;;
        --host)
            SERVICE_HOST="$2"
            BASE_URL="http://$SERVICE_HOST:$SERVICE_PORT"
            shift 2
            ;;
        --port)
            SERVICE_PORT="$2"
            BASE_URL="http://$SERVICE_HOST:$SERVICE_PORT"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --retries)
            MAX_RETRIES="$2"
            shift 2
            ;;
        --info)
            show_service_info
            exit 0
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
    echo "🏥 Cloud Debugging Task - Health Check"
    echo "======================================"
    
    show_service_info
    
    # Check if required tools are available
    if ! command -v curl > /dev/null 2>&1; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    if ! command -v jq > /dev/null 2>&1; then
        log_warning "jq not found - JSON parsing will be limited"
    fi
    
    # Perform health check
    if [ "$QUICK_CHECK" = true ]; then
        if quick_health_check; then
            exit 0
        else
            exit 1
        fi
    else
        if perform_health_check; then
            echo ""
            echo "🎉 Service is healthy and ready to use!"
            echo ""
            echo "Test the debug tool with:"
            echo "python debug_tool/debug.py \"What is the system doing right now?\""
            exit 0
        else
            echo ""
            echo "❌ Service health check failed!"
            echo ""
            echo "Troubleshooting steps:"
            echo "1. Check if the service is running: docker-compose ps"
            echo "2. Check logs: docker-compose logs"
            echo "3. Restart the service: docker-compose restart"
            echo "4. Check firewall settings"
            exit 1
        fi
    fi
}

# Run main function
main