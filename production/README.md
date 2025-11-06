# Production Deployment System

Orion Starline uchun to'liq production-ready deployment tizimi. Bu tizim real user accounts, payment integration, monitoring, load testing va automated deployment funksiyalarini qo'llab-quvvatlaydi.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React/Vite)  │────│   (FastAPI)     │────│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Redis Cache   │    │   File Storage  │
│   (Nginx)       │    │   Port: 6379    │    │   (MinIO/S3)    │
│   Ports: 80/443 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN           │    │   Monitoring    │    │   Payment       │
│   (CloudFlare)  │    │   Stack         │    │   Gateways      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Alerting      │
                    │   System        │
                    │                 │
                    └─────────────────┘
```

## 🚀 Quick Start

### 1. Environment Variables

Production environment uchun quyidagi environment variables ni sozlang:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Payment Integration
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret

# Security
JWT_SECRET_KEY=your-jwt-secret-key
SESSION_SECRET_KEY=your-session-secret

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
POSTGRES_DB=orion_starline
POSTGRES_USER=orion_starline
POSTGRES_PASSWORD=secure-password

# Cache
REDIS_PASSWORD=redis-password

# Monitoring
GRAFANA_PASSWORD=grafana-password
PROMETHEUS_URL=http://prometheus:9090
ALERTMANAGER_URL=http://alertmanager:9093

# Notifications
SMTP_HOST=smtp.gmail.com
SMTP_USER=alerts@orion-starline.com
SMTP_PASSWORD=smtp-password
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

### 2. Automated Deployment

```bash
# Make script executable
chmod +x production/deploy.sh

# Deploy to production
./production/deploy.sh

# Or with specific environment
ENVIRONMENT=staging ./production/deploy.sh
```

### 3. Manual Deployment

```bash
# 1. Build and push images
docker-compose -f production/docker-compose.production.yml build
docker push ghcr.io/orion-starline/backend:latest
docker push ghcr.io/orion-starline/frontend:latest

# 2. Deploy to Kubernetes
kubectl apply -f production/kubernetes.deployment.yml
kubectl apply -f production/kubernetes.services.yml

# 3. Check deployment status
kubectl get pods -n orion-starline-prod
kubectl logs -f deployment/orion-backend -n orion-starline-prod
```

## 📦 Components

### 1. Core Application

#### Backend (FastAPI)
- **Port**: 8000
- **Health Check**: `/health`
- **API Docs**: `/docs`
- **Metrics**: `/metrics`

#### Frontend (React/Vite)
- **Port**: 3000
- **Build**: Production optimized
- **CDN**: CloudFlare integration

### 2. Data Layer

#### PostgreSQL Database
```sql
-- Key tables
users                  -- User accounts
payments              -- Payment records
subscriptions         -- Subscription data
trading_signals       -- Trading signals
audit_logs           -- Security audit
```

#### Redis Cache
- Session storage
- Rate limiting
- Temporary data
- Real-time features

### 3. Payment Integration

#### Stripe Integration
```python
from production.payment_integration import ProductionPaymentSystem

payment = ProductionPaymentSystem()
result = payment.process_payment(
    user_id=123,
    amount=29.99,
    payment_method="stripe",
    payment_type="subscription",
    plan_id="basic"
)
```

#### PayPal Integration
```python
result = payment.process_payment(
    user_id=123,
    amount=29.99,
    payment_method="paypal",
    payment_type="one_time",
    plan_id="basic"
)
```

### 4. Monitoring Stack

#### Prometheus Metrics
```python
from production.monitoring import ProductionMonitoring

monitoring = ProductionMonitoring()
metrics = monitoring.get_dashboard_data()
```

#### Grafana Dashboards
- **URL**: https://admin.orion-starline.com/grafana
- **User**: admin
- **Password**: (from environment)

#### AlertManager
- Email notifications
- Slack integration
- PagerDuty support

### 5. User Onboarding System

#### Automated Onboarding
```python
from production.onboarding import ProductionOnboardingSystem

onboarding = ProductionOnboardingSystem()

# Create user
success, message, user_id = onboarding.create_user({
    "email": "user@example.com",
    "password": "secure-password",
    "first_name": "John",
    "last_name": "Doe",
    "country": "Uzbekistan"
})

# Get onboarding steps
steps = onboarding.get_onboarding_steps(user_id)
```

#### Course Progress Tracking
- Interactive tutorials
- Video lessons
- Quiz assessments
- Certificate generation

## 🔧 Configuration

### Production Config (`production_config.py`)

```python
from production_config import ProductionConfig

config = ProductionConfig()

# Database settings
config.DATABASE_POOL_SIZE = 20
config.DATABASE_TIMEOUT = 30

# Security settings
config.REQUIRE_EMAIL_VERIFICATION = True
config.MAX_LOGIN_ATTEMPTS = 5

# Performance settings
config.RATE_LIMIT_REQUESTS = 100
config.RATE_LIMIT_WINDOW = 60
```

### Kubernetes Settings

```yaml
# Resources
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 4Gi

# Auto-scaling
autoscaling:
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## 📊 Monitoring & Observability

### Real-time Metrics

1. **Application Metrics**
   - Request rate
   - Response times
   - Error rates
   - Active users

2. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

3. **Business Metrics**
   - Payment success rate
   - User registrations
   - Trading activity
   - Revenue metrics

### Alert Rules

```yaml
- alert: HighResponseTime
  expr: avg(http_request_duration_seconds) > 0.5
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High response time detected"
```

## 🧪 Load Testing

### Run Load Tests

```bash
# Install dependencies
pip install aiohttp asyncio

# Basic load test
python production/load_testing.py \
  --test-type load \
  --users 100 \
  --duration 30 \
  --endpoints "/health" "/api/v1/trading/status"

# Stress test
python production/load_testing.py \
  --test-type stress \
  --users 1000

# Spike test
python production/load_testing.py \
  --test-type spike \
  --users 50
```

### Performance Targets

| Metric | Target | Critical |
|--------|---------|----------|
| Response Time (avg) | < 1s | < 2s |
| Response Time (p95) | < 2s | < 5s |
| Success Rate | > 99% | > 95% |
| Throughput | > 100 req/s | > 50 req/s |
| Error Rate | < 1% | < 5% |

## 🔒 Security

### SSL/TLS Configuration
- Let's Encrypt certificates
- HTTP/2 support
- Perfect Forward Secrecy
- Security headers

### Authentication
- JWT tokens
- Session management
- Rate limiting
- IP whitelisting

### Data Protection
- Encryption at rest
- Encryption in transit
- PII data masking
- Audit logging

## 🚨 Disaster Recovery

### Backup Strategy
```bash
# Database backup
./production/deploy.sh backup

# Automated backups
0 2 * * * /workspace/orion-starline/production/deploy.sh backup
```

### Rollback Procedure
```bash
# Automatic rollback on failure
./production/deploy.sh rollback

# Manual rollback
kubectl rollout undo deployment/orion-backend -n orion-starline-prod
```

### Recovery Time Objectives
- **RTO**: 30 minutes
- **RPO**: 1 hour
- **Availability**: 99.9%

## 📈 Scaling

### Horizontal Scaling
- Auto-scaling based on CPU/memory
- Load balancing with Nginx
- Database read replicas

### Vertical Scaling
- Resource limits and requests
- Pod priority classes
- Resource quotas

### Database Scaling
- Connection pooling
- Query optimization
- Index management

## 🛠️ Maintenance

### Regular Tasks

1. **Daily**
   - Monitor error rates
   - Check disk usage
   - Review alerts

2. **Weekly**
   - Update dependencies
   - Security patches
   - Performance review

3. **Monthly**
   - Capacity planning
   - Security audit
   - Backup validation

### Update Procedure
```bash
# 1. Create backup
./production/deploy.sh backup

# 2. Deploy updates
./production/deploy.sh deploy

# 3. Verify deployment
./production/deploy.sh health-check

# 4. Monitor for issues
kubectl logs -f deployment/orion-backend -n orion-starline-prod
```

## 🚀 CI/CD Pipeline

### GitHub Actions
```yaml
name: Production Deploy
on:
  push:
    branches: [main]
    
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Production
        run: ./production/deploy.sh
        env:
          ENVIRONMENT: production
```

### Pre-deployment Checks
- Unit tests
- Integration tests
- Security scanning
- Performance testing

## 📝 Logging

### Log Structure
```
/workspace/orion-starline/logs/
├── deploy_YYYYMMDD_HHMMSS.log
├── monitoring.log
├── payment.log
├── onboarding.log
└── access.log
```

### Log Levels
- **INFO**: General information
- **WARNING**: Potential issues
- **ERROR**: Errors requiring attention
- **DEBUG**: Detailed debugging info

## 🔍 Troubleshooting

### Common Issues

1. **Pod Startup Failures**
   ```bash
   kubectl describe pod <pod-name> -n orion-starline-prod
   kubectl logs <pod-name> -n orion-starline-prod
   ```

2. **Database Connection Issues**
   ```bash
   kubectl exec -it <pod-name> -n orion-starline-prod -- psql -U orion_starline
   ```

3. **High Memory Usage**
   ```bash
   kubectl top pods -n orion-starline-prod
   ```

4. **Payment Integration Issues**
   ```bash
   # Check webhook logs
   tail -f /workspace/orion-starline/logs/payment.log
   ```

### Health Check Endpoints
- Backend: `https://api.orion-starline.com/health`
- Database: `https://api.orion-starline.com/health/database`
- Redis: `https://api.orion-starline.com/health/cache`

## 📞 Support

### Contact Information
- **Email**: admin@orion-starline.com
- **Slack**: #orion-starline-support
- **PagerDuty**: [contact admin]

### Documentation
- [API Documentation](https://api.orion-starline.com/docs)
- [User Guide](https://docs.orion-starline.com)
- [Troubleshooting Guide](https://docs.orion-starline.com/troubleshooting)

---

## 🎯 Success Metrics

- **Uptime**: 99.9%
- **Response Time**: < 1s average
- **Error Rate**: < 1%
- **User Satisfaction**: > 4.5/5
- **Security Score**: A+

Bu production deployment tizimi Orion Starline uchun enterprise-grade, scalable va secure deployment yechimini ta'minlaydi.