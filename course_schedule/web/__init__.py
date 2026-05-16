import datetime
import logging
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from icalendar import Calendar as ICalendar

from course_schedule import Schedule, AcademicCalendar
from course_schedule.client import RitajClient, RitajError, fetch_academic_calendar
from course_schedule.config import START_DATE, END_DATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Course Schedule")

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

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
    raise HTTPException(
        status_code=400,
        detail="Semester dates not available. Set START_DATE/END_DATE env vars.",
    )


def _build_schedule_internal(html: str, start_date: datetime.datetime, end_date: datetime.datetime) -> dict:
    schedule = Schedule(html, start_date=start_date, end_date=end_date)
    ical = schedule.to_ical()
    result_id = str(uuid.uuid4())
    results[result_id] = {
        "ical": ical.to_ical(),
        "df": schedule.df,
    }
    return {
        "id": result_id,
        "courses": schedule.df.to_dict(orient="records"),
        "filename": f"schedule-{result_id[:8]}.ics",
    }


# ── Routes ──────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload_submit(request: Request, file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".html"):
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "message": "Please upload an .html file."},
        )
    html_content = (await file.read()).decode("utf-8")
    try:
        start_date, end_date = _resolve_dates()
        result = _build_schedule_internal(html_content, start_date, end_date)
    except (ValueError, HTTPException) as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "message": str(e)},
        )
    return templates.TemplateResponse("partials/result.html", {"request": request, **result})


@app.get("/live", response_class=HTMLResponse)
async def live_form(request: Request):
    return templates.TemplateResponse("live.html", {"request": request})


@app.post("/live", response_class=HTMLResponse)
async def live_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    flaresolverr_url = os.environ.get("FLARESOLVERR_URL", "http://localhost:8191/v1")

    calendar_html = None
    try:
        calendar_html = await fetch_academic_calendar(flaresolverr_url)
    except Exception as e:
        logger.warning("Failed to fetch academic calendar: %s", e)

    try:
        start_date, end_date = _resolve_dates(calendar_html)
    except HTTPException:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "message": "Could not detect semester dates and no START_DATE/END_DATE set."},
        )

    client = RitajClient(flaresolverr_url=flaresolverr_url, username=username, password=password)
    try:
        await client.login()
        schedule_html = await client.fetch_schedule()
    except RitajError as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "message": str(e)},
        )
    finally:
        await client.close()

    try:
        result = _build_schedule_internal(schedule_html, start_date, end_date)
    except ValueError as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "message": f"Failed to parse schedule: {e}"},
        )
    return templates.TemplateResponse("partials/result.html", {"request": request, **result})


@app.get("/calendar", response_class=HTMLResponse)
async def calendar_page(request: Request):
    flaresolverr_url = os.environ.get("FLARESOLVERR_URL", "http://localhost:8191/v1")
    try:
        calendar_html = await fetch_academic_calendar(flaresolverr_url)
    except Exception as e:
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "message": f"Failed to fetch calendar: {e}"},
        )

    cal = AcademicCalendar(calendar_html)
    semester = cal.detect_current_semester()

    cal_ical = ICalendar()
    cal_ical.add("version", "2.0")
    cal_ical.add("prodid", "-//Birzeit University//Academic Calendar//EN")
    cal_ical.add("calscale", "GREGORIAN")
    cal.add_to_ical(cal_ical)

    cal_id = str(uuid.uuid4())
    results[cal_id] = {"ical": cal_ical.to_ical()}

    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "semester": semester,
        "events": cal.events,
        "academic_year": cal.academic_year,
        "cal_id": cal_id,
    })


@app.get("/download/{result_id}")
async def download(result_id: str):
    entry = results.get(result_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Result not found or expired.")
    return Response(
        content=entry["ical"],
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="schedule-{result_id[:8]}.ics"'},
    )
