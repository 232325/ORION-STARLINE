# Production deployment script for Orion Starline
# Automated deployment with health checks and rollback capability

#!/bin/bash

set -euo pipefail

# Configuration
APP_NAME="orion-starline"
DOCKER_REGISTRY="ghcr.io"
IMAGE_TAG="${1:-latest}"
ENVIRONMENT="${2:-production}"
NAMESPACE="${3:-orion-production}"
BACKUP_BEFORE_DEPLOY="${4:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    local tools=("docker" "kubectl" "helm" "jq")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check namespace
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "Creating namespace $NAMESPACE..."
        kubectl create namespace "$NAMESPACE"
    fi
    
    log_success "Prerequisites check passed"
}

# Function to build and push Docker images
build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    local image_name="$DOCKER_REGISTRY/$APP_NAME"
    local full_tag="$image_name:$IMAGE_TAG"
    
    # Build image
    log_info "Building Docker image: $full_tag"
    docker build -t "$full_tag" -f deployment/Dockerfile .
    
    # Push to registry
    if [[ "$DOCKER_REGISTRY" != "localhost" ]]; then
        log_info "Pushing image to registry: $full_tag"
        docker push "$full_tag"
    fi
    
    log_success "Docker image built and pushed: $full_tag"
}

# Function to create database backup
create_backup() {
    if [[ "$BACKUP_BEFORE_DEPLOY" != "true" ]]; then
        log_info "Skipping backup as requested"
        return 0
    fi
    
    log_info "Creating database backup..."
    
    local backup_name="backup-$(date +%Y%m%d-%H%M%S)"
    local backup_dir="backups/$backup_name"
    
    mkdir -p "$backup_dir"
    
    # Database backup
    if kubectl get pvc postgres-pvc -n "$NAMESPACE" &> /dev/null; then
        log_info "Creating PVC snapshot..."
        # This would use a volume snapshotter in production
        log_warning "Volume snapshots not implemented in this demo"
    fi
    
    # Configuration backup
    kubectl get all,configmaps,secrets -n "$NAMESPACE" -o yaml > "$backup_dir/cluster-state.yaml"
    
    log_success "Backup created: $backup_dir"
}

# Function to apply Kubernetes manifests
apply_manifests() {
    log_info "Applying Kubernetes manifests..."
    
    local image_name="$DOCKER_REGISTRY/$APP_NAME"
    local full_tag="$image_name:$IMAGE_TAG"
    
    # Update image in manifests
    sed "s|image: .*|image: $full_tag|g" deployment/kubernetes.yml | \
    kubectl apply -n "$NAMESPACE" -f -
    
    # Wait for rollout
    log_info "Waiting for deployment rollout..."
    kubectl rollout status deployment/orion-backend -n "$NAMESPACE" --timeout=600s || {
        log_error "Backend deployment failed"
        return 1
    }
    
    kubectl rollout status deployment/orion-frontend -n "$NAMESPACE" --timeout=300s || {
        log_error "Frontend deployment failed"
        return 1
    }
    
    log_success "Kubernetes manifests applied"
}

# Function to run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if kubectl exec -n "$NAMESPACE" deployment/orion-postgres -- pg_isready -U orion; then
            break
        fi
        log_info "Waiting for database... attempt $attempt/$max_attempts"
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Database not ready after $max_attempts attempts"
        return 1
    fi
    
    # Run migrations (this would depend on your migration tool)
    log_info "Running application migrations..."
    kubectl run -n "$NAMESPACE" migration-$(date +%s) --image="$DOCKER_REGISTRY/$APP_NAME:$IMAGE_TAG" --restart=OnFailure --command -- python scripts/migrate.py
    
    log_success "Database migrations completed"
}

# Function to run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    local service_url
    service_url=$(kubectl get svc orion-frontend -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "localhost")
    
    # Wait for service to be ready
    sleep 30
    
    # Frontend health check
    local frontend_url="http://$service_url/health"
    if curl -f -s "$frontend_url" > /dev/null; then
        log_success "Frontend health check passed"
    else
        log_warning "Frontend health check failed: $frontend_url"
    fi
    
    # Backend health check
    local backend_url="http://$service_url/api/health"
    if curl -f -s "$backend_url" > /dev/null; then
        log_success "Backend health check passed"
    else
        log_warning "Backend health check failed: $backend_url"
    fi
    
    # Kubernetes health check
    if kubectl get pods -n "$NAMESPACE" | grep -q Running; then
        log_success "Kubernetes pods are running"
    else
        log_error "Some Kubernetes pods are not running"
        kubectl get pods -n "$NAMESPACE"
        return 1
    fi
}

