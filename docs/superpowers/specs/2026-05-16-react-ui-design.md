# React + MUI Web UI for Course Schedule

## Overview

Replace the current Jinja2+HTMX frontend with a React Single Page Application
using Material UI (MUI) components. The FastAPI backend changes from returning
HTML partials to returning JSON, serving as a pure REST API.

The existing CLI (`main.py`) and core classes (`Schedule`, `RitajClient`,
`AcademicCalendar`) are unchanged.

## Architecture

```
┌──────────────────────┐     JSON API      ┌──────────────────────┐
│   React SPA (Vite)   │ ◄──────────────► │   FastAPI Backend    │
│   MUI Components     │   fetch/axios     │   REST endpoints     │
│                      │                   │                      │
│  frontend/            │                   │  course_schedule/web/ │
│   src/               │                   │   __init__.py        │
│    App.tsx           │                   │   (modified)         │
│    pages/            │                   │                      │
│    components/       │                   │  + existing classes  │
└──────────────────────┘                   └──────────────────────┘
```

- **Development:** Vite dev server (port 5173) proxies `/api` to FastAPI (port 8000)
- **Production:** Vite builds to `frontend/dist/`, served by FastAPI as static files

## Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| Primary | `#2e7d32` (MUI green) | Buttons, links, active nav |
| Primary light | `#e8f5e9` | Icon backgrounds, hover states |
| Background | `#f8faf8` | Page background |
| Surface | `#ffffff` | Cards, tables |
| Text | `#1a1a1a` | Body text |
| Text muted | `#666666` | Subtitles, secondary info |
| Border | `#e0e0e0` | Card borders, table dividers |

## Component Tree

```
App
├── ThemeProvider (MUI green theme)
└── BrowserRouter
    └── Layout
        ├── AppBar (fixed top bar)
        │   ├── Typography "Course Schedule"
        │   └── Tab navigation (Home / Upload / Live / Calendar)
        └── Container
            └── Routes
                ├── "/" → HomePage
                │   ├── HeroSection (title + subtitle)
                │   └── Card grid (3 cards)
                │       ├── UploadCard
                │       ├── LiveFetchCard
                │       └── CalendarCard
                │
                ├── "/upload" → UploadPage
                │   ├── PageHeader
                │   ├── FileDropzone (drag & drop + click)
                │   ├── [loading] CircularProgress
                │   ├── [result]  ScheduleTable
                │   │              └── DownloadButtons (.ics + .csv)
                │   └── [error]  Alert
                │
                ├── "/live" → LivePage
                │   ├── PageHeader
                │   ├── CredentialsForm (username + password TextFields)
                │   ├── [loading] CircularProgress
                │   ├── [result]  ScheduleTable + DownloadButtons
                │   └── [error]  Alert
                │
                └── "/calendar" → CalendarPage
                    ├── PageHeader
                    ├── [semester] SemesterCard
                    ├── CalendarTable
                    └── DownloadButtons
```

## API Endpoints (Backend Changes)

Current routes change from returning `HTMLResponse` to returning JSON.
Error responses use consistent `{ "detail": "..." }` format.

| Method | Route | Request | Response |
|--------|-------|---------|----------|
| GET | `/api/` | — | `{ "status": "ok" }` |
| POST | `/api/upload` | FormData: `file` (`.html`) | `{ "id": "uuid", "courses": [...], "filename": "..." }` |
| POST | `/api/live` | JSON: `{ "username", "password" }` | `{ "id": "uuid", "courses": [...], "filename": "..." }` |
| GET | `/api/calendar` | — | `{ "academic_year": [2025,2026], "semester": {...}, "events": [...], "id": "uuid" }` |
| GET | `/api/download/{id}` | — | Binary `.ics` file download |
| GET | `/api/download/{id}/csv` | — | Binary `.csv` file download |
| GET | `/api/health` | — | `{ "status": "ok" }` |

