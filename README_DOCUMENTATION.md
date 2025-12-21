# Vinsaraa Backend - Documentation Index

Complete documentation for the Vinsaraa Django REST API backend.

---

## 📚 Documentation Overview

This project includes comprehensive documentation for developers, QA testers, and tech leads.

### For Developers & First-Time Setups
👉 **Start here:** [SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md)

Comprehensive guide covering:
- Project overview and technology stack
- Prerequisites and system requirements
- Step-by-step setup instructions
- Local development environment
- SQLite to PostgreSQL migration
- Environment configuration
- Database migrations
- Testing procedures
- Production deployment options
- Docker deployment
- Troubleshooting guide

### For Quick Testing & Immediate Deployment
👉 **Start here:** [QUICK_START_CHECKLIST.md](QUICK_START_CHECKLIST.md)

Quick reference for:
- 5-10 minute development setup
- 10-15 minute PostgreSQL setup
- Pre-deployment testing checklist
- Production deployment checklist
- API endpoints overview
- Quick troubleshooting guide
- Essential Django commands

### For Tech Leads & DevOps Engineers
👉 **Start here:** [TECH_LEAD_DEPLOYMENT.md](TECH_LEAD_DEPLOYMENT.md)

Advanced guide covering:
- Architecture overview
- System requirements (dev/prod)
- Pre-deployment checklist
- Server setup and hardening
- PostgreSQL configuration and tuning
- Application deployment with Gunicorn
- Nginx reverse proxy setup
- SSL/TLS configuration
- Monitoring and logging
- Backup and recovery procedures
- Scaling considerations
- CI/CD integration
- Health checks and alerts
- Troubleshooting production issues

---

## 🚀 Quick Start (Choose Your Path)

### Path 1: Development Setup (Next 10 minutes)
```bash
# 1. Create virtual environment and install
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env with DEBUG=True, SECRET_KEY, etc.

# 3. Run migrations and start
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Visit: http://localhost:8000/admin
```

→ See [QUICK_START_CHECKLIST.md](QUICK_START_CHECKLIST.md) for more details

### Path 2: PostgreSQL Setup (Next 20 minutes)
```bash
# 1. Install PostgreSQL (or use existing)
# See SETUP_AND_DEPLOYMENT.md for platform-specific instructions

# 2. Create database and user
psql -U postgres
CREATE DATABASE vinsaraa_db;
CREATE USER vinsaraa_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE vinsaraa_db TO vinsaraa_user;

# 3. Update .env and settings
pip install psycopg2-binary dj-database-url
# Update .env: DATABASE_URL=postgresql://vinsaraa_user:password@localhost:5432/vinsaraa_db
# Update settings.py (see SETUP_AND_DEPLOYMENT.md)

# 4. Run migrations
python manage.py migrate
```

