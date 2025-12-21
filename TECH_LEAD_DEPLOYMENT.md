# Vinsaraa Backend - Tech Lead Deployment Guide

Comprehensive reference for deploying, testing, and maintaining the production backend.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React/Next.js)                │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/HTTPS
┌────────────────────▼────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                    │
│              (SSL/TLS Termination)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│               Gunicorn (App Server)                         │
│                  (Worker Pool: 4-8)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐    ┌─────────▼──────────┐
│  PostgreSQL      │    │  Redis (Optional)  │
│  (Main Database) │    │  (Cache/Sessions)  │
└──────────────────┘    └────────────────────┘

Additional Services:
├─ Razorpay (Payment Gateway)
├─ Google OAuth (Authentication)
├─ Email Service (Django Email Backend)
└─ S3/Object Storage (Media Files - Optional)
```

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Server Setup](#server-setup)
4. [Database Configuration](#database-configuration)
5. [Application Deployment](#application-deployment)
6. [Reverse Proxy Configuration](#reverse-proxy-configuration)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Scaling Considerations](#scaling-considerations)

---

## System Requirements

### Recommended Server Specifications

**Development/Staging:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 50 GB SSD
- OS: Ubuntu 20.04 LTS or higher

**Production:**
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 100+ GB SSD
- OS: Ubuntu 22.04 LTS (recommended)
- Database: Separate instance (or managed service like AWS RDS)

### Software Requirements

```
Python: 3.10+
PostgreSQL: 13+
Nginx: 1.18+
Gunicorn: 20.1+
Redis: 6+ (optional, for caching)
Certbot: For SSL certificates
```

---

## Pre-Deployment Checklist

### Code Review & Testing

- [ ] All tests pass: `python manage.py test`
- [ ] No linting errors: `flake8` or `pylint` (optional setup)
- [ ] Security check: `python manage.py check --deploy`
- [ ] Database migrations reviewed and tested
- [ ] All environment variables documented
- [ ] API endpoints tested with Postman/Insomnia
- [ ] Third-party integrations verified (Razorpay, Google OAuth)

### Environment Configuration

- [ ] Generate secure `SECRET_KEY`
- [ ] Set `DEBUG = False`
- [ ] Configure database URL for PostgreSQL
- [ ] Update `ALLOWED_HOSTS` with production domains
- [ ] Set `CORS_ALLOWED_ORIGINS` to frontend domain only
- [ ] Configure Razorpay credentials (production keys)
- [ ] Configure Google OAuth credentials
- [ ] Set email backend (SendGrid, AWS SES, etc.)
- [ ] Configure logging system
- [ ] Set up monitoring alerts

### Infrastructure

- [ ] Domain name registered and DNS configured
- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] Server provisioned and hardened
- [ ] Firewall rules configured
- [ ] Database backup system in place
- [ ] Monitoring system configured

---

## Server Setup

### Initial System Configuration

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
    build-essential \
    python3.10 \
    python3.10-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    curl \
    wget \
    supervisor \
    redis-server

# Create application user
sudo useradd -m -s /bin/bash vinsaraa
sudo usermod -aG sudo vinsaraa

# Switch to app user
sudo su - vinsaraa

# Clone repository
git clone <repository-url> ~/vinsaraa
cd ~/vinsaraa/backend
```

### Virtual Environment Setup

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install production server
pip install gunicorn redis
```

---

## Database Configuration

### PostgreSQL Setup

```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE vinsaraa_db;
CREATE USER vinsaraa_user WITH PASSWORD 'strong_password_here';

-- Optimize settings for India timezone
ALTER ROLE vinsaraa_user SET client_encoding TO 'utf8';
ALTER ROLE vinsaraa_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE vinsaraa_user SET default_transaction_deferrable TO on;
ALTER ROLE vinsaraa_user SET timezone TO 'Asia/Kolkata';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE vinsaraa_db TO vinsaraa_user;

