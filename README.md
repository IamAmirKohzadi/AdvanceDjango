# AdvanceDjango

Backend practice project built with Django + DRF, focused on production-style fundamentals:

- Custom user model (email-based auth)
- JWT authentication (SimpleJWT)
- DRF global defaults (auth, permissions, filtering, pagination)
- OpenAPI docs (drf-spectacular)

## Tech Stack

- Python
- Django
- Django REST Framework
- SimpleJWT
- drf-spectacular
- django-filter
- django-cors-headers
- SQLite (current local DB)

## Project Structure

```text
.
├── accounts/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```

## Setup

### 1) Create and activate virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3) Create `.env`

Create `.env` in project root:

```env
DJANGO_SECRET_KEY=replace-with-a-real-secret
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

### 4) Run migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5) Create superuser and run server

```powershell
python manage.py createsuperuser
python manage.py runserver
```

## Authentication

This project uses JWT for API auth.

Flow:

1. Register user at `POST /api/auth/register/`
2. Obtain tokens at `POST /api/token`
3. Use access token in `Authorization` header:
   `Bearer <access_token>`
4. Call protected endpoint `GET /api/auth/me/`

## API Endpoints

- `POST /api/auth/register/` - register new user
- `GET /api/auth/me/` - current authenticated user
- `POST /api/token` - obtain JWT access/refresh tokens
- `POST /api/token/refresh` - refresh access token
- `GET /api/schema` - OpenAPI schema
- `GET /api/docs` - Swagger UI
- `GET /api/redoc` - ReDoc UI

## Admin

- Admin URL: `/admin/`
- Custom user model: `accounts.User`

## Notes

- Global DRF defaults are configured in `core/settings.py`.
- Default API permission is authenticated-only (`IsAuthenticated`), with explicit exceptions per view (e.g. register).
