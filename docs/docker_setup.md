# Docker Setup Guide

Complete guide for deploying and configuring Universal Time Tracker with Docker.

## Quick Setup

### Prerequisites
- Docker 20.0+
- Docker Compose 1.27+
- 2GB available RAM
- 1GB available disk space

### Basic Deployment
```bash
# Clone the repository
git clone https://github.com/your-org/universal-time-tracker.git
cd universal-time-tracker

# Start the service
docker-compose up -d

# Verify it's running
docker-compose ps
curl http://localhost:9000/health
```

## Docker Configuration

### Docker Compose File

```yaml
version: '3.8'

services:
  time-tracker:
    build: ./server
    container_name: universal-time-tracker
    ports:
      - "9000:9000"
    volumes:
      # Persistent data storage
      - ./data:/app/data
      # Optional: Custom configuration
      - ./config:/app/config
    environment:
      - PORT=9000
      - DEBUG=false
      - DATABASE_PATH=/app/data/timetracker.db
      - TZ=America/New_York
    restart: unless-stopped
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:9000/health" ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  time-tracker-data:
    driver: local
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:9000/health || exit 1

# Run the application
CMD ["python", "src/app.py"]
```

## Environment Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `9000` | Server port |
| `DEBUG` | `false` | Enable debug mode |
| `DATABASE_PATH` | `/app/data/timetracker.db` | SQLite database path |
| `TZ` | `UTC` | Container timezone |
| `MAX_WORKERS` | `4` | Gunicorn worker processes |
| `WORKER_TIMEOUT` | `30` | Worker timeout seconds |
| `LOG_LEVEL` | `INFO` | Logging level |

### Production Environment

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  time-tracker:
    build: ./server
    container_name: time-tracker-prod
    ports:
      - "9000:9000"
    volumes:
      - time-tracker-data:/app/data
      - ./logs:/app/logs
    environment:
      - PORT=9000
      - DEBUG=false
      - DATABASE_PATH=/app/data/timetracker.db
      - TZ=America/New_York
      - MAX_WORKERS=8
      - WORKER_TIMEOUT=60
      - LOG_LEVEL=WARNING
    restart: always
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:9000/health" ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'

  # Optional: Reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - time-tracker
    restart: always

volumes:
  time-tracker-data:
    driver: local
```

## Data Persistence

### Volume Configuration

**Local Development:**
```yaml
volumes:
  - ./data:/app/data  # Bind mount for easy access
```

**Production:**
```yaml
volumes:
  - time-tracker-data:/app/data  # Named volume for persistence
```

### Backup Strategy

```bash
# Create backup
docker run --rm \
  -v universal-time-tracker_time-tracker-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/timetracker-backup-$(date +%Y%m%d).tar.gz /data

# Restore backup
docker run --rm \
  -v universal-time-tracker_time-tracker-data:/data \
  -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/timetracker-backup-20250623.tar.gz --strip 1"
```

### Database Migration

```bash
# Export data
docker exec universal-time-tracker sqlite3 /app/data/timetracker.db .dump > backup.sql

# Import to new database
docker exec -i universal-time-tracker sqlite3 /app/data/timetracker_new.db < backup.sql
```

## Networking & Security

### Network Configuration

```yaml
# docker-compose.yml with custom network
version: '3.8'

services:
  time-tracker:
    build: ./server
    networks:
      - time-tracker-network
    # ... other configuration

networks:
  time-tracker-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Security Best Practices

**Container Security:**
```dockerfile
# Use non-root user
FROM python:3.11-slim

RUN groupadd -r timetracker && useradd -r -g timetracker timetracker
USER timetracker

# Set secure permissions
COPY --chown=timetracker:timetracker src/ ./src/
RUN chmod -R 755 /app/src
```

**Environment Security:**
```yaml
services:
  time-tracker:
    environment:
      - SECRET_KEY_FILE=/run/secrets/secret_key
    secrets:
      - secret_key

secrets:
  secret_key:
    file: ./secrets/secret_key.txt
```

### SSL/TLS Configuration

**Nginx Reverse Proxy:**
```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://time-tracker:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring & Logging

### Health Checks

```yaml
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:9000/health" ]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Logging Configuration

```yaml
services:
  time-tracker:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Centralized Logging:**
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  time-tracker:
    logging:
      driver: "gelf"
      options:
        gelf-address: "udp://localhost:12201"
        tag: "time-tracker"

  logspout:
    image: gliderlabs/logspout
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "8000:80"
    environment:
      - ROUTE_URIS=logstash://logstash:5000
```