-- Exit psql
\q
```

### Performance Tuning

Edit `/etc/postgresql/14/main/postgresql.conf`:

```conf
# Connection settings
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 2GB
work_mem = 8MB
maintenance_work_mem = 64MB

# WAL settings (write-ahead log)
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql.log'
log_statement = 'all'  # Change to 'mod' in production
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Verify Connection

```bash
# Test connection
psql -U vinsaraa_user -d vinsaraa_db -h localhost

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

---

## Application Deployment

### Production Settings Configuration

Update `.env`:

```dotenv
DEBUG=False
SECRET_KEY=<generate-secure-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://vinsaraa_user:strong_password@localhost:5432/vinsaraa_db
RAZORPAY_KEY_ID=<production-key>
RAZORPAY_KEY_SECRET=<production-secret>
RAZORPAY_WEBHOOK_SECRET=<webhook-secret>
GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
SITE_URL=https://yourdomain.com
FRONTEND_URL=https://frontend-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Collect Static Files

```bash
cd ~/vinsaraa/backend
python manage.py collectstatic --noinput
```

### Create Gunicorn Service

Create `/etc/systemd/system/vinsaraa.service`:

```ini
[Unit]
Description=Vinsaraa Backend Service
After=network.target postgresql.service

[Service]
User=vinsaraa
WorkingDirectory=/home/vinsaraa/vinsaraa/backend
Environment="PATH=/home/vinsaraa/vinsaraa/backend/venv/bin"
Environment="DEBUG=False"
EnvironmentFile=/home/vinsaraa/vinsaraa/backend/.env
ExecStart=/home/vinsaraa/vinsaraa/backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/home/vinsaraa/vinsaraa/backend/vinsaraa.sock \
    --timeout 120 \
    --access-logfile /var/log/vinsaraa/access.log \
    --error-logfile /var/log/vinsaraa/error.log \
    core.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Start Service

```bash
# Create log directory
sudo mkdir -p /var/log/vinsaraa
sudo chown vinsaraa:vinsaraa /var/log/vinsaraa

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable vinsaraa
sudo systemctl start vinsaraa

# Check status
sudo systemctl status vinsaraa

# View logs
sudo tail -f /var/log/vinsaraa/error.log
```

---

## Reverse Proxy Configuration

### Nginx Configuration

Create `/etc/nginx/sites-available/vinsaraa`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss;
    gzip_vary on;
    
    # Client upload limit
    client_max_body_size 100M;
    
    # Static files
    location /static/ {
        alias /home/vinsaraa/vinsaraa/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /home/vinsaraa/vinsaraa/backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # API requests to Gunicorn
    location / {
        proxy_pass http://unix:/home/vinsaraa/vinsaraa/backend/vinsaraa.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Enable Site

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/vinsaraa /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## SSL/TLS Configuration

### Let's Encrypt Setup

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Manual renewal
sudo certbot renew
```

### SSL/TLS Best Practices

- Use TLS 1.2 or higher
- Implement HSTS (HTTP Strict Transport Security)
- Use modern ciphers
- Regular security audits

---

## Monitoring & Logging

### Application Logging

Update `core/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/vinsaraa/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Monitoring Tools

**Recommended:**
- Sentry (Error tracking)
- New Relic (Performance monitoring)
- Datadog (Comprehensive monitoring)
- Prometheus + Grafana (Self-hosted)

### System Monitoring

```bash
# Monitor service status
watch -n 5 'systemctl status vinsaraa'

# Monitor system resources
htop
vmstat 1
iotop

# Check logs
sudo journalctl -u vinsaraa -f  # Systemd logs
sudo tail -f /var/log/vinsaraa/error.log  # App logs
sudo tail -f /var/log/nginx/error.log  # Nginx logs
```

---

## Backup & Recovery

### Database Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

pg_dump -U vinsaraa_user vinsaraa_db | \
    gzip > $BACKUP_DIR/vinsaraa_db_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Add to crontab:
```bash
# Backup daily at 2 AM
0 2 * * * /home/vinsaraa/backup.sh
```

### Media Files Backup

```bash
# Backup media directory
tar -czf /backups/media_$(date +%Y%m%d).tar.gz \
    /home/vinsaraa/vinsaraa/backend/media/

