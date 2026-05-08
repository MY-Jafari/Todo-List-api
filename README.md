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

# 📝 درباره پروژه | About The Project

**Todo List API** یک پروژه بکاند کامل و حرفه‌ای مبتنی بر Django REST Framework است که علاوه بر
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

## ✨ ویژگی‌های کلیدی | Key Features

### 🔐 احراز هویت | Authentication
- **ثبت‌نام با موبایل** — ثبت‌نام فقط با شماره موبایل (اعتبارسنجی ۱۱ رقمی ایرانی: `09xxxxxxxxx`)
- **کد TOTP بلادرنگ** — استفاده از `pyotp` برای تولید کدهای ۶ رقمی بر اساس زمان (بدون ذخیره در دیتابیس)
- **JWT Verification Token** — انتقال امن وضعیت تأیید بین مراحل ثبت‌نام با JWT موقت (بدون نیاز به Session)
- **لاگین ترکیبی (Hybrid Login)** — ورود با **رمز عبور** (پیش‌فرض) **یا** کد OTP
- **ورود بدون رمز (Passwordless)** — ورود با درخواست کد OTP در دو مرحله (`send-login-otp` + `verify-login-otp`)
- **تأیید ایمیل** — ارسال کد به ایمیل با قالب HTML (SHA256 hashed storage)
- **فراموشی رمز** — بازیابی رمز عبور با کد OTP (اولویت با شماره موبایل)
- **Rate Limiting** — محدودیت ۲ دقیقه‌ای بین هر درخواست OTP
- **Custom User Model از صفر** — ساخته‌شده با `AbstractBaseUser` + `PermissionsMixin`، شناسه: `phone_number`

### 📋 مدیریت تسک‌ها | Task Management
- **مدیریت لیست‌ها** — ایجاد، مشاهده، ویرایش و حذف لیست‌های کار شخصی
- **مدیریت وظایف** — ایجاد، مشاهده، ویرایش و حذف وظایف درون لیست‌ها
- **فیلتر و جستجو** — فیلتر کردن وظایف بر اساس وضعیت، اولویت، لیست و جستجوی متنی
- **مرتب‌سازی** — مرتب‌سازی بر اساس تاریخ ایجاد، وضعیت، اولویت و عنوان
- **صفحه‌بندی** — بازگشت خودکار نتایج به صورت صفحه‌بندی شده (۵ آیتم در هر صفحه)
- **کنترل دسترسی** — هر کاربر فقط به لیست‌ها و تسک‌های خودش دسترسی دارد

### 🛡️ امنیت | Security
- **Non-root user** در Docker
- **Multi-stage Docker build** برای کاهش حجم ایمیج
- **Security headers** در Nginx
- **Health checks** برای همه سرویس‌ها
- **پنل ادمین کامل** — نمایش تمام اطلاعات کاربران (شماره موبایل، ایمیل، وضعیت تأیید)

### 🧪 تست‌ها | Testing
- **۸۵ تست خودکار** با Pytest
- پوشش کامل مدل‌های `User`, `PhoneVerification`, `EmailVerification`
- پوشش کامل تمام APIهای Auth (ثبت‌نام، لاگین، ایمیل، بازیابی رمز)
- پوشش کامل CRUD لیست‌ها و تسک‌ها
- تست‌های امنیتی (دسترسی غیرمجاز → 401/403)
- تست Rate Limiting و اعتبارسنجی شماره ایرانی

---

## 🛠️ تکنولوژی‌ها | Tech Stack

| **دسته** | **تکنولوژی** |
|-----------|--------------|
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



## 🚀 نصب و راه‌اندازی | Installation

### 📦 پیش‌نیازها | Prerequisites

- **Docker & Docker Compose** (توصیه می‌شود | Recommended)
- Python 3.12+ (برای اجرای دستی | For manual setup)
- PostgreSQL 16 (برای Production)

---

### 🐳 روش اجرا با Docker (توصیه می‌شود) | Docker Setup (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/MY-Jafari/Todo-List-api.git
cd Todo-List-api

# 2. Create .env file from template
cp .env.example .env
# Edit .env with your configuration (see Environment Variables section below)

# 3. Run with Docker Compose
docker compose up -d --build

# 4. Create a superuser
docker compose exec web python manage.py createsuperuser

# 5. Access the application
# - Swagger UI:  http://localhost/swagger/
# - ReDoc:       http://localhost/redoc/
# - Admin Panel: http://localhost/admin/
# - API:         http://localhost/api/v1/todos/

    نکته برای کاربران داخل ایران: برای استفاده از میرورهای داخلی:
    bash

    docker compose build --build-arg USE_IRAN_MIRRORS=true
    docker compose up -d