### Metrics Collection

```yaml
# Add Prometheus metrics
services:
  time-tracker:
    environment:
      - ENABLE_METRICS=true
      - METRICS_PORT=9090
    ports:
      - "9000:9000"
      - "9090:9090"  # Metrics endpoint

  prometheus:
    image: prom/prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## Scaling & Performance

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  time-tracker:
    build: ./server
    deploy:
      replicas: 3
    environment:
      - DATABASE_PATH=/app/data/timetracker.db
    volumes:
      - time-tracker-data:/app/data

  load-balancer:
    image: nginx:alpine
    ports:
      - "9000:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
    depends_on:
      - time-tracker
```

**Load Balancer Configuration:**
```nginx
# nginx-lb.conf
upstream time-tracker-backend {
    server time-tracker_time-tracker_1:9000;
    server time-tracker_time-tracker_2:9000;
    server time-tracker_time-tracker_3:9000;
}

server {
    listen 80;
    location / {
        proxy_pass http://time-tracker-backend;
    }
}
```

### Performance Optimization

```yaml
services:
  time-tracker:
    environment:
      - MAX_WORKERS=8
      - WORKER_TIMEOUT=60
      - WORKER_CLASS=gevent
      - WORKER_CONNECTIONS=1000
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
```

## Development Setup

### Development Environment

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  time-tracker-dev:
    build: 
      context: ./server
      dockerfile: Dockerfile.dev
    volumes:
      - ./server/src:/app/src  # Live code reload
      - ./data:/app/data
    ports:
      - "9000:9000"
      - "5678:5678"  # Debug port
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - FLASK_ENV=development
    command: ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "src/app.py"]
```

**Development Dockerfile:**
```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install development dependencies
COPY requirements.dev.txt .
RUN pip install --no-cache-dir -r requirements.dev.txt

# Install debugpy for debugging
RUN pip install debugpy

# Copy source code (will be overridden by volume)
COPY src/ ./src/

EXPOSE 9000 5678

CMD ["python", "src/app.py"]
```

### Hot Reload Setup

```python
# src/app.py development configuration
if os.environ.get('DEBUG') == 'true':
    app.run(host='0.0.0.0', port=9000, debug=True, use_reloader=True)
else:
    app.run(host='0.0.0.0', port=9000, debug=False)
```

## Deployment Strategies

### Single Server Deployment

```bash
# Production deployment script
#!/bin/bash

# Pull latest changes
git pull origin main

# Build and start services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Wait for health check
sleep 30

# Verify deployment
curl -f http://localhost:9000/health || exit 1

echo "Deployment successful!"
```

### Multi-Environment Setup

```bash
# Environment-specific deployments
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d     # Development
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d # Staging  
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d    # Production
```

### CI/CD Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy Time Tracker

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      run: |
        docker-compose build
        docker-compose up -d
        
    - name: Health check
      run: |
        sleep 30
        curl -f http://localhost:9000/health
```

## Troubleshooting

### Common Issues

**Container Won't Start:**
```bash
# Check logs
docker-compose logs time-tracker

# Check container status
docker-compose ps

# Restart services
docker-compose restart time-tracker
```

**Database Issues:**
```bash
# Check database file permissions
docker exec time-tracker ls -la /app/data/

# Reset database
docker exec time-tracker rm /app/data/timetracker.db
docker-compose restart time-tracker
```

**Port Conflicts:**
```bash
# Check port usage
lsof -i :9000

# Use different port
docker-compose up -d --scale time-tracker=0
docker-compose -f docker-compose.yml up -d
```

**Memory Issues:**
```bash
# Check container memory usage
docker stats time-tracker

# Increase memory limit
docker-compose -f docker-compose.yml up -d --scale time-tracker=1 --memory=2g
```

### Performance Debugging

```bash
# Monitor container performance
docker stats --no-stream

# Check application logs
docker-compose logs -f time-tracker

# Profile database queries
docker exec time-tracker sqlite3 /app/data/timetracker.db ".stats on"
```

### Maintenance Tasks

```bash
# Update container
docker-compose pull
docker-compose up -d

# Clean up old images
docker image prune -f

# Backup before maintenance
./scripts/backup.sh

# Database maintenance
docker exec time-tracker sqlite3 /app/data/timetracker.db "VACUUM;"
```
