<div align="center">

![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.16-CC2927?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-🐳-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-Docs-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Tests-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

[![License](https://img.shields.io/github/license/MY-Jafari/Todo-List-api?style=flat-square)](https://github.com/MY-Jafari/Todo-List-api/blob/main/LICENSE)
[![Stars](https://img.shields.io/github/stars/MY-Jafari/Todo-List-api?style=flat-square)](https://github.com/MY-Jafari/Todo-List-api/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/MY-Jafari/Todo-List-api?style=flat-square)](https://github.com/MY-Jafari/Todo-List-api/commits/main)

</div>

# 📖 درباره پروژه | About The Project

Todo List API یک پروژه بک‌اند مبتنی بر Django REST Framework است که امکان مدیریت لیست‌های کار (Todo Lists) و وظایف (Tasks) را از طریق REST API فراهم می‌کند. این پروژه به عنوان اولین تجربه کاری من در زمینه Django و توسعه API طراحی و پیاده‌سازی شده است.
### ✨ ویژگی‌های کلیدی

- **احراز هویت JWT** — ورود، ثبت‌نام و مدیریت نشست کاربران با JSON Web Token
- **مدیریت لیست‌ها** — ایجاد، مشاهده، ویرایش و حذف لیست‌های کار شخصی
- **مدیریت وظایف** — ایجاد، مشاهده، ویرایش و حذف وظایف درون لیست‌ها
- **فیلتر و جستجو** — فیلتر کردن وظایف بر اساس وضعیت، اولویت و جستجوی متنی
- **صفحه‌بندی** — بازگشت خودکار نتایج به صورت صفحه‌بندی شده
- **مستندات Swagger** — مستندات کامل API با Swagger UI و ReDoc
- **Docker** — اجرای کامل پروژه با Docker و Nginx
- **تست‌های خودکار** — پوشش تست برای Models، Serializers و Views با Pytest

---


Todo List API is a Django REST Framework backend project that enables managing todo lists and tasks through a RESTful API. This project was built as my first hands-on experience with Django and API development.

### ✨ Key Features

- **JWT Authentication** — Login, registration, and session management with JSON Web Tokens
- **List Management** — Create, read, update, and delete personal todo lists
- **Task Management** — Create, read, update, and delete tasks within lists
- **Filtering & Search** — Filter tasks by status, priority, and full-text search
- **Pagination** — Automatic paginated results for all list endpoints
- **Swagger Documentation** — Interactive API docs with Swagger UI and ReDoc
- **Docker** — Full Docker setup with Nginx reverse proxy
- **Automated Tests** — Comprehensive test coverage using Pytest

---

# 🛠 تکنولوژی‌ها | Tech Stack

| Category | Technology |
|---|---|
| Framework | Django 5.2 + Django REST Framework |
| Auth | Simple JWT (Access & Refresh Token) |
| Database | SQLite (Dev) / PostgreSQL (Prod) |
| Cache | Redis |
| Web Server | Nginx + Gunicorn |
| Container | Docker & Docker Compose |
| Docs | Swagger (drf-yasg) + ReDoc |
| Testing | Pytest + Flake8 + Black |

---

# 📂 ساختار پروژه | Project Structure

```
Todo-List-api/
├── apps/                          # Django Applications
│   ├── todos/                     # Todo app
│   │   ├── api/v1/                # API version 1
│   │   │   ├── serializers.py     # Data serializers
│   │   │   ├── views.py           # API views (CRUD)
│   │   │   └── urls.py            # API routes
│   │   ├── tests/                 # Test suites
│   │   │   ├── api/v1/            # API tests
│   │   │   ├── test_models.py     # Model tests
│   │   │   └── test_filters.py    # Filter tests
│   │   ├── models.py              # List & Task models
│   │   ├── filters.py             # TaskFilter
│   │   └── urls.py                # App routes
│   └── users/                     # User app
│       ├── models.py              # Custom User & Profile
│       ├── tests/                 # User tests
│       └── views.py               # Auth views
├── core/                          # Django Project Config
│   ├── settings.py                # Settings
│   ├── urls.py                    # Main URL config + Swagger
│   ├── wsgi.py
│   └── asgi.py
├── nginx/                         # Nginx configuration
│   └── default.conf
├── static/                        # Static files
├── docker-compose.yml             # Docker Compose (web + redis)
├── Dockerfile                     # Docker image definition
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── .flake8                        # Flake8 linting rules
├── manage.py
└── README.md
```

---

# 🚀 نصب و راه‌اندازی | Installation

## پیش‌نیازها

- Python 3.12+
- Docker & Docker Compose (برای اجرا با Docker)
- Redis (برای محیط توسعه)

##  Prerequisites

- Python 3.12+
- Docker & Docker Compose (for Docker setup)
- Redis (for development)

---

## 🐳 روش اجرا با Docker (توصیه می‌شود)

```bash
# 1. Clone the repository
git clone https://github.com/MY-Jafari/Todo-List-api.git
cd Todo-List-api

# 2. Create .env file
cp .env.example .env
# Edit .env with your configuration

# 3. Run with Docker Compose
docker-compose up -d

# 4. Create a superuser (optional)
docker-compose exec web python manage.py createsuperuser

# 5. Open the API
# - API: http://localhost:8000/api/v1/todos/
# - Swagger: http://localhost:8000/swagger/
# - ReDoc: http://localhost:8000/redoc/
# - Admin: http://localhost:8000/admin/
```

## 💻 روش اجرای دستی (Local Development)

```bash
# 1. Clone the repository
git clone https://github.com/MY-Jafari/Todo-List-api.git
cd Todo-List-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver

# 7. Open in browser
# - API: http://127.0.0.1:8000/api/v1/todos/
# - Swagger: http://127.0.0.1:8000/swagger/
# - ReDoc: http://127.0.0.1:8000/redoc/
```

---

# 🔌 API Endpoints

## 🔐 Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Get JWT token (login) |
| POST | `/api/token/refresh/` | Refresh access token |

## 📋 Lists

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/todos/lists/` | Get all user lists |
| POST | `/api/v1/todos/lists/` | Create a new list |
| GET | `/api/v1/todos/lists/{list_id}/` | Get list details |
| PUT | `/api/v1/todos/lists/{list_id}/` | Update a list |
| PATCH | `/api/v1/todos/lists/{list_id}/` | Partial update |
| DELETE | `/api/v1/todos/lists/{list_id}/` | Delete a list |

## ✅ Tasks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/todos/tasks/` | Get all user tasks |
| POST | `/api/v1/todos/tasks/` | Create a new task |
| GET | `/api/v1/todos/tasks/{pk}/` | Get task details |
| PUT | `/api/v1/todos/tasks/{pk}/` | Update a task |
| PATCH | `/api/v1/todos/tasks/{pk}/` | Partial update |
| DELETE | `/api/v1/todos/tasks/{pk}/` | Delete a task |
| GET | `/api/v1/todos/lists/{list_id}/tasks/` | Get tasks in a list |
| POST | `/api/v1/todos/lists/{list_id}/tasks/` | Create task in list |

## 🔍 Filtering & Search

Tasks can be filtered using query parameters:

| Parameter | Description | Example |
|---|---|---|
| `status` | Filter by status | `?status=todo` |
| `priority` | Filter by priority | `?priority=high` |
| `search` | Search in task title | `?search=buy` |
| `ordering` | Sort results | `?ordering=-created_at` |
| `page` | Page number | `?page=1` |
| `page_size` | Items per page | `?page_size=10` |

---

# 🧪 اجرای تست‌ها | Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest apps/todos/tests/test_models.py

# Run with coverage report
pytest --cov=apps --cov-report=html

# Run linting
flake8 .

# Run code formatting
black .
```

## 📊 Test Coverage

Tests cover:

- ✅ **Models** — List and Task creation & validation
- ✅ **Serializers** — Data validation & read-only fields
- ✅ **Views** — CRUD operations & permission checks
- ✅ **Filters** — Task filtering & search functionality
- ✅ **User** — Custom user model & profile creation

---

# 📚 مستندات API | API Documentation

پس از اجرای پروژه، مستندات API از طریق آدرس‌های زیر در دسترس است:

After running the project, API documentation is available at:

- **Swagger UI:** `http://localhost:8000/swagger/`
- **ReDoc:** `http://localhost:8000/redoc/`

> 💡 برای تست API در Swagger:
> 1. ابتدا از `/api/token/` توکن دریافت کنید
> 2. روی دکمه **Authorize** کلیک کنید
> 3. مقدار `Bearer <your_token>` را وارد کنید
>
> 💡 To test the API in Swagger:
> 1. Get your token from `/api/token/`
> 2. Click **Authorize** button
> 3. Enter `Bearer <your_token>`

---

# 🗄 مدل‌های داده | Data Models

## 👤 User (کاربر سفارشی)

- ارث‌بری از `AbstractUser` django
- فیلدهای اضافی: `created_at`، `updated_at`
- متدهای سفارشی: `create_user`، `create_user_with_profile`، `create_superuser`
- پروفایل خودکار برای هر کاربر

**👤 User (Custom)**
- Extends Django `AbstractUser`
- Extra fields: `created_at`, `updated_at`
- Custom methods: `create_user`, `create_user_with_profile`, `create_superuser`
- Automatic profile creation

---

## 📋 List (لیست کار)

| فیلد | نوع | توضیح |
|---|---|---|
| `list_id` | AutoField | شناسه یکتا |
| `user` | ForeignKey | مالک لیست |
| `list_name` | CharField(200) | نام لیست |
| `description` | TextField | توضیحات (اختیاری) |
| `created_at` | DateTime | تاریخ ایجاد |
| `updated_at` | DateTime | تاریخ بروزرسانی |

**📋 List**

| Field | Type | Description |
|---|---|---|
| `list_id` | AutoField | Unique ID |
| `user` | ForeignKey | List owner |
| `list_name` | CharField(200) | List name |
| `description` | TextField | Description (optional) |
| `created_at` | DateTime | Created timestamp |
| `updated_at` | DateTime | Updated timestamp |

---

## ✅ Task (وظیفه)

| فیلد | نوع | توضیح |
|---|---|---|
| `task_id` | AutoField | شناسه یکتا |
| `user` | ForeignKey | مالک وظیفه |
| `list` | ForeignKey | لیست والد |
| `task_title` | CharField(255) | عنوان وظیفه |
| `task_description` | TextField | توضیحات (اختیاری) |
| `priority` | ChoiceField | low / medium / high |
| `status` | ChoiceField | todo / inprogress / done |
| `due_date` | DateTime | تاریخ سررسید (اختیاری) |
| `created_at` | DateTime | تاریخ ایجاد |
| `updated_at` | DateTime | تاریخ بروزرسانی |

**✅ Task**

| Field | Type | Description |
|---|---|---|
| `task_id` | AutoField | Unique ID |
| `user` | ForeignKey | Task owner |
| `list` | ForeignKey | Parent list |
| `task_title` | CharField(255) | Task title |
| `task_description` | TextField | Description (optional) |
| `priority` | ChoiceField | low / medium / high |
| `status` | ChoiceField | todo / inprogress / done |
| `due_date` | DateTime | Due date (optional) |
| `created_at` | DateTime | Created timestamp |
| `updated_at` | DateTime | Updated timestamp |

---

# 📝 Development Notes

## Code Quality Tools

```bash
# Format code with Black
black .

# Lint with Flake8
flake8 .

# Run tests
pytest -v

# Run all checks
black . && flake8 . && pytest -v
```

## Environment Variables (.env)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_HOST=redis
REDIS_PORT=6379
```

---

# 👤 نویسنده | Author

**Mohammad Yasin Jafari**

- GitHub: [@MY-Jafari](https://github.com/MY-Jafari)
- Project: [Todo-List-api](https://github.com/MY-Jafari/Todo-List-api)

---

# 📄 مجوز | License

This project is licensed under the MIT License. See [LICENSE](https://github.com/MY-Jafari/Todo-List-api/blob/main/LICENSE) for details.

---

<div align="center">

<sub>Made with ❤️ by MY-Jafari | First Django API Project</sub>

</div>