💻 روش اجرای دستی (توسعه محلی) | Manual Setup (Local Development)
bash

# 1. Clone the repository
git clone https://github.com/MY-Jafari/Todo-List-api.git
cd Todo-List-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# یا
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your local configuration
# Set DB_HOST=localhost for local PostgreSQL

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

📡 API Endpoints
🔐 احراز هویت | Authentication
Method	Endpoint	توضیح	Auth
POST	/api/v1/auth/send-otp/	درخواست کد تأیید برای ثبت‌نام	❌
POST	/api/v1/auth/verify-otp-register/	تأیید کد و تکمیل ثبت‌نام + دریافت JWT	❌
POST	/api/v1/auth/login/	ورود با رمز عبور (پیش‌فرض)	❌
POST	/api/v1/auth/send-login-otp/	درخواست کد OTP برای ورود بدون رمز	❌
POST	/api/v1/auth/verify-login-otp/	تأیید کد OTP و ورود + دریافت JWT	❌
POST	/api/v1/auth/send-email-verification/	ارسال کد تأیید به ایمیل	✅ JWT
POST	/api/v1/auth/verify-email/	تأیید ایمیل با کد دریافتی	✅ JWT
POST	/api/v1/auth/password-reset/request/	درخواست کد بازیابی رمز (با موبایل)	❌
POST	/api/v1/auth/password-reset/confirm/	تأیید کد و تنظیم رمز جدید	❌
📋 لیست‌ها | Lists
Method	Endpoint	توضیح
GET	/api/v1/todos/lists/	دریافت همه لیست‌های کاربر
POST	/api/v1/todos/lists/	ایجاد لیست جدید
GET	/api/v1/todos/lists/{list_id}/	دریافت جزئیات یک لیست
PUT	/api/v1/todos/lists/{list_id}/	بروزرسانی کامل لیست
PATCH	/api/v1/todos/lists/{list_id}/	بروزرسانی جزئی لیست
DELETE	/api/v1/todos/lists/{list_id}/	حذف لیست
✅ وظایف | Tasks
Method	Endpoint	توضیح
GET	/api/v1/todos/tasks/	دریافت همه وظایف کاربر
POST	/api/v1/todos/tasks/	ایجاد وظیفه جدید
GET	/api/v1/todos/tasks/{task_id}/	دریافت جزئیات وظیفه
PUT	/api/v1/todos/tasks/{task_id}/	بروزرسانی کامل وظیفه
PATCH	/api/v1/todos/tasks/{task_id}/	بروزرسانی جزئی وظیفه
DELETE	/api/v1/todos/tasks/{task_id}/	حذف وظیفه
GET	/api/v1/todos/lists/{list_id}/tasks/	دریافت وظایف یک لیست خاص
POST	/api/v1/todos/lists/{list_id}/tasks/	ایجاد وظیفه در لیست خاص
🔍 فیلتر و جستجو | Filtering & Search
Parameter	Description	Example
status	فیلتر بر اساس وضعیت	?status=todo
priority	فیلتر بر اساس اولویت	?priority=high
list	فیلتر بر اساس لیست	?list=1
search	جستجوی متنی در عنوان	?search=buy
o / ordering	مرتب‌سازی نتایج	?o=-created_at
page	شماره صفحه	?page=1
page_size	تعداد آیتم در صفحه	?page_size=10

    مقادیر معتبر:

        status: todo, inprogress, done

        priority: low, medium, high

        ordering: status, -status, priority, -priority, task_title, -task_title, created_at, -created_at

📊 مدل‌های داده | Data Models
👤 User (کاربر سفارشی)
فیلد	نوع	توضیح
phone_number	CharField(15)	شناسه یکتا برای ورود (USERNAME_FIELD)
email	EmailField	ایمیل کاربر (اختیاری)
email_verified	BooleanField	وضعیت تأیید ایمیل
full_name	CharField(150)	نام کامل (اختیاری)
is_active	BooleanField	وضعیت فعال بودن حساب
is_staff	BooleanField	دسترسی به پنل ادمین
is_phone_verified	BooleanField	وضعیت تأیید شماره موبایل
date_joined	DateTimeField	تاریخ ثبت‌نام

ویژگی‌های خاص:

    ساخته‌شده از صفر با AbstractBaseUser + PermissionsMixin

    استفاده از phone_number به‌عنوان شناسه (به جای username)

    UserManager سفارشی برای ساخت کاربر و سوپریوزر

    ایندکس‌گذاری روی phone_number و email برای عملکرد بهتر

