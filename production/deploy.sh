#!/usr/bin/env bash
"""
Production Deployment Automation Script
Production muhit uchun avtomatik deployment
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${ENVIRONMENT:-production}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-ghcr.io/orion-starline}"
KUBE_NAMESPACE="${KUBE_NAMESPACE:-orion-starline-prod}"
LOG_DIR="/workspace/orion-starline/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "${LOG_DIR}/deploy_${TIMESTAMP}.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "${LOG_DIR}/deploy_${TIMESTAMP}.log"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${LOG_DIR}/deploy_${TIMESTAMP}.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOG_DIR}/deploy_${TIMESTAMP}.log"
}

# Prerequisites check
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    local tools=("docker" "kubectl" "helm" "python3")
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed"
            exit 1
        fi
    done
    
    # Check environment variables
    local required_vars=(
        "SUPABASE_URL" "SUPABASE_ANON_KEY" "SUPABASE_SERVICE_ROLE_KEY"
        "STRIPE_SECRET_KEY" "STRIPE_PUBLISHABLE_KEY"
        "PAYPAL_CLIENT_ID" "PAYPAL_CLIENT_SECRET"
        "JWT_SECRET_KEY" "DATABASE_URL"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Environment variable $var is not set"
            exit 1
        fi
    done
    
    log_success "All prerequisites met"
}

# Database backup
backup_database() {
    log_info "Creating database backup..."
    
    local backup_dir="${LOG_DIR}/backups"
    mkdir -p "$backup_dir"
    
    local backup_file="${backup_dir}/db_backup_${TIMESTAMP}.sql"
    
    # Create backup
    if command -v pg_dump &> /dev/null; then
        PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump \
            -h "${POSTGRES_HOST:-localhost}" \
            -U "${POSTGRES_USER:-orion_starline}" \
            -d "${POSTGRES_DB:-orion_starline}" \
            -f "$backup_file"
        
        if [[ $? -eq 0 ]]; then
            log_success "Database backup created: $backup_file"
            
            # Upload to S3 (optional)
            if command -v aws &> /dev/null && [[ -n "${AWS_S3_BACKUP_BUCKET:-}" ]]; then
                aws s3 cp "$backup_file" "s3://${AWS_S3_BACKUP_BUCKET}/database/backups/"
                log_success "Backup uploaded to S3"
            fi
        else
            log_error "Database backup failed"
            return 1
        fi
    else
        log_warning "pg_dump not available, skipping database backup"
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build backend image
    log_info "Building backend image..."
    docker build -f Dockerfile.backend -t "${DOCKER_REGISTRY}/backend:latest" .
    
    if [[ $? -ne 0 ]]; then
        log_error "Backend image build failed"
        return 1
    fi
    
    # Build frontend image
    log_info "Building frontend image..."
    cd frontend
    docker build -f Dockerfile.frontend -t "${DOCKER_REGISTRY}/frontend:latest" .
    cd ..
    
    if [[ $? -ne 0 ]]; then
        log_error "Frontend image build failed"
        return 1
    fi
    
    log_success "Docker images built successfully"
}

# Push images to registry
push_images() {
    log_info "Pushing images to registry..."
    
    # Login to registry
    if [[ -n "${DOCKER_REGISTRY_TOKEN:-}" ]]; then
        echo "$DOCKER_REGISTRY_TOKEN" | docker login "${DOCKER_REGISTRY}" -u "${DOCKER_REGISTRY_USER:-}" --password-stdin
    else
        log_warning "No registry token provided, skipping login"
    fi
    
    # Tag images
    docker tag "${DOCKER_REGISTRY}/backend:latest" "${DOCKER_REGISTRY}/backend:${TIMESTAMP}"
    docker tag "${DOCKER_REGISTRY}/frontend:latest" "${DOCKER_REGISTRY}/frontend:${TIMESTAMP}"
    
    # Push images
    docker push "${DOCKER_REGISTRY}/backend:${TIMESTAMP}"
    docker push "${DOCKER_REGISTRY}/frontend:${TIMESTAMP}"
    
    if [[ $? -eq 0 ]]; then
        log_success "Images pushed successfully"
    else
        log_error "Image push failed"
        return 1
    fi
}

# Update image tags in Kubernetes
update_k8s_images() {
    log_info "Updating Kubernetes image tags..."
    
    # Create namespace if not exists
    kubectl create namespace "$KUBE_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply secrets
    kubectl apply -f production/kubernetes.secrets.yml -n "$KUBE_NAMESPACE"
    
    # Update image tags in deployment files
    sed -i.bak "s|:latest|:${TIMESTAMP}|g" production/kubernetes.deployment.yml
    
    # Apply Kubernetes manifests
    kubectl apply -f production/kubernetes.deployment.yml -n "$KUBE_NAMESPACE"
    kubectl apply -f production/kubernetes.services.yml -n "$KUBE_NAMESPACE"
    
    log_success "Kubernetes manifests applied"
}

# Wait for rollout
wait_for_rollout() {
    log_info "Waiting for deployments to roll out..."
    
    local deployments=("orion-backend" "orion-frontend")
    
    for deployment in "${deployments[@]}"; do
        log_info "Waiting for $deployment rollout..."
        
        if kubectl rollout status deployment/"$deployment" -n "$KUBE_NAMESPACE" --timeout=600s; then
            log_success "$deployment rollout completed"
        else
            log_error "$deployment rollout failed"
            return 1
        fi
    done
}

# Run health checks
health_check() {
    log_info "Running health checks..."
    
    # Check services
    local services=("orion-backend-service" "orion-frontend-service")
    
    for service in "${services[@]}"; do
        log_info "Checking $service..."
        
        local pod
        pod=$(kubectl get pods -n "$KUBE_NAMESPACE" -l "app=${service%-service}" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
        
        if [[ -z "$pod" ]]; then
            log_error "No pods found for $service"
            return 1
        fi
        
        # Check pod status
        local pod_status
        pod_status=$(kubectl get pod "$pod" -n "$KUBE_NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
        
        if [[ "$pod_status" == "Running" ]]; then
            log_success "$service is running"
        else
            log_error "$service is not running (status: $pod_status)"
            return 1
        fi
        
        # Check health endpoint
        sleep 10  # Give pods time to start
        
        if kubectl exec "$pod" -n "$KUBE_NAMESPACE" -- curl -f http://localhost:8000/health &>/dev/null; then
            log_success "$service health check passed"
        else
            log_error "$service health check failed"
            return 1
        fi
    done
}

# Run smoke tests
smoke_test() {
    log_info "Running smoke tests..."
    
    # Test API endpoints
    local endpoints=(
        "https://api.orion-starline.com/health"
        "https://api.orion-starline.com/api/v1/trading/status"
    )
    
    for endpoint in "${endpoints[@]}"; do
        log_info "Testing $endpoint..."
        
        if curl -f -s --max-time 30 "$endpoint" &>/dev/null; then
            log_success "$endpoint is responding"
        else
            log_error "$endpoint is not responding"
            return 1
        fi
    done
    
    # Test frontend
    if curl -f -s --max-time 30 "https://app.orion-starline.com" &>/dev/null; then
        log_success "Frontend is responding"
    else
        log_error "Frontend is not responding"
        return 1
    fi
}

# Rollback function
rollback() {
    log_error "Deployment failed, initiating rollback..."
    
    # Get previous image tag
    local previous_tag
    previous_tag=$(kubectl get deployment orion-backend -n "$KUBE_NAMESPACE" -o jsonpath='{.spec.template.spec.containers[0].image}' | sed 's/.*://')
    
    if [[ -n "$previous_tag" ]]; then
        log_info "Rolling back to previous image: $previous_tag"
        
        # Rollback deployments
        kubectl rollout undo deployment/orion-backend -n "$KUBE_NAMESPACE"
        kubectl rollout undo deployment/orion-frontend -n "$KUBE_NAMESPACE"
        
        # Wait for rollback to complete
        wait_for_rollout
        
        log_success "Rollback completed"
    else
        log_error "No previous deployment found for rollback"
        return 1
    fi
}

# Monitoring setup
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Deploy Prometheus
    kubectl apply -f production/monitoring/prometheus.yml -n "$KUBE_NAMESPACE"
    
    # Deploy Grafana
    kubectl apply -f production/monitoring/grafana.yml -n "$KUBE_NAMESPACE"
    
    # Deploy AlertManager
    kubectl apply -f production/monitoring/alertmanager.yml -n "$KUBE_NAMESPACE"
    
    log_success "Monitoring setup completed"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    
    # Remove temporary files
    find . -name "*.bak" -delete
    find . -name "*.log.*" -mtime +7 -delete
    
    # Clean up unused Docker images
    if command -v docker &> /dev/null; then
        docker system prune -f &>/dev/null || true
    fi
    
    log_success "Cleanup completed"
}

# Send notification
send_notification() {
    local status="$1"
    local message="$2"
    
    # Slack notification (if webhook is configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        local payload
        payload=$(cat <<EOF
{
    "text": "Deployment Notification",
    "attachments": [
        {
            "color": "$([[ "$status" == "success" ]] && echo "good" || echo "danger")",
            "fields": [
                {
                    "title": "Environment",
                    "value": "$ENVIRONMENT",
                    "short": true
                },
                {
                    "title": "Status",
                    "value": "$status",
                    "short": true
                },
                {
                    "title": "Message",
                    "value": "$message",
                    "short": false
                }
            ]
        }
    ]
}
EOF
)
        
        curl -X POST -H 'Content-type: application/json' \
            --data "$payload" \
            "$SLACK_WEBHOOK_URL" &>/dev/null || true
    fi
    
    # Email notification (if SMTP is configured)
    if [[ -n "${SMTP_HOST:-}" ]] && [[ -n "${NOTIFICATION_EMAIL:-}" ]]; then
        echo "Deployment $status: $message" | mail -s "Orion Starline Deployment" "$NOTIFICATION_EMAIL" || true
    fi
}

# Main deployment function
main() {
    log_info "Starting production deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Timestamp: $TIMESTAMP"
    
    # Trap for cleanup on exit
    trap cleanup EXIT
    
    # Check prerequisites
    check_prerequisites || exit 1
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Run pre-deployment steps
    backup_database || log_warning "Database backup failed"
    
    # Deploy
    if build_images && push_images && update_k8s_images; then
        if wait_for_rollout && health_check && smoke_test; then
            log_success "Deployment completed successfully!"
            send_notification "success" "Deployment completed successfully in $ENVIRONMENT"
            exit 0
        else
            log_error "Post-deployment checks failed"
            rollback
            send_notification "failure" "Deployment failed in $ENVIRONMENT"
            exit 1
        fi
    else
        log_error "Deployment pipeline failed"
        send_notification "failure" "Deployment pipeline failed in $ENVIRONMENT"
        exit 1
    fi
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health-check")
        health_check
        ;;
    "backup")
        backup_database
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health-check|backup|cleanup}"
        exit 1
        ;;
esac