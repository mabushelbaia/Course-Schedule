# Web UI for Course Schedule

## Overview

Add a web-based user interface to the existing Birzeit University course schedule
CLI tool, allowing users to upload schedule HTML files or fetch their schedule
live via FlareSolverr, and download the result as .ics (and optionally .csv).

The existing CLI (`main.py`) continues working independently. The web server is
a new entry point.

## Architecture

```
FastAPI + Jinja2 + HTMX
        │
        ▼
course_schedule/          ← reused as-is (no refactoring)
  ├─ main.py (Schedule)
  ├─ client.py (RitajClient)
  ├─ calendar.py (AcademicCalendar)
  ├─ config.py
  └─ cli.py
```

**New files:**
- `course_schedule/web/__init__.py` — FastAPI app factory, route definitions
- `course_schedule/web/models.py` — Pydantic request/response models
- `course_schedule/web/templates/` — Jinja2 templates
- `course_schedule/web/static/` — CSS file
- `Dockerfile` — production uvicorn image

**Modified files:**
- `pyproject.toml` — add fastapi, uvicorn, python-multipart, jinja2 deps
- `docker-compose.yml` — add web service alongside flaresolverr
- `main.py` — add `--serve` CLI flag to start web server

## Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Home page — choose mode (Upload / Live / Calendar) |
| GET | `/upload` | Upload page with file input |
| POST | `/upload` | Process uploaded HTML, return result partial |
| GET | `/live` | Live fetch page with credentials form |
| POST | `/live` | Login + fetch via FlareSolverr, return result partial |
| GET | `/calendar` | Academic calendar info + download |
| GET | `/download/ics/{uid}` | Download generated .ics file |
| GET | `/download/csv/{uid}` | Download generated .csv file (optional) |

## Screens

### Home (`/`)
Three option cards side by side: Upload HTML, Live Fetch, Academic Calendar.
Each describes the mode briefly. Clicking navigates to the respective route.

### Upload (`/upload`)
- File input accepting `.html` files
- HTMX: on submit, `hx-post="/upload" hx-target="#result" hx-swap="innerHTML"`
- Server returns a partial with:
  - Course table (code, title, section, days, time, room, instructor)
  - Download buttons for .ics and .csv
  - Or an error message if parsing failed

### Live Fetch (`/live`)
- Form fields: Ritaj username, password
- Submit triggers async FlareSolverr flow
- Loading state shown during fetch (HTMX polling or spinner)
- Same result partial as upload on success
- Error partial on failure (wrong credentials, network error) with retry button

### Calendar (`/calendar`)
- Shows detected semester info (Fall/Spring/Summer, start/end dates)
- Lists academic events (holidays, exams, deadlines)
- Download .ics button

## Data Flow

### Upload flow
1. User selects `.html` file and submits
2. HTMX POSTs the file to `/upload`
3. FastAPI reads file bytes, constructs `Schedule(html, start_date, end_date)`
4. `Schedule` parses HTML into DataFrame (existing code)
5. `to_ical()` generates Calendar object (existing code)
6. Result partial rendered with course info + download links
7. Download link: `GET /download/ics/{uid}` returns `.ics` as response

### Live fetch flow
1. User enters credentials and submits
2. HTMX POSTs JSON/form to `/live`
3. FastAPI creates `RitajClient`, calls `login()` then `fetch_schedule()`
4. Returns HTML string → same `Schedule` path as upload
5. Result partial returned

### Calendar flow
1. GET `/calendar` triggers `AcademicCalendar` fetch + parse
2. Semester info + events rendered in template
3. Download triggers `to_ical()` for calendar events

## Result Storage

Generated `.ics` and `.csv` files are stored temporarily in memory or a temp
directory, keyed by a UUID. The UUID is returned in the result partial and used
for the download endpoint. Files are cleaned up after a configurable timeout
(e.g. 30 minutes via a background task).

## Dependencies (to add)

- `fastapi`
- `uvicorn[standard]`
- `python-multipart`
- `jinja2` (bundled with fastapi)
- `aiofiles` (optional, for temp file management)

## Docker

**Dockerfile:**
```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev
COPY . .
CMD ["uvicorn", "course_schedule.web:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml addition:**
```yaml
web:
  build: .
  ports:
    - "8000:8000"
  environment:
    - FLARESOLVERR_URL=http://flaresolverr:8191/v1
    - START_DATE=${START_DATE}
    - END_DATE=${END_DATE}
    - RITAJ_USERNAME=${RITAJ_USERNAME}
    - RITAJ_PASSWORD=${RITAJ_PASSWORD}
  depends_on:
    - flaresolverr
```

## CLI Flag

`main.py` gains a `--serve` flag:

```bash
python main.py --serve           # start web server (default port 8000)
python main.py --serve --port 9000
```

This calls `uvicorn.run()` with the FastAPI app.

## Implementation Order

1. Add web dependencies to `pyproject.toml`
2. Create `course_schedule/web/__init__.py` with FastAPI app and routes
3. Create Jinja2 templates (base layout, home, upload, live, calendar, result partials)
4. Add CSS styling
5. Add `--serve` flag to `main.py`
6. Update `Dockerfile` and `docker-compose.yml`
7. Test end-to-end: upload mode, live mode, calendar mode
