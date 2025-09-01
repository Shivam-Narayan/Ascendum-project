# Copilot Instructions for AI Agents

## Project Overview
- This is a Django-based backend project for chatbot and AI analyst features.
- Main app: `ai_analyst_backend` (Django project root)
- Key Django app: `chatbot` (contains models, views, admin, migrations)

## Architecture & Data Flow
- Django standard structure: `manage.py` for commands, `settings.py` for config, `urls.py` for routing.
- All business logic for chatbot features lives in `chatbot/`.
- Models are defined in `chatbot/models.py` and managed via Django ORM.
- Migrations are tracked in `chatbot/migrations/`.

## Developer Workflows
- **Run server:**
  ```
  python manage.py runserver
  ```
- **Apply migrations:**
  ```
  python manage.py makemigrations
  python manage.py migrate
  ```
- **Run tests:**
  ```
  python manage.py test
  ```
- **Create superuser:**
  ```
  python manage.py createsuperuser
  ```

## Project Conventions
- Models use Django ORM fields (e.g., `CharField`, `EmailField`).
- All business logic should be placed in the appropriate Django app (`chatbot`).
- Use Django's built-in authentication and admin where possible.
- Keep migrations in sync with model changes.

## Integration Points
- No external APIs or services are referenced in the current codebase.
- All configuration is handled via `settings.py`.

## Key Files & Directories
- `ai_analyst_backend/settings.py`: Django settings
- `ai_analyst_backend/urls.py`: URL routing
- `chatbot/models.py`: Data models
- `chatbot/views.py`: Business logic endpoints
- `chatbot/migrations/`: Database migrations

## Example Patterns
- To add a new model, define it in `chatbot/models.py` and run migrations.
- To expose new endpoints, add views in `chatbot/views.py` and update `urls.py`.

---
If you are unsure about a workflow or pattern, check the Django documentation or inspect the corresponding file in this project.