📱 PhoneVerification (تأیید موبایل با TOTP)
فیلد	نوع	توضیح
phone_number	CharField(11)	شماره در حال تأیید
secret	CharField(32)	کلید Base32 برای TOTP
session_token	CharField(64)	توکن جلسه (UUID)
created_at	DateTimeField	زمان ایجاد
verified	BooleanField	وضعیت تأیید

ویژگی‌ها:

    استفاده از TOTP (Time-based One-Time Password) با pyotp

    کد هرگز در دیتابیس ذخیره نمی‌شود — فقط secret ذخیره می‌شود

    اعتبار خودکار ۲ دقیقه‌ای (بدون نیاز به چک دستی)

    جلوگیری از replay attack

✉️ EmailVerification (تأیید ایمیل با SHA256)
فیلد	نوع	توضیح
email	EmailField	ایمیل در حال تأیید
user	ForeignKey	کاربر مربوطه
code_hash	CharField(64)	هش SHA256 کد ۶ رقمی
created_at	DateTimeField	زمان ایجاد
is_used	BooleanField	وضعیت مصرف

ویژگی‌ها:

    کد اصلی در دیتابیس ذخیره نمی‌شود — فقط هش SHA256

    تولید کد ۶ رقمی با secrets (cryptographically secure)

    اعتبار ۱۰ دقیقه‌ای

    ایندکس‌گذاری روی email و user

📋 List (لیست کار)
فیلد	نوع	توضیح
list_id	AutoField	شناسه یکتا (PK)
user	ForeignKey	مالک لیست
list_name	CharField(200)	نام لیست
description	TextField	توضیحات (اختیاری)
created_at	DateTimeField	تاریخ ایجاد
updated_at	DateTimeField	تاریخ بروزرسانی
✅ Task (وظیفه)
فیلد	نوع	توضیح
task_id	AutoField	شناسه یکتا (PK)
user	ForeignKey	مالک وظیفه
list	ForeignKey	لیست والد
task_title	CharField(255)	عنوان وظیفه
task_description	TextField	توضیحات (اختیاری)
priority	ChoiceField	low / medium / high
status	ChoiceField	todo / inprogress / done
due_date	DateTimeField	تاریخ سررسید (اختیاری)
created_at	DateTimeField	تاریخ ایجاد
updated_at	DateTimeField	تاریخ بروزرسانی
🧪 اجرای تست‌ها | Running Tests
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

📊 پوشش تست‌ها | Test Coverage (85 Tests)
دسته	تعداد	شرح
test_models.py (accounts)	۳۰ تست	User, PhoneVerification (TOTP), EmailVerification (SHA256)
test_auth_apis.py (accounts)	۲۶ تست	ثبت‌نام, لاگین (رمز + OTP), تأیید ایمیل, بازیابی رمز, Rate Limiting
test_models.py (todos)	۸ تست	List & Task creation, validation
test_views.py (todos)	۲۱ تست	CRUD, filtering, ordering, pagination, security checks
⚙️ متغیرهای محیطی | Environment Variables

فایل .env.example را به .env کپی کنید و مقادیر را تنظیم کنید:
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

    توجه: مقادیر POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD باید دقیقاً با DB_NAME, DB_USER, DB_PASSWORD یکسان باشند.

🔧 ابزارهای کیفیت کد | Code Quality
bash

# Format code with Black
black .

# Lint with Flake8
flake8 apps/

# Run all checks
black . && flake8 apps/ && pytest -v

📝 مستندات API | API Documentation

پس از اجرای پروژه، مستندات API از طریق آدرس‌های زیر در دسترس است:

    Swagger UI: http://localhost/swagger/

    ReDoc: http://localhost/redoc/

    برای تست API در Swagger:

        ابتدا از /api/v1/auth/login/ وارد شوید (با رمز عبور)

        یا از /api/v1/auth/verify-login-otp/ (با کد OTP)

        توکن access را کپی کنید

        روی دکمه Authorize کلیک کنید

        مقدار Bearer <access_token> را وارد کنید

🏗️ معماری Docker | Docker Architecture
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

👤 نویسنده | Author

Mohammad Yasin Jafari

    GitHub: @MY-Jafari

    Project: Todo-List-api

📄 مجوز | License

This project is licensed under the MIT License.
See LICENSE for details.
<div align="center"> Made with ❤️ by <b>MY-Jafari</b> | Full-Stack Django API Project

<b>🔐 Custom Auth · 📋 Task Management · 🐳 Dockerized · ✅ 85 Tests</b>
</div> ```
