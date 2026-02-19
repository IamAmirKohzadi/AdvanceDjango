# AdvanceDjango

Backend practice project built with Django + DRF.

Current scope:
- Custom user model (`accounts.User`) with email login
- JWT auth with SimpleJWT
- Tasks CRUD module
- Filtering, search, ordering, and pagination
- Write throttling on task write actions
- OpenAPI docs with drf-spectacular

## Stack

- Python
- Django
- Django REST Framework
- djangorestframework-simplejwt
- django-filter
- drf-spectacular
- django-cors-headers
- SQLite (local development)

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create `.env` in project root:

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Run project:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Docs

- Swagger UI: `GET /api/docs`
- ReDoc: `GET /api/redoc`
- OpenAPI schema: `GET /api/schema`

## Auth Flow

1. Register: `POST /api/auth/register/`
2. Get tokens: `POST /api/token`
3. Refresh token: `POST /api/token/refresh`
4. Use access token in header:
`Authorization: Bearer <access_token>`
5. Current user: `GET /api/auth/me/`

## Task Endpoints

Base path: `/api/tasks/`

- `GET /api/tasks/` list current user's tasks
- `POST /api/tasks/` create task
- `GET /api/tasks/{id}/` retrieve task
- `PATCH /api/tasks/{id}/` partial update
- `PUT /api/tasks/{id}/` full update
- `DELETE /api/tasks/{id}/` delete task

Query features:
- Filter: `?status=todo|in_progress|done`
- Search: `?search=<text>` on `title`, `description`
- Ordering: `?ordering=created_date|due_date|updated_date`
- Desc ordering: `?ordering=-created_date`
- Pagination: page-number pagination enabled globally (`PAGE_SIZE=10`)

## Permissions and Throttling

- Task API permission: authenticated users can write, unauthenticated users are read-only.
- Task object rule: owner can modify; staff/superuser can modify
- Task write throttling scope: `task_write`
- Current write rate: `20/hour` for `create`, `update`, `partial_update`, `destroy`

## Testing

Run task tests:

```powershell
python manage.py test tasks
```

Current `tasks` test suite covers:
- auth-required create
- authenticated create
- user-scoped list
- owner update allowed
- non-owner update blocked
- owner delete allowed
- non-owner delete blocked
- status filtering
- search by title and description
- ordering by `created_date` asc/desc
- write throttling for create and update paths

## Admin

- Admin URL: `/admin/`
- Registered models:
- `accounts.User`
- `tasks.Task`