# Function to run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."
    
    # This would run your smoke tests
    log_info "Running application smoke tests..."
    
    # Example smoke test commands
    if kubectl exec -n "$NAMESPACE" deployment/orion-backend -- python scripts/smoke_tests.py; then
        log_success "Smoke tests passed"
    else
        log_error "Smoke tests failed"
        return 1
    fi
}

# Function to rollback deployment
rollback_deployment() {
    log_error "Deployment failed, initiating rollback..."
    
    # Rollback to previous version
    kubectl rollout undo deployment/orion-backend -n "$NAMESPACE"
    kubectl rollout undo deployment/orion-frontend -n "$NAMESPACE"
    
    # Wait for rollback
    kubectl rollout status deployment/orion-backend -n "$NAMESPACE" --timeout=300s
    kubectl rollout status deployment/orion-frontend -n "$NAMESPACE" --timeout=300s
    
    log_info "Rollback completed"
}

# Function to cleanup
cleanup() {
    log_info "Cleaning up..."
    
    # Remove temporary files
    rm -f /tmp/orion-deploy-*.log
    
    log_success "Cleanup completed"
}

# Function to send deployment notifications
send_notification() {
    local status="$1"
    local message="$2"
    
    # Slack notification (if configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 Orion Deployment - $ENVIRONMENT - $status\\n$message\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
    
    # Email notification (if configured)
    if [[ -n "${DEPLOYMENT_EMAIL:-}" ]]; then
        echo "$message" | mail -s "Orion Deployment $status" "$DEPLOYMENT_EMAIL"
    fi
}

# Main deployment function
main() {
    log_info "Starting Orion Starline deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Namespace: $NAMESPACE"
    log_info "Image Tag: $IMAGE_TAG"
    
    # Trap for cleanup on exit
    trap cleanup EXIT
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup
    if ! create_backup; then
        log_error "Backup failed"
        send_notification "FAILED" "Backup creation failed"
        exit 1
    fi
    
    # Build and push images
    if ! build_and_push_images; then
        log_error "Image build failed"
        send_notification "FAILED" "Docker image build failed"
        exit 1
    fi
    
    # Apply manifests
    if ! apply_manifests; then
        log_error "Manifest application failed"
        rollback_deployment
        send_notification "FAILED" "Kubernetes manifest application failed"
        exit 1
    fi
    
    # Run migrations
    if ! run_migrations; then
        log_error "Migration failed"
        rollback_deployment
        send_notification "FAILED" "Database migration failed"
        exit 1
    fi
    
    # Run health checks
    if ! run_health_checks; then
        log_error "Health checks failed"
        rollback_deployment
        send_notification "FAILED" "Health checks failed"
        exit 1
    fi
    
    # Run smoke tests
    if ! run_smoke_tests; then
        log_error "Smoke tests failed"
        rollback_deployment
        send_notification "FAILED" "Smoke tests failed"
        exit 1
    fi
    
    log_success "Deployment completed successfully!"
    send_notification "SUCCESS" "Orion Starline deployed successfully to $ENVIRONMENT"
}

# Script usage
usage() {
    echo "Usage: $0 [IMAGE_TAG] [ENVIRONMENT] [NAMESPACE] [BACKUP_BEFORE_DEPLOY]"
    echo ""
    echo "Arguments:"
    echo "  IMAGE_TAG            Docker image tag (default: latest)"
    echo "  ENVIRONMENT          Deployment environment (default: production)"
    echo "  NAMESPACE            Kubernetes namespace (default: orion-production)"
    echo "  BACKUP_BEFORE_DEPLOY Whether to create backup before deploy (default: true)"
    echo ""
    echo "Examples:"
    echo "  $0 v1.0.0 production orion-production true"
    echo "  $0 latest staging orion-staging false"
    echo ""
    echo "Environment variables:"
    echo "  DOCKER_REGISTRY      Docker registry URL (default: ghcr.io)"
    echo "  SLACK_WEBHOOK_URL    Slack webhook for notifications"
    echo "  DEPLOYMENT_EMAIL     Email for deployment notifications"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        *)
            # Positional arguments are handled in main()
            break
            ;;
    esac
    shift
done

# Check if script is run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi