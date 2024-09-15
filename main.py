import io
import logging
import os
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google_auth_oauthlib.flow import Flow
from package.main import Schedule
from package import CURRENT_SEMESTER
from package.utils import create_calendar
from dotenv import find_dotenv, load_dotenv

# Setup
app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

load_dotenv(find_dotenv())

CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE")
SCOPES = [os.getenv("SCOPES")]
REDIRECT_URI = os.getenv("REDIRECT_URI")

flow = Flow.from_client_secrets_file(
    CLIENT_SECRET_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/callback")
async def callback(request: Request, state: str, code: str):
    if not code:
        return JSONResponse({"error": "Missing authorization code"}, status_code=400)

    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Retrieve iCal data from the state parameter
    import base64
    ical_data = base64.b64decode(state).decode('utf-8')

    calendar_id, events_count = await create_calendar(
        credentials, CURRENT_SEMESTER + " Schedule", ical_data
    )
    if calendar_id:
        message = f"Calendar created successfully with {events_count} events"
    else:
        message = "Failed to create calendar"

    # Redirect to the home page with a query parameter
    return RedirectResponse(f"/?message={message}")

@app.get("/authorize")
async def authorize(ical_data: str):
    import base64
    state = base64.b64encode(ical_data.encode('utf-8')).decode('utf-8')
    authorization_url, _ = flow.authorization_url(prompt="consent", state=state)
    return RedirectResponse(authorization_url)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        schedule = Schedule(file.file)
        ical_data = schedule.to_ical()
        return JSONResponse({"ical_data": ical_data.decode('utf-8')}, status_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/download")
async def get_file(request: Request):
    logger.info("Download request received")
    ical_data = request.query_params.get("ical_data")
    logger.info(f"Received ical_data: {ical_data[:100] if ical_data else None}")  # Log first 100 chars for privacy
    
    if not ical_data:
        logger.error("No iCal data provided in the request")
        return JSONResponse({"error": "No iCal data provided"}, status_code=400)
    
    try:
        return StreamingResponse(
            io.BytesIO(ical_data.encode('utf-8')),
            media_type="text/calendar",
            headers={"Content-Disposition": "attachment; filename=calendar.ics"},
        )
    except Exception as e:
        logger.exception("Error occurred while processing download request")
        return JSONResponse({"error": str(e)}, status_code=500)