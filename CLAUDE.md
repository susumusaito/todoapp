# CLAUDE.md

## Project Overview

A task management (ToDo) web application with AI coaching powered by Google Gemini. Built with Python/FastAPI, server-side rendered with Jinja2 templates, and uses HTMX for dynamic interactions. The UI is in Japanese.

## Tech Stack

- **Backend**: Python 3, FastAPI, SQLModel (SQLAlchemy + Pydantic)
- **Database**: SQLite (`todo.db`, auto-created on startup)
- **Templates**: Jinja2 with HTMX for partial page updates
- **Frontend**: Tailwind CSS + DaisyUI (via CDN), HTMX v2 (via CDN)
- **AI**: Google Gemini API (`google-genai` SDK)

## Project Structure

```
app/
├── main.py          # FastAPI routes and app setup
├── models.py        # SQLModel database models (Todo, AiCoachLog)
├── database.py      # Database engine and session management
├── ai_coach.py      # Gemini API integration for coaching advice
└── templates/
    ├── base.html        # Base layout (CDN imports, nav)
    ├── dashboard.html   # Main single-page dashboard
    └── partials/        # HTMX partial response templates
        ├── todo_form.html
        ├── todo_list.html
        ├── todo_list_with_stats.html
        ├── todo_row.html
        ├── stats.html
        └── ai_coach.html
```

## Setup & Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Then set GEMINI_API_KEY
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-2.0-flash-lite` | Gemini model name |

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Dashboard (full page) |
| POST | `/todos` | Create todo (returns HTMX partial) |
| PUT | `/todos/{id}` | Update todo (returns HTMX partial) |
| DELETE | `/todos/{id}` | Delete todo (returns HTMX partial) |
| POST | `/ai-coach/generate` | Generate AI coaching advice |

## Key Conventions

- **Status values**: `未着手` (not started), `進行中` (in progress), `完了` (done)
- **Priority values**: `高` (high), `中` (medium), `低` (low)
- **Progress**: Integer 0-100
- **HTMX pattern**: Mutation endpoints return `partials/todo_list_with_stats.html` which uses out-of-band (OOB) swaps to update both the list and stats areas
- **Database sessions**: Injected via FastAPI `Depends(get_session)`
- **No frontend build step**: All CSS/JS loaded from CDN

## Testing & Linting

No test suite or linting tools are currently configured. If adding tests, use `pytest` with `httpx` for FastAPI test client support.

## Important Notes

- The AI coach has retry logic (3 attempts) for rate-limited (429) responses with exponential backoff
- AI token output capped at 256 tokens, temperature 0.7
- Task summaries sent to AI are limited to 10 tasks
- SQLite database file (`todo.db`) is gitignored
- No database migration system; schema changes require deleting `todo.db`
