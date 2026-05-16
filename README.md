# Course Schedule

Convert Birzeit University (Ritaj) course schedules to iCalendar format.

## Features

- **File mode** — parse an exported HTML schedule file into `.ics` + optional `.csv`
- **Live mode** — log into Ritaj via FlareSolverr and fetch the schedule automatically
- **Academic calendar** — automatically fetches and merges all academic calendar events (holidays, exam periods, registration deadlines) into the `.ics`
- **Semester auto-detection** — detects the current semester from the academic calendar and auto-sets START_DATE/END_DATE for course RRULEs
- **Separate or merged output** — academic calendar events in the same `.ics` as courses, or in their own file
- **Interactive prompts** — no args needed, just run the tool and follow the prompts

## Usage

### Quick start (interactive)

```bash
python main.py
```

Prompts for credentials, semester, calendar options, and output path — then runs live mode.

### File mode

```bash
python main.py schedule.html -o my_schedule.ics --csv
```

### Live mode

```bash
python main.py --live -o schedule.ics
```

### With academic calendar

```bash
# Merged into one file (default)
python main.py --live -o schedule.ics --calendar merged

# Separate files
python main.py --live -o schedule.ics --calendar separate --calendar-output calendar.ics

# Skip calendar events
python main.py --live -o schedule.ics --no-calendar
```

### Force a specific semester

```bash
python main.py --live --semester Fall
```

## CLI Reference

| Flag | Description |
|------|-------------|
| `html` | Path to HTML file (optional with `--live`, not needed in interactive) |
| `-o`, `--output` | Output `.ics` filename (default: `schedule.ics`) |
| `--csv` | Also export as CSV |
| `--live` | Fetch schedule live from Ritaj via FlareSolverr |
| `--interactive` | Run interactive prompts |
| `--username` | Ritaj username (env: `RITAJ_USERNAME`) |
| `--password` | Ritaj password (env: `RITAJ_PASSWORD`) |
| `--flaresolverr-url` | FlareSolverr URL (default: `http://localhost:8191/v1`) |
| `--no-calendar` | Skip academic calendar events |
| `--semester` | Force semester (`Fall`, `Spring`, `Summer`) |
| `--calendar` | `merged` (default) or `separate` |
| `--calendar-output` | Calendar `.ics` path (only with `--calendar separate`) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RITAJ_USERNAME` | For `--live` | Ritaj username |
| `RITAJ_PASSWORD` | For `--live` | Ritaj password |
| `START_DATE` | For file mode | Semester start date (DD-MM-YYYY) |
| `END_DATE` | For file mode | Semester end date (DD-MM-YYYY) |
| `FLARESOLVER_URL` | For `--live` | FlareSolverr URL (default: `http://localhost:8191/v1`) |

## Docker (FlareSolverr only)

The tool itself runs natively with Python. FlareSolverr runs in Docker.

```bash
docker compose up -d flaresolverr
```

## Installation

Requires Python 3.12+ and uv or pip.

```bash
uv sync
```

Or with pip:

```bash
pip install .
```
