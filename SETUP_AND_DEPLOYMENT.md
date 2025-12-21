# Vinsaraa Backend - Setup & Deployment Guide

This guide provides complete instructions for setting up, testing, and deploying the Vinsaraa Django REST API backend.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Initial Setup](#initial-setup)
4. [Running Locally](#running-locally)
5. [Switching to PostgreSQL](#switching-to-postgresql)
6. [Environment Configuration](#environment-configuration)
7. [Database Migrations](#database-migrations)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Stack:**
- **Framework:** Django 5.2.9 with Django REST Framework 3.16.1
- **Authentication:** JWT (SimpleJWT) + Google OAuth (django-allauth)
- **Payment Gateway:** Razorpay
- **Admin Interface:** Jazzmin (enhanced Django admin)
- **Database:** SQLite (default) or PostgreSQL (recommended for production)

**Key Apps:**
- `accounts` - User authentication & profiles
- `store` - Products, categories, inventory
- `orders` - Order management & order items
- `payments` - Razorpay payment integration
- `web_content` - Hero slides, videos, promotional content

---

## Prerequisites

### System Requirements
- **Python:** 3.8 or higher (3.10+ recommended)
- **Git:** Latest version
- **Database:** PostgreSQL 12+ (for production) or SQLite (for development)
- **Virtual Environment:** Python `venv` or `virtualenv`

### Required Accounts (for production)
- **Razorpay:** API Key & Secret
- **Google OAuth:** Client ID & Client Secret (for Google login)

---

## Initial Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd vinsaraa/backend
```

### 2. Create a Python Virtual Environment

**On Windows (PowerShell/CMD):**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```dotenv
# --- CORE DJANGO SETTINGS ---
DEBUG=True
SECRET_KEY=your-very-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# --- DATABASE (SQLite for now, PostgreSQL instructions below) ---
DATABASE_URL=sqlite:///db.sqlite3

# --- RAZORPAY (Add your credentials) ---
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# --- GOOGLE OAUTH (Add your credentials) ---
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret

# --- SITE URLS ---
SITE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser Account
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account with email and password.

### 7. Collect Static Files (if needed)
```bash
python manage.py collectstatic --noinput
```

---

## Running Locally

### Start Development Server
```bash
python manage.py runserver
```

The server will start at `http://localhost:8000`

### Access Points
- **API Root:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/
- **Auth APIs:** http://localhost:8000/api/auth/
- **Store APIs:** http://localhost:8000/api/store/
- **Orders APIs:** http://localhost:8000/api/orders/
- **Payments APIs:** http://localhost:8000/api/payments/
- **Content APIs:** http://localhost:8000/api/content/

---

## Switching to PostgreSQL

PostgreSQL is **highly recommended** for production environments.

### Step 1: Install PostgreSQL

**On Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Run the installer and remember the password for the `postgres` superuser

**On macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 2: Create Database & User

```bash
# Connect to PostgreSQL
psql -U postgres

# Inside psql shell:
CREATE DATABASE vinsaraa_db;
CREATE USER vinsaraa_user WITH PASSWORD 'your_secure_password';
ALTER ROLE vinsaraa_user SET client_encoding TO 'utf8';
ALTER ROLE vinsaraa_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE vinsaraa_user SET default_transaction_deferrable TO on;
ALTER ROLE vinsaraa_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE vinsaraa_db TO vinsaraa_user;
\q
```

### Step 3: Install PostgreSQL Adapter for Django

```bash
pip install psycopg2-binary
pip freeze > requirements.txt  # Update requirements.txt
```

### Step 4: Update `.env` Configuration

```dotenv
# Change database configuration
DATABASE_URL=postgresql://vinsaraa_user:your_secure_password@localhost:5432/vinsaraa_db
```

### Step 5: Update `core/settings.py`

Modify the `DATABASES` section to use environment variable:

```python
import dj_database_url

# In core/settings.py, replace the DATABASES section:
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

Install the required package:
```bash
pip install dj-database-url
pip freeze > requirements.txt
```

### Step 6: Run Migrations on PostgreSQL

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Step 7: Test PostgreSQL Connection

```bash
python manage.py dbshell
```

If the connection opens, PostgreSQL is properly configured.

---

## Environment Configuration

### Required Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `DEBUG` | Development mode flag | `True` (dev), `False` (prod) |
| `SECRET_KEY` | Django secret key | Generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| `ALLOWED_HOSTS` | Allowed domain hosts | `localhost,127.0.0.1,yourdomain.com` |
| `DATABASE_URL` | Database connection string | SQLite or PostgreSQL URL |
| `RAZORPAY_KEY_ID` | Razorpay public key | From Razorpay Dashboard |
| `RAZORPAY_KEY_SECRET` | Razorpay secret key | From Razorpay Dashboard |
| `RAZORPAY_WEBHOOK_SECRET` | Razorpay webhook secret | From Razorpay Dashboard |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | From Google Cloud Console |
| `SITE_URL` | Backend URL | http://localhost:8000 |
| `FRONTEND_URL` | Frontend URL | http://localhost:3000 |

### Generate Secure Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Database Migrations

### View Migration Status
```bash
python manage.py showmigrations
```

### Create New Migrations (after model changes)
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Rollback to Previous Migration
```bash
python manage.py migrate app_name 0002  # Specific migration
python manage.py migrate app_name zero  # Remove all migrations
```

### Reset Database (Development Only)
```bash
# Remove old migrations (keep __init__.py files)
# Delete db.sqlite3
# Recreate migrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
python manage.py test accounts
python manage.py test store
python manage.py test orders
```

### Run with Verbosity
```bash
python manage.py test --verbosity=2
```

---

## Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in settings or environment
- [ ] Generate a secure `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with actual domain names
- [ ] Switch to PostgreSQL database
- [ ] Configure Razorpay credentials
- [ ] Configure Google OAuth credentials
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure CORS for frontend domain only
- [ ] Set `CORS_ALLOW_ALL_ORIGINS = False`
- [ ] Use a production WSGI server (Gunicorn)
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure environment variables securely

### 1. Install Gunicorn (Production Server)
```bash
pip install gunicorn
pip freeze > requirements.txt
```

### 2. Update `core/settings.py` for Production

```python
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# More restrictive for production
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Restrict CORS in production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    os.environ.get('FRONTEND_URL', 'http://localhost:3000'),
]

# Security settings for production
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}
```

### 3. Create Gunicorn Configuration

Create `gunicorn_config.py`:
```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
```

### 4. Run with Gunicorn
```bash
gunicorn --config gunicorn_config.py core.wsgi:application
```

### 5. Nginx Configuration Example

```nginx
upstream gunicorn {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 100M;

    location /static/ {
        alias /path/to/backend/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/backend/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### 6. Deploy Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: vinsaraa_db
      POSTGRES_USER: vinsaraa_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 core.wsgi:application
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://vinsaraa_user:secure_password@db:5432/vinsaraa_db
      DEBUG: "False"
      SECRET_KEY: your-secret-key
    depends_on:
      - db
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles

volumes:
  postgres_data:
```

Run with Docker:
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## Troubleshooting

### Issue: Module not found errors
**Solution:**
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database connection failed
**Solution:**
```bash
# Check database URL in .env
# Verify PostgreSQL is running (if using PostgreSQL)
psql -U vinsaraa_user -d vinsaraa_db -h localhost

# Recreate migrations
python manage.py migrate --fake-initial
```

### Issue: Static files not loading
**Solution:**
```bash
python manage.py collectstatic --clear --noinput
```

### Issue: Permission denied on Linux
**Solution:**
```bash
# Give execute permission to manage.py
chmod +x manage.py

# Fix directory permissions
chmod -R 755 .
```

### Issue: CORS errors from frontend
**Solution:** Check `FRONTEND_URL` in `.env` and update `CORS_ALLOWED_ORIGINS` in settings.py

### Issue: Google OAuth not working
**Solution:**
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
- Check Google Cloud Console for authorized redirect URIs: `http://your-domain/accounts/google/login/callback/`

### Issue: Razorpay payments failing
**Solution:**
- Verify `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in `.env`
- Check webhook configuration in Razorpay dashboard

---

## Quick Reference Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create/apply migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic --noinput

# Access Django shell
python manage.py shell

# Check for issues
python manage.py check

# Clear cache
python manage.py clear_cache
```

---

## Security Notes

1. **Never commit `.env` to version control**
2. **Always use strong `SECRET_KEY` in production**
3. **Set `DEBUG = False` in production**
4. **Use HTTPS in production**
5. **Restrict `CORS_ALLOWED_ORIGINS` to frontend domain only**
6. **Use environment variables for sensitive data**
7. **Keep dependencies updated** with `pip install --upgrade -r requirements.txt`
8. **Use strong database passwords**
9. **Configure firewall rules appropriately**
10. **Set up regular database backups**

---

## Support & Contact

For issues or questions, contact the development team or check the project repository's issue tracker.

**Last Updated:** December 21, 2025