→ See [SETUP_AND_DEPLOYMENT.md - Switching to PostgreSQL](SETUP_AND_DEPLOYMENT.md#switching-to-postgresql)

### Path 3: Production Deployment (Next 1-2 hours)
```bash
# Follow the complete checklist in TECH_LEAD_DEPLOYMENT.md including:
# - System setup and hardening
# - PostgreSQL installation and configuration
# - Gunicorn application server setup
# - Nginx reverse proxy configuration
# - SSL/TLS certificate setup
# - Monitoring and logging configuration
# - Backup procedures
```

→ See [TECH_LEAD_DEPLOYMENT.md](TECH_LEAD_DEPLOYMENT.md)

---

## 🔧 Project Structure

```
backend/
├── accounts/              # User authentication & profiles
│   ├── models.py         # CustomUser, Address, SavedAddress models
│   ├── views.py          # Auth endpoints
│   ├── serializers.py    # User serializers
│   ├── urls.py           # Auth URLs
│   └── migrations/       # Database migrations
├── store/                # Products & inventory
│   ├── models.py         # Product, Category, etc.
│   ├── views.py          # Product endpoints
│   ├── serializers.py    # Product serializers
│   └── migrations/
├── orders/               # Order management
│   ├── models.py         # Order, OrderItem models
│   ├── views.py          # Order endpoints
│   └── migrations/
├── payments/             # Razorpay integration
│   ├── models.py         # Payment models
│   ├── views.py          # Payment endpoints
│   ├── razorpay_client.py # Razorpay integration
│   └── migrations/
├── web_content/          # Hero slides, videos, etc.
│   ├── models.py         # Content models
│   ├── views.py          # Content endpoints
│   └── management/       # Custom management commands
├── core/                 # Django configuration
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── wsgi.py          # WSGI entry point
│   └── asgi.py          # ASGI entry point
├── static/              # Static files (CSS, JS)
├── media/               # User uploads (products, images)
├── manage.py            # Django management
├── requirements.txt     # Python dependencies
├── db.sqlite3           # SQLite database (dev only)
├── .env.example         # Environment template
└── .env                 # Environment variables (not in git)
```

---

## 📋 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | Django | 5.2.9 |
| **REST API** | Django REST Framework | 3.16.1 |
| **Authentication** | SimpleJWT | 5.5.1 |
| **Social Auth** | django-allauth | 65.13.1 |
| **Admin UI** | Jazzmin | 3.0.1 |
| **Database (Dev)** | SQLite | Built-in |
| **Database (Prod)** | PostgreSQL | 13+ |
| **Image Processing** | Pillow | 12.0.0 |
| **Payment Gateway** | Razorpay | 1.4.2 |
| **API Client** | Requests | 2.32.5 |
| **Environment** | python-dotenv | Latest |
| **CORS** | django-cors-headers | 4.9.0 |

---

## 🔐 Key Features

### Authentication
- Email-based user accounts (no username required)
- JWT token authentication
- Google OAuth 2.0 login
- Password strength validation
- Secure password hashing

### Products & Store
- Product catalog with categories
- Product images and videos
- Product filtering and search
- Inventory management
- Country of origin and disclaimers

### Orders & Payments
- Shopping cart functionality
- Order creation and tracking
- Razorpay payment integration
- Order status management
- Payment webhook handling

### User Features
- User profiles and addresses
- Saved addresses for quick checkout
- Order history
- Account management

### Admin Features
- Jazzmin enhanced admin interface
- Custom admin customizations
- Dashboard and analytics
- Content management

---

## 🌐 API Endpoints

### Authentication Endpoints
```
POST   /api/auth/register/          - User registration
POST   /api/auth/login/             - User login
POST   /api/auth/logout/            - User logout
POST   /api/auth/refresh/           - Refresh JWT token
GET    /api/auth/user/              - Get current user
POST   /api/auth/google/            - Google OAuth login
```

### Store Endpoints
```
GET    /api/store/products/         - List all products
GET    /api/store/products/<id>/    - Get product details
GET    /api/store/categories/       - List categories
GET    /api/store/categories/<id>/  - Get category details
```

### Orders Endpoints
```
GET    /api/orders/                 - List user orders
POST   /api/orders/create/          - Create new order
GET    /api/orders/<id>/            - Get order details
PATCH  /api/orders/<id>/            - Update order status
```

### Payments Endpoints
```
POST   /api/payments/razorpay/order/    - Create Razorpay order
POST   /api/payments/razorpay/verify/   - Verify payment
POST   /api/payments/webhook/razorpay/  - Razorpay webhook
```

### Content Endpoints
```
GET    /api/content/hero_slides/    - Get hero slides
GET    /api/content/videos/         - Get videos
GET    /api/content/promotions/     - Get promotions
```

---

## 📦 Dependencies

### Core Django Packages
```
Django==5.2.9                    # Web framework
djangorestframework==3.16.1      # REST API
djangorestframework_simplejwt    # JWT authentication
dj-rest-auth==7.0.1             # REST auth endpoints
```

### Authentication & Authorization
```
django-allauth==65.13.1         # Social authentication
rest_framework.authtoken        # Token auth
```

### Additional Features
```
django-cors-headers==4.9.0      # CORS support
django-environ==0.12.0          # Environment variables
django-jazzmin==3.0.1           # Enhanced admin
Pillow==12.0.0                  # Image processing
razorpay==1.4.2                 # Razorpay SDK
python-dotenv                   # .env file support
```

---

## 🔄 Environment Variables Reference

All environment variables are documented in [.env.example](.env.example)

**Important Variables:**
- `DEBUG` - Development flag (True/False)
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Comma-separated allowed hosts
- `DATABASE_URL` - Database connection string
- `RAZORPAY_KEY_ID` - Razorpay public key
- `RAZORPAY_KEY_SECRET` - Razorpay secret key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret
- `SITE_URL` - Backend URL
- `FRONTEND_URL` - Frontend URL

---

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run App-Specific Tests
```bash
python manage.py test accounts    # Test authentication
python manage.py test store       # Test products
python manage.py test orders      # Test orders
python manage.py test payments    # Test payments
```

### With Verbosity
```bash
python manage.py test --verbosity=2
```

---

## 📊 Database Migrations

### View Migration Status
```bash
python manage.py showmigrations
```

### Create New Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Rollback Migrations
```bash
python manage.py migrate accounts 0001  # Go to specific migration
python manage.py migrate accounts zero  # Remove all migrations
```

---

## 🐛 Common Issues & Solutions

| Issue | Solution | Ref |
|-------|----------|-----|
| Module not found | Activate venv, reinstall requirements | [SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md) |
| Database errors | Run migrations | [SETUP_AND_DEPLOYMENT.md#database-migrations](SETUP_AND_DEPLOYMENT.md#database-migrations) |
| CORS errors | Update FRONTEND_URL in .env | [SETUP_AND_DEPLOYMENT.md#environment-variables](SETUP_AND_DEPLOYMENT.md#environment-variables) |
| Static files missing | Run collectstatic | [TECH_LEAD_DEPLOYMENT.md](TECH_LEAD_DEPLOYMENT.md) |
| Razorpay errors | Verify API keys | [.env.example](.env.example) |
| Google OAuth fails | Check OAuth credentials | [SETUP_AND_DEPLOYMENT.md](SETUP_AND_DEPLOYMENT.md) |

→ See full troubleshooting guides:
- [SETUP_AND_DEPLOYMENT.md#troubleshooting](SETUP_AND_DEPLOYMENT.md#troubleshooting)
- [QUICK_START_CHECKLIST.md#-troubleshooting-quick-fixes](QUICK_START_CHECKLIST.md#-troubleshooting-quick-fixes)
- [TECH_LEAD_DEPLOYMENT.md#troubleshooting-production-issues](TECH_LEAD_DEPLOYMENT.md#troubleshooting-production-issues)

---

## 🚦 Deployment Paths

### Development
```bash
1. Clone repo
2. Create venv
3. Install requirements
4. Setup .env (DEBUG=True)
5. Run migrations
6. Create superuser
7. Start server: python manage.py runserver
```

### Testing/Staging
```bash
1. Use PostgreSQL
2. Set DEBUG=False
3. Generate secure SECRET_KEY
4. Configure all API keys
5. Run full test suite
6. Deploy with Gunicorn
```

### Production
```bash
1. Follow TECH_LEAD_DEPLOYMENT.md completely
2. Use PostgreSQL with replication
3. Configure SSL/TLS
4. Set up monitoring and logging
5. Configure backup procedures
6. Deploy with Gunicorn + Nginx
7. Enable health checks
```

---

## 📞 Quick Reference

### Essential Commands
```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install
pip install -r requirements.txt

# Database
python manage.py migrate
python manage.py createsuperuser
python manage.py makemigrations

# Run
python manage.py runserver        # Development
gunicorn core.wsgi:application    # Production

# Admin
python manage.py shell            # Interactive shell
python manage.py dbshell          # Database shell
python manage.py check            # Check configuration

# Testing
python manage.py test             # Run tests
python manage.py test --verbosity=2

# Static files
python manage.py collectstatic --noinput
```

---

## 🔗 Related Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Razorpay API Documentation](https://razorpay.com/docs/api/)

---

## 📝 Document Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-21 | 1.0 | Initial complete documentation |

---

## 📧 Support

For questions or issues:
1. Check the relevant documentation file above
2. Review the troubleshooting sections
3. Check project repository issues
4. Contact the development team

---

**Happy Deploying! 🚀**

Generated: December 21, 2025  
Last Updated: December 21, 2025

