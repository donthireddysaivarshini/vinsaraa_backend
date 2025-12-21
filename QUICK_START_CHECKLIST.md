# Vinsaraa Backend - Quick Start Checklist

Use this checklist for rapid deployment and testing.

---

## ✅ Development Setup (5-10 minutes)

```bash
# 1. Clone and navigate
git clone <repository-url>
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your configuration (DEBUG=True, SECRET_KEY, etc.)

# 5. Run migrations
python manage.py migrate

# 6. Create admin user
python manage.py createsuperuser
# Email: admin@example.com
# Password: (your choice)

# 7. Start server
python manage.py runserver
# Access at http://localhost:8000/admin
```

---

## ✅ PostgreSQL Setup (10-15 minutes)

```bash
# 1. Install PostgreSQL
# Windows: https://www.postgresql.org/download/windows/
# macOS: brew install postgresql@15
# Linux: sudo apt-get install postgresql postgresql-contrib

# 2. Create database and user
psql -U postgres
# Inside psql:
CREATE DATABASE vinsaraa_db;
CREATE USER vinsaraa_user WITH PASSWORD 'your_password';
ALTER ROLE vinsaraa_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE vinsaraa_db TO vinsaraa_user;
\q

# 3. Install PostgreSQL adapter
pip install psycopg2-binary dj-database-url

# 4. Update .env
# DATABASE_URL=postgresql://vinsaraa_user:your_password@localhost:5432/vinsaraa_db

# 5. Update settings.py (follow SETUP_AND_DEPLOYMENT.md)

# 6. Run migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Verify connection
python manage.py dbshell
```

---

## ✅ Pre-Deployment Testing

```bash
# Run all tests
python manage.py test

# Check for issues
python manage.py check

# Test database connection
python manage.py dbshell

# Verify static files
python manage.py collectstatic --noinput

# Test email (optional)
python manage.py shell
# >>> from django.core.mail import send_mail
# >>> send_mail('Test', 'Message', 'noreply@vinsaraa.com', ['test@example.com'])

# Test Razorpay integration (in shell)
# >>> from payments.razorpay_client import razorpay_client
# >>> razorpay_client.order.create(data={"amount": 1000, "currency": "INR"})
```

---

## ✅ Production Deployment Checklist

### Before Deployment
- [ ] Change `DEBUG = False`
- [ ] Generate secure `SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS` with domain names
- [ ] Set `CORS_ALLOWED_ORIGINS` to frontend URL only
- [ ] Update database to PostgreSQL
- [ ] Configure all environment variables in `.env`
- [ ] Set up SSL/HTTPS certificate
- [ ] Run full test suite: `python manage.py test`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Verify migrations: `python manage.py showmigrations`

### Deployment Steps
```bash
# 1. Install Gunicorn
pip install gunicorn

# 2. Run migrations on production server
python manage.py migrate

# 3. Create superuser on production
python manage.py createsuperuser

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Start Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 core.wsgi:application

# 6. Configure Nginx (see SETUP_AND_DEPLOYMENT.md for config)

# 7. Set up SSL with Let's Encrypt
# certbot certonly --standalone -d yourdomain.com
```

---

## ✅ API Endpoints Overview

| Endpoint | Purpose |
|----------|---------|
| `POST /api/auth/register/` | User registration |
| `POST /api/auth/login/` | User login |
| `POST /api/auth/refresh/` | Refresh JWT token |
| `GET /api/auth/user/` | Get current user |
| `GET /api/store/products/` | List products |
| `GET /api/store/categories/` | List categories |
| `GET /api/orders/` | List user orders |
| `POST /api/orders/create/` | Create new order |
| `POST /api/payments/razorpay/order/` | Create Razorpay order |
| `POST /api/payments/razorpay/verify/` | Verify payment |
| `GET /api/content/hero_slides/` | Get hero slides |

---

## ✅ Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Verify venv activated and requirements installed |
| `OperationalError: no such table` | Run `python manage.py migrate` |
| `CSRF token missing` | Check request headers include `X-CSRFToken` |
| `CORS error` | Update `FRONTEND_URL` in `.env` and settings |
| `Database connection refused` | Verify PostgreSQL is running and credentials are correct |
| `Static files not found` | Run `python manage.py collectstatic --clear --noinput` |
| `Google OAuth not working` | Verify `GOOGLE_CLIENT_ID` and redirect URIs in Google Cloud Console |
| `Razorpay payment failed` | Check `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in `.env` |

---

## 📱 Frontend Integration

The frontend should be configured to use:
```
API_URL=http://localhost:8000/api
```

For production:
```
API_URL=https://yourdomain.com/api
```

---

## 📊 Useful Django Commands

```bash
# Database
python manage.py migrate              # Apply migrations
python manage.py makemigrations       # Create migrations
python manage.py showmigrations       # Show migration status

# Users
python manage.py createsuperuser      # Create admin user
python manage.py changepassword <user>

# Testing
python manage.py test                 # Run all tests
python manage.py test accounts        # Test specific app

# Utilities
python manage.py shell                # Interactive Python shell
python manage.py dbshell              # Database shell
python manage.py check                # Check for errors
python manage.py collectstatic        # Collect static files
python manage.py flush                # Clear database (DEV ONLY)
```

---

## 🔐 Security Reminders

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use strong passwords** - For database and admin users
3. **Rotate Razorpay keys** - Regularly in production
4. **Monitor API logs** - Check for suspicious activity
5. **Keep dependencies updated** - Run `pip list --outdated`
6. **Use HTTPS only** - In production
7. **Enable HTTPS redirects** - `SECURE_SSL_REDIRECT = True`
8. **Backup database regularly** - Daily in production

---

## 📞 Contact & Support

- **Documentation:** See `SETUP_AND_DEPLOYMENT.md`
- **Issues:** Check project repository
- **Environment Variables:** See `.env.example`

**Ready to deploy!** 🚀