Response types:
- `courses`: `[{ "Course Label": string, "Course Title": string, "Section": string, "Days": string, "Time": string, "Room": string }]`
- `events`: `[{ "date": "2025-09-01", "end_date": "2025-09-15", "title": string }]`
- `semester`: `{ "name": string, "start_date": "2025-09-01T00:00:00", "end_date": "2025-12-31T00:00:00" }` or `null`

## Frontend Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api.ts              (all fetch calls to backend)
│   ├── theme.ts            (MUI green theme)
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── UploadPage.tsx
│   │   ├── LivePage.tsx
│   │   └── CalendarPage.tsx
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── FileDropzone.tsx
│   │   ├── CredentialsForm.tsx
│   │   ├── ScheduleTable.tsx
│   │   ├── CalendarTable.tsx
│   │   ├── DownloadButtons.tsx
│   │   ├── SemesterCard.tsx
│   │   └── ErrorAlert.tsx
│   └── types.ts            (TypeScript interfaces)
```

## Data Flow

### Upload flow
1. User drops/selects file in `FileDropzone`
2. `UploadPage` POSTs FormData to `/api/upload`
3. Backend reads file, calls `Schedule(html, start, end)` → `to_ical()`
4. Returns JSON with `{ id, courses, filename }`
5. React renders `ScheduleTable` with course data, `DownloadButtons` link to `/api/download/{id}`

### Live fetch flow
1. User fills `CredentialsForm` (username, password)
2. `LivePage` POSTs JSON to `/api/live`
3. Backend creates `RitajClient`, logs in, fetches HTML, builds schedule
4. Returns same JSON format as upload
5. React renders same result components

### Calendar flow
1. `CalendarPage` mounts, GETs `/api/calendar`
2. Backend fetches academic calendar via FlareSolverr, parses events
3. Returns JSON with semester info + events list
4. React renders `SemesterCard` + `CalendarTable`

## Production Build

The Vite build outputs static files to `frontend/dist/`. The FastAPI app serves
these as static files and handles `/api/*` routes for data.

```python
# In course_schedule/web/__init__.py
from fastapi.staticfiles import StaticFiles

# Serve React SPA
app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
```

The Dockerfile builds both stages:
1. Node stage: `npm install && npm run build`
2. Python stage: serves the built files

## State & Security

- **Credentials**: Sent as JSON POST body. Use HTTPS in production (reverse proxy
  with TLS). Local-only use is safe without TLS.
- **Results storage**: In-memory dict with UUID keys, FIFO eviction at 100 entries.
  Same as current implementation — no cross-user contamination since each request
  creates isolated `RitajClient` sessions.
- **No auth**: The app has no user accounts. The results dict is shared but
  UUID-based keys prevent casual access.

## Files to Change

**Modified:**
- `course_schedule/web/__init__.py` — routes change to JSON API, add `/api/` prefix
- `main.py` — update `--serve` to also serve frontend (no change needed, just CORS)

**New:**
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/api.ts`
- `frontend/src/theme.ts`
- `frontend/src/types.ts`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/UploadPage.tsx`
- `frontend/src/pages/LivePage.tsx`
- `frontend/src/pages/CalendarPage.tsx`
- `frontend/src/components/Layout.tsx`
- `frontend/src/components/FileDropzone.tsx`
- `frontend/src/components/CredentialsForm.tsx`
- `frontend/src/components/ScheduleTable.tsx`
- `frontend/src/components/CalendarTable.tsx`
- `frontend/src/components/DownloadButtons.tsx`
- `frontend/src/components/SemesterCard.tsx`
- `frontend/src/components/ErrorAlert.tsx`

**Deleted or deprecated:**
- `course_schedule/web/templates/` — Jinja2 templates no longer needed
- `course_schedule/web/static/` — hand-written CSS no longer needed

## Implementation Order

1. Refactor backend routes to JSON API
2. Scaffold React app with Vite + MUI
3. Build Layout + theme
4. Build HomePage
5. Build UploadPage (FileDropzone, ScheduleTable, DownloadButtons)
6. Build LivePage (CredentialsForm, result components)
7. Build CalendarPage (SemesterCard, CalendarTable)
8. Wire up production build (FastAPI serves React build)
9. Update Dockerfile for multi-stage build
10. Update tests
