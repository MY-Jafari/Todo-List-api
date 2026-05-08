# Todo‑List‑api

![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.16-CC2927?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-🐳-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![TOTP](https://img.shields.io/badge/TOTP-2FA-4CAF50?style=for-the-badge&logo=authenticator&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-Docs-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)
![Pytest](https://img.shields.io/badge/Pytest-85_Tests-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

[![License](https://img.shields.io/github/license/MY-Jafari/Todo-List-api?style=flat-square)](https://github.com/MY-Jafari/Todo-List-api/blob/main/LICENSE)
[![Stars](https://img.shields.io/github/stars/MY-Jafari/Todo-List-api?style=flat-square)](https://github.com/MY-Jafari/Todo-List-api/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/MY-Jafari/Todo-List-api?style=flat-square)](https://github.com/MY-Jafari/Todo-List-api/commits/main)
[![Tests](https://img.shields.io/badge/tests-85%20passed-success?style=flat-square)]()

---

## About The Project

**Todo List API** یک پروژه بک‌اند کامل و حرفه‌ای مبتنی بر Django REST Framework است که علاوه بر
مدیریت لیست‌های کار (Todo Lists) و وظایف (Tasks) از طریق REST API، یک **سیستم احراز هویت
سفارشی کامل از صفر** را نیز پیاده‌سازی می‌کند. ویژگی‌های امنیتی مانند احراز هویت دومرحله‌ای
با **TOTP (Time-based One-Time Password)**، تأیید ایمیل با **هش SHA256**، و ورود ترکیبی
(رمز عبور + کد OTP) از نقاط قوت این پروژه هستند. کل پروژه با **Docker** و **Nginx** روی
**PostgreSQL** قابل اجراست و با **۸۵ تست خودکار** پوشش داده شده است.

**Todo List API** is a full-featured, production-ready Django REST Framework backend that
manages todo lists and tasks through a RESTful API. It also implements a **fully custom
authentication system from scratch**—built on `AbstractBaseUser`—featuring **TOTP-based
two-factor phone verification**, **SHA256-hashed email verification**, hybrid login
(password + OTP), rate limiting, and a complete password reset flow. The entire project
is containerized with **Docker**, served via **Nginx + Gunicorn** on **PostgreSQL**, and
backed by **85 automated tests**.

---

## Key Features

### Authentication

- **ثبت‌نام با موبایل** — ثبت‌نام فقط با شماره موبایل (اعتبارسنجی ۱۱ رقمی ایرانی: `09xxxxxxxxx`)
- **کد TOTP بلادرنگ** — استفاده از `pyotp` برای تولید کدهای ۶ رقمی بر اساس زمان (بدون ذخیره در دیتابیس)
- **JWT Verification Token** — انتقال امن وضعیت تأیید بین مراحل ثبت‌نام با JWT موقت (بدون نیاز به Session)
- **لاگین ترکیبی (Hybrid Login)** — ورود با **رمز عبور** (پیش‌فرض) **یا** کد OTP
- **ورود بدون رمز (Passwordless)** — ورود با درخواست کد OTP در دو مرحله (`send-login-otp` + `verify-login-otp`)
- **تأیید ایمیل** — ارسال کد به ایمیل با قالب HTML (SHA256 hashed storage)
- **فراموشی رمز** — بازیابی رمز عبور با کد OTP (اولویت با شماره موبایل)
- **Rate Limiting** — محدودیت ۲ دقیقه‌ای بین هر درخواست OTP
- **Custom User Model از صفر** — ساخته‌شده با `AbstractBaseUser` + `PermissionsMixin`، شناسه: `phone_number`

### Task Management

- **مدیریت لیست‌ها** — ایجاد، مشاهده، ویرایش و حذف لیست‌های کار شخصی
- **مدیریت وظایف** — ایجاد، مشاهده، ویرایش و حذف وظایف درون لیست‌ها
- **فیلتر و جستجو** — فیلتر کردن وظایف بر اساس وضعیت، اولویت، لیست و جستجوی متنی
- **مرتب‌سازی** — مرتب‌سازی بر اساس تاریخ ایجاد، وضعیت، اولویت و عنوان
- **صفحه‌بندی** — بازگشت خودکار نتایج به صورت صفحه‌بندی شده (۵ آیتم در هر صفحه)
- **کنترل دسترسی** — هر کاربر فقط به لیست‌ها و تسک‌های خودش دسترسی دارد

### Security

- **Non-root user** در Docker
- **Multi-stage Docker build** برای کاهش حجم ایمیج
- **Security headers** در Nginx
- **Health checks** برای همه سرویس‌ها
- **پنل ادمین کامل** — نمایش تمام اطلاعات کاربران (شماره موبایل، ایمیل، وضعیت تأیید)

### Testing

- **۸۵ تست خودکار** با Pytest
- پوشش کامل مدل‌های `User`, `PhoneVerification`, `EmailVerification`
- پوشش کامل تمام APIهای Auth (ثبت‌نام، لاگین، ایمیل، بازیابی رمز)
- پوشش کامل CRUD لیست‌ها و تسک‌ها
- تست‌های امنیتی (دسترسی غیرمجاز → 401/403)
- تست Rate Limiting و اعتبارسنجی شماره ایرانی

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | Django 5.2 + Django REST Framework 3.16 |
| Auth | Simple JWT (Access & Refresh Token) + PyOTP (TOTP) |
| Database | PostgreSQL 16 (Production) |
| Web Server | Nginx (Reverse Proxy) + Gunicorn |
| Container | Docker & Docker Compose |
| Docs | Swagger (drf-yasg) + ReDoc |
| Testing | Pytest (۸۵ تست) |
| Email | django-mail-templated (HTML templates) |
| Filtering | django-filter |

---

## Installation

### Prerequisites

- **Docker & Docker Compose** (Recommended)
- Python 3.12+ (for manual setup)
- PostgreSQL 16 (for Production)

### Docker Setup (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/MY-Jafari/Todo-List-api.git
cd Todo-List-api

# 2. Create .env file from template
cp .env.example .env

# 3. Run with Docker Compose
docker compose up -d --build

# 4. Create a superuser
docker compose exec web python manage.py createsuperuser

# 5. Access the application
# - Swagger UI:  http://localhost/swagger/
# - ReDoc:       http://localhost/redoc/
# - Admin Panel: http://localhost/admin/
# - API:         http://localhost/api/v1/todos/

    For users inside Iran:
    bash

    docker compose build --build-arg USE_IRAN_MIRRORS=true
    docker compose up -d

Manual Setup (Local Development)
bash

# 1. Clone the repository
git clone https://github.com/MY-Jafari/Todo-List-api.git
cd Todo-List-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# or
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver

# 8. Open in browser
# - Swagger: http://127.0.0.1:8000/swagger/
# - ReDoc:   http://127.0.0.1:8000/redoc/
# - Admin:   http://127.0.0.1:8000/admin/

API Endpoints
Authentication
Method	Endpoint	Description	Auth
POST	/api/v1/auth/send-otp/	Request registration OTP code	No
POST	/api/v1/auth/verify-otp-register/	Verify OTP + Register + Get JWT	No
POST	/api/v1/auth/login/	Login with password (default)	No
POST	/api/v1/auth/send-login-otp/	Request OTP for passwordless login	No
POST	/api/v1/auth/verify-login-otp/	Verify OTP + Login + Get JWT	No
POST	/api/v1/auth/send-email-verification/	Send email verification code	JWT
POST	/api/v1/auth/verify-email/	Verify email with code	JWT
POST	/api/v1/auth/password-reset/request/	Request password reset OTP	No
POST	/api/v1/auth/password-reset/confirm/	Verify OTP + Set new password	No
Lists
Method	Endpoint	Description
GET	/api/v1/todos/lists/	Get all user lists
POST	/api/v1/todos/lists/	Create a new list
GET	/api/v1/todos/lists/{list_id}/	Get list details
PUT	/api/v1/todos/lists/{list_id}/	Update a list
PATCH	/api/v1/todos/lists/{list_id}/	Partially update a list
DELETE	/api/v1/todos/lists/{list_id}/	Delete a list
Tasks
Method	Endpoint	Description
GET	/api/v1/todos/tasks/	Get all user tasks
POST	/api/v1/todos/tasks/	Create a new task
GET	/api/v1/todos/tasks/{task_id}/	Get task details
PUT	/api/v1/todos/tasks/{task_id}/	Update a task
PATCH	/api/v1/todos/tasks/{task_id}/	Partially update a task
DELETE	/api/v1/todos/tasks/{task_id}/	Delete a task
GET	/api/v1/todos/lists/{list_id}/tasks/	Get tasks for a specific list
POST	/api/v1/todos/lists/{list_id}/tasks/	Create task in a specific list
Filtering & Search
Parameter	Description	Example
status	Filter by status	?status=todo
priority	Filter by priority	?priority=high
list	Filter by list	?list=1
search	Text search in title	?search=buy
o / ordering	Order results	?o=-created_at
page	Page number	?page=1
page_size	Items per page	?page_size=10

    Valid values:

        status: todo, inprogress, done

        priority: low, medium, high

        ordering: status, -status, priority, -priority, task_title, -task_title, created_at, -created_at

Data Models
User (Custom User)
Field	Type	Description
phone_number	CharField(15)	Unique identifier for login (USERNAME_FIELD)
email	EmailField	User email (optional)
email_verified	BooleanField	Email verification status
full_name	CharField(150)	Full name (optional)
is_active	BooleanField	Account active status
is_staff	BooleanField	Admin panel access
is_phone_verified	BooleanField	Phone verification status
date_joined	DateTimeField	Registration date
PhoneVerification (TOTP)
Field	Type	Description
phone_number	CharField(11)	Phone number being verified
secret	CharField(32)	Base32 secret for TOTP
session_token	CharField(64)	Session UUID
created_at	DateTimeField	Creation time
verified	BooleanField	Verification status
EmailVerification (SHA256)
Field	Type	Description
email	EmailField	Email being verified
user	ForeignKey	Related user
code_hash	CharField(64)	SHA256 hash of 6-digit code
created_at	DateTimeField	Creation time
is_used	BooleanField	Usage status
List
Field	Type	Description
list_id	AutoField	Primary key
user	ForeignKey	List owner
list_name	CharField(200)	List name
description	TextField	Description (optional)
created_at	DateTimeField	Creation date
updated_at	DateTimeField	Last update date
Task
Field	Type	Description
task_id	AutoField	Primary key
user	ForeignKey	Task owner
list	ForeignKey	Parent list
task_title	CharField(255)	Task title
task_description	TextField	Description (optional)
priority	ChoiceField	low / medium / high
status	ChoiceField	todo / inprogress / done
due_date	DateTimeField	Due date (optional)
created_at	DateTimeField	Creation date
updated_at	DateTimeField	Last update date
Running Tests
bash

# Run all tests (85 tests)
pytest -v

# Run only accounts tests
pytest apps/accounts/tests/ -v

# Run only todos tests
pytest apps/todos/tests/ -v

# Run with coverage report
pytest --cov=apps --cov-report=html

# Run linting
flake8 apps/

# Run code formatting
black .

Test Coverage (85 Tests)
Suite	Count	Description
test_models.py (accounts)	30 tests	User, PhoneVerification (TOTP), EmailVerification (SHA256)
test_auth_apis.py (accounts)	26 tests	Registration, Login (password + OTP), Email verification, Password reset, Rate Limiting
test_models.py (todos)	8 tests	List & Task creation, validation
test_views.py (todos)	21 tests	CRUD, filtering, ordering, pagination, security checks
Environment Variables

Copy .env.example to .env and configure:
ini

# Django
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=todo_db
DB_USER=todo_user
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

    Note: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD in .env must match DB_NAME, DB_USER, DB_PASSWORD exactly.

Code Quality
bash

# Format code with Black
black .

# Lint with Flake8
flake8 apps/

# Run all checks
black . && flake8 apps/ && pytest -v

API Documentation

After running the project, API docs are available at:

    Swagger UI: http://localhost/swagger/

    ReDoc: http://localhost/redoc/

    To test APIs in Swagger:

        Login via /api/v1/auth/login/ (with password)

        Or via /api/v1/auth/verify-login-otp/ (with OTP)

        Copy the access token

        Click Authorize button

        Enter Bearer <access_token>

Docker Architecture
text

                    Internet
                        │
                        ▼
                ┌───────────────┐
                │    Nginx      │  ← Reverse Proxy (Port 80)
                │  (Alpine)     │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │  Gunicorn     │  ← WSGI Server (Port 8000)
                │  (4 workers)  │
                └───────┬───────┘
                        │
                ┌───────┴───────┐
                │               │
                ▼               ▼
        ┌──────────┐    ┌──────────┐
        │PostgreSQL│    │  Static  │
        │   (16)   │    │  Files   │
        └──────────┘    └──────────┘

Author

Mohammad Yasin Jafari

    GitHub: @MY-Jafari

    Project: Todo-List-api

License

This project is licensed under the MIT License.
See LICENSE for details.
<div align="center"> Made with ❤️ by <b>MY-Jafari</b> | Full-Stack Django API Project

<b>🔐 Custom Auth · 📋 Task Management · 🐳 Dockerized · ✅ 85 Tests</b>
</div> ```
