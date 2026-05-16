import datetime
import logging
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from icalendar import Calendar as ICalendar

from course_schedule import Schedule, AcademicCalendar
from course_schedule.client import RitajClient, RitajError, fetch_academic_calendar
from course_schedule.config import START_DATE, END_DATE

logger = logging.getLogger(__name__)

app = FastAPI(title="Course Schedule API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
FRONTEND_DIST = BASE_DIR.parent.parent / "frontend" / "dist"

results: dict[str, dict] = {}


def _resolve_dates(calendar_html: str | None = None) -> tuple[datetime.datetime, datetime.datetime]:
    if calendar_html:
        try:
            cal = AcademicCalendar(calendar_html)
            semester = cal.detect_current_semester()
            if semester:
                return semester.start_date, semester.end_date
        except Exception as e:
            logger.warning("Semester detection failed: %s", e)
    if START_DATE and END_DATE:
        return START_DATE, END_DATE
    raise HTTPException(status_code=400, detail="Semester dates not available.")


def _build_schedule_internal(html: str, start_date: datetime.datetime, end_date: datetime.datetime) -> dict:
    schedule = Schedule(html, start_date=start_date, end_date=end_date)
    ical = schedule.to_ical()
    result_id = str(uuid.uuid4())
    results[result_id] = {"ical": ical.to_ical()}
    while len(results) > 100:
        results.pop(next(iter(results)))
    return {
        "id": result_id,
        "courses": schedule.df.fillna("").to_dict(orient="records"),
        "filename": f"schedule-{result_id[:8]}.ics",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_submit(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".html"):
        raise HTTPException(status_code=400, detail="Please upload an .html file.")
    content = (await file.read()).decode("utf-8", errors="replace")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum is 10MB.")
    try:
        start_date, end_date = _resolve_dates()
        return _build_schedule_internal(content, start_date, end_date)
    except (ValueError, HTTPException) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/live")
async def live_submit(username: str = Form(...), password: str = Form(...)):
    flaresolverr_url = os.environ.get("FLARESOLVERR_URL", "http://localhost:8191/v1")

    calendar_html = None
    try:
        calendar_html = await fetch_academic_calendar(flaresolverr_url)
    except Exception as e:
        logger.warning("Failed to fetch academic calendar: %s", e)

    try:
        start_date, end_date = _resolve_dates(calendar_html)
    except HTTPException:
        raise HTTPException(status_code=400, detail="Could not detect semester dates.")

    client = RitajClient(flaresolverr_url=flaresolverr_url, username=username, password=password)
    try:
        await client.login()
        schedule_html = await client.fetch_schedule()
    except RitajError as e:
        raise HTTPException(status_code=401, detail=str(e))
    finally:
        await client.close()

    try:
        return _build_schedule_internal(schedule_html, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse schedule: {e}")


@app.get("/api/calendar")
async def calendar_data():
    flaresolverr_url = os.environ.get("FLARESOLVERR_URL", "http://localhost:8191/v1")
    try:
        calendar_html = await fetch_academic_calendar(flaresolverr_url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch calendar: {e}")

    cal = AcademicCalendar(calendar_html)
    semester = cal.detect_current_semester()

    cal_ical = ICalendar()
    cal_ical.add("version", "2.0")
    cal_ical.add("prodid", "-//Birzeit University//Academic Calendar//EN")
    cal_ical.add("calscale", "GREGORIAN")
    cal.add_to_ical(cal_ical)

    cal_id = str(uuid.uuid4())
    results[cal_id] = {"ical": cal_ical.to_ical(), "prefix": "calendar"}

    return {
        "id": cal_id,
        "academic_year": cal.academic_year,
        "semester": {
            "name": semester.name,
            "start_date": semester.start_date.isoformat(),
            "end_date": semester.end_date.isoformat(),
        } if semester else None,
        "events": [
            {
                "date": e.date.isoformat(),
                "end_date": e.end_date.isoformat() if e.end_date and e.end_date != e.date else None,
                "title": e.title,
            }
            for e in cal.events
        ],
    }


@app.get("/api/download/{result_id}")
async def download(result_id: str):
    entry = results.get(result_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Result not found.")
    prefix = entry.get("prefix", "schedule")
    return Response(
        content=entry["ical"],
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{prefix}-{result_id[:8]}.ics"',
            "Cache-Control": "no-store",
        },
    )


@app.get("/api/{path:path}")
async def api_404(path: str):
    raise HTTPException(status_code=404, detail="Not found")


# Optional: serve React SPA in production
_frontend_index = FRONTEND_DIST / "index.html"
if _frontend_index.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
