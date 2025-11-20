# StyleGenie Backend (Django + DRF)

Backend for the StyleGenie platform. Provides dual-role auth (client + stylist), wardrobe management, AI-powered outfit recommendations, and documented REST endpoints for the React frontend.

## What's inside
- Custom `accounts.User` with roles (`client`, `stylist`, `admin`) and JWT auth via SimpleJWT.
- Client flows: register/login/logout, password reset/change, style profile (gender, skin tone, body/face shape), and Cloudinary-backed wardrobe CRUD.
- Stylist flows: register/login/logout, password reset/change, profile w/ bio, expertise tags, experience, and ratings counters.
- AI recommendations: LangChain + Gemini agent (`agents/style_agent.py`) wrapping a structured prompt to return 5 outfits from the user's wardrobe.
- API docs + health: `/api/schema/`, `/api/docs/`, `/api/redoc/`, and `/health/` with DB + env metadata.
- Environment-specific settings (`core/settings/dev|prod|test.py`) and Docker Compose for Django + Postgres.

## Prerequisites
- Python 3.11+
- PostgreSQL 13+ (dev/prod) or SQLite (tests)
- Redis (if you enable Celery workers)
- Optional: Docker + docker-compose for containerized runs

## Project layout
- `core/` – settings, urls, health endpoint, Celery bootstrap.
- `accounts/` – custom user model with roles + JWT.
- `client/` – onboarding, profile, wardrobe CRUD, stylist browse.
- `stylist/` – stylist auth/profile + password flows.
- `recommendations/` – AI orchestration + LangChain agent wiring.
- `common/` – shared permissions and JWT/email utilities.

## Quickstart (local)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # or Scripts\activate on Windows
pip install -r requirements.txt
```

Create `backend/.env` (example values):
```ini
DJANGO_SETTINGS_MODULE=core.settings.dev
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (dev uses Postgres; tests default to sqlite)
DB_NAME=stylegenie
DB_USER=postgres
DB_PASS=postgres
DB_HOST=localhost
DB_PORT=5432

# Async workers (optional if you wire Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Frontend + CORS/CSRF
FRONTEND_URL=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
CORS_ALLOWED_ORIGINS=http://localhost:5173
CORS_ALLOW_ALL_ORIGINS=True

# Agents / health metadata
GOOGLE_API_KEY=<gemini-key>
APP_VERSION=1.0.0
DJANGO_ENV=development
```

Run migrations and start the API:
```bash
python manage.py migrate
python manage.py createsuperuser  # optional admin for /admin/
python manage.py runserver 0.0.0.0:8000
```

Useful commands:
- `python manage.py test`
- `python manage.py check --deploy` (sanity checks for prod settings)
- `celery -A core worker -l info` (if you enable Redis/Celery)
- `python manage.py shell` for quick debugging

## Running with Docker
```bash
cd backend
docker-compose up --build
```
`docker-compose.yml` runs Django against a Postgres service and executes migrations. The command string references `python manage.py wait_for_db`; add that management command or remove the line if you do not need a wait loop.

## Environment reference (backend)
| Key | Description | Example |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | Which settings file to load | `core.settings.prod` |
| `SECRET_KEY` | Django secret key | `generate-a-strong-key` |
| `DEBUG` | Toggle debug mode | `False` in prod |
| `ALLOWED_HOSTS` | Comma-separated hosts | `api.stylegenie.com,localhost` |
| `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT` | Postgres credentials | `stylegenie`, `postgres`, `postgres`, `db`, `5432` |
| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | Redis endpoints for Celery | `redis://redis:6379/0` |
| `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, `CORS_ALLOW_ALL_ORIGINS` | Frontend hosts allowed | `https://app.stylegenie.com` |
| `GOOGLE_API_KEY` | Gemini API key for the stylist agent | `ya29....` |
| `APP_VERSION`, `DJANGO_ENV` | Exposed in `/health/` | `1.2.0`, `production` |

## Production checklist
- Use `DJANGO_SETTINGS_MODULE=core.settings.prod` and `DEBUG=False`.
- Set `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `CORS_ALLOWED_ORIGINS` to your domains.
- Serve static files with WhiteNoise (already configured in `prod.py`) and run `python manage.py collectstatic` during deploy.
- Run with a WSGI server (e.g., `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT`).
- Ensure Postgres + Redis are reachable; mount persistent volumes for both if using containers.
- Rotate `SECRET_KEY` carefully; invalidates sessions.
- Configure HTTPS termination at your proxy/load balancer and keep `SECURE_*` settings enabled.

## Migrations & data
- Apply migrations on every deploy: `python manage.py migrate`.
- Add migrations when changing models: `python manage.py makemigrations <app>`.
- Seed data through Django admin or custom management commands (none bundled yet).

## API surface (selected)
- `GET /health/` – app + DB heartbeat with env/version.
- Docs: `GET /api/schema/`, `GET /api/docs/`, `GET /api/redoc/`.
- Client auth: `POST /client/auth/register/`, `POST /client/auth/login/`, `POST /client/auth/logout/`, `POST /client/auth/token/refresh/`.
- Client profile/security: `GET/PATCH /client/me/`, `POST /client/auth/change-password/`, `POST /client/auth/send-reset-password-email/`, `POST /client/auth/reset-password/<uidb64>/<token>/`.
- Wardrobe: `GET/POST /client/wardrobe/`, `GET/PATCH/DELETE /client/wardrobe/{id}/` (scoped to the authenticated client).
- Stylist browse: `GET /client/stylists/` (public listing for clients).
- Outfit recommendations: `POST /client/recommendations/` with body:
  ```json
  {
    "destination": "Dhaka",
    "occasion": "wedding",
    "datetime": "2024-12-01T18:30:00Z",
    "drawer_products": [
      {"id": 1, "title": "Navy Blazer", "color": "blue", "category": "top"}
    ]
  }
  ```
  If `drawer_products` is omitted, the service pulls the user's `WardrobeItem` rows and feeds them to the Gemini stylist agent.
- Stylist auth/profile: `POST /stylist/auth/register/`, `POST /stylist/auth/login/`, `POST /stylist/auth/logout/`, `POST /stylist/auth/token/refresh/`, `GET/PATCH /stylist/me/`, password change/reset endpoints.

## Data model snapshot
- `accounts.User` – email login, roles (client/stylist/admin), status, phone, profile picture, staff flags.
- `client.ClientProfile` – date of birth + style attributes (gender, skin tone, body/face shape).
- `client.WardrobeItem` – user-owned closet items with title, color, category, description, and image URL.
- `stylist.StylistProfile` – bio, expertise tags (JSON), years of experience, ratings, and earnings counters.

## Agents / recommendations
- `recommendations/services.py` validates client profile, pulls drawer items from the DB, and builds a `StylistRequestPayload`.
- `agents/style_agent.py` uses LangChain + Gemini (`GOOGLE_API_KEY`) to return structured `AIRecommendations` (5 outfits, each with `product_ids`).
- The response is re-validated by `RecommendResponseSerializer` before returning to the client.

## Notes
- Dev settings target Postgres; test settings (`core/settings/test.py`) use sqlite. Switch via `DJANGO_SETTINGS_MODULE`.
- JWT blacklisting is enabled; password change/reset revokes outstanding tokens.
- Customize CORS/CSRF lists to match your frontend host(s).