# Upload to S3 (optional)
aws s3 cp /backups/media_*.tar.gz s3://your-bucket/backups/
```

### Recovery Procedure

```bash
# Restore database
gunzip -c /backups/vinsaraa_db_20231215_020000.sql.gz | \
    psql -U vinsaraa_user vinsaraa_db

# Restore media files
tar -xzf /backups/media_20231215.tar.gz -C /
```

---

## Scaling Considerations

### Horizontal Scaling

As traffic increases:

1. **Load Balancer:** Use nginx or HAProxy
2. **Multiple App Servers:** Run Gunicorn on multiple servers
3. **Database Replication:** Set up PostgreSQL replicas
4. **Cache Layer:** Implement Redis for sessions and caching

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize database indexes
- Implement query caching

### Performance Optimization

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Enable query optimization
DEBUG_PROPAGATE_EXCEPTIONS = True
CONN_MAX_AGE = 600  # Connection pooling
```

---

## Deployment Workflow

### CI/CD Integration (Example with GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run tests
        run: python manage.py test
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_IP }}
          username: vinsaraa
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd ~/vinsaraa/backend
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            python manage.py migrate
            python manage.py collectstatic --noinput
            sudo systemctl restart vinsaraa
```

---

## Health Checks & Alerts

### Add Health Check Endpoint

Create `core/views.py`:

```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Test database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy"})
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=500)
```

Add to `core/urls.py`:

```python
path("health/", health_check),
```

### Monitoring Script

```bash
#!/bin/bash
# Check every 5 minutes
while true; do
    RESPONSE=$(curl -s http://localhost/health/)
    if [[ $RESPONSE != *"healthy"* ]]; then
        # Send alert
        echo "System unhealthy!" | mail -s "Alert" admin@example.com
    fi
    sleep 300
done
```

---

## Rollback Procedure

In case of deployment issues:

```bash
# 1. Check git log
git log --oneline -n 10

# 2. Revert to previous commit
git revert HEAD
git push origin main

# 3. Stop current service
sudo systemctl stop vinsaraa

# 4. Pull previous version
git pull

# 5. Reinstall/revert database if needed
python manage.py migrate <previous-migration>

# 6. Restart service
sudo systemctl start vinsaraa

# 7. Verify
curl http://localhost/health/
```

---

## Security Hardening Checklist

- [ ] SSH key-based authentication only
- [ ] Firewall rules: Only ports 80, 443, 22 open
- [ ] Fail2ban for brute-force protection
- [ ] Regular security patches
- [ ] Database encryption at rest
- [ ] API rate limiting enabled
- [ ] CORS restricted to frontend domain
- [ ] Secrets in environment variables (not in code)
- [ ] Regular security audits
- [ ] Database access restricted to localhost

---

## Troubleshooting Production Issues

### Issue: High CPU/Memory Usage

```bash
# Find processes
top
ps aux | grep python

# Check specific metrics
systemctl status vinsaraa
journalctl -u vinsaraa -n 50
```

### Issue: Database Connection Errors

```bash
# Verify PostgreSQL running
sudo systemctl status postgresql

# Check connections
sudo -u postgres psql -c "SELECT datname, usename, count(*) FROM pg_stat_activity GROUP BY datname, usename;"
```

### Issue: SSL Certificate Expiring

```bash
# Check expiration
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal
```

---

## Support & Documentation

- Official Django Docs: https://docs.djangoproject.com/
- DRF Documentation: https://www.django-rest-framework.org/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Nginx Documentation: https://nginx.org/en/docs/

---

**Last Updated:** December 21, 2025
**Maintainer:** Tech Lead
**Version:** 1.0

