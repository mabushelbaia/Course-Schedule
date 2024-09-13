import io
import os
import secrets

import fastapi
from fastapi import File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from starlette.middleware.sessions import SessionMiddleware


from package.main import Schedule
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google_auth_oauthlib.flow import Flow
from package import CURRENT_SEMESTER
from utils import create_calendar

# Setup
secret_key = secrets.token_hex(32)
app = fastapi.FastAPI()
app.add_middleware(SessionMiddleware, secret_key=secret_key)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Disable HTTPS requirement for local testing

CLIENT_SECRET_FILE = "secret.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
REDIRECT_URI = "http://localhost:8000/callback"

flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI)

@app.get("/", response_class=HTMLResponse)
async def index():
    return fastapi.responses.FileResponse("templates/index.html")

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "Missing authorization code"}, status_code=400)

    ical_data = request.session.get("ical_data")
    if not ical_data:
        return JSONResponse({"error": "No iCal data available"}, status_code=400)

    flow.fetch_token(code=code)
    credentials = flow.credentials

    calendar_id = await create_calendar(credentials, CURRENT_SEMESTER + " Schedule", ical_data)
    if calendar_id:
        return RedirectResponse("/")

@app.get("/authorize")
async def authorize():
    authorization_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(authorization_url)

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    schedule = Schedule(file.file)
    ical_data = schedule.to_ical()
    
    # Store ical_data as a base64 encoded string
    request.session["ical_data"] = ical_data.decode('utf-8')
    return {"message": "File uploaded successfully"}

@app.get("/download")
async def get_file(request: Request):
    ical_data_str = request.session.get("ical_data")
    if not ical_data_str:
        return JSONResponse({"error": "No file uploaded"}, status_code=400)
    
    # Convert string back to bytes
    ical_data_bytes = ical_data_str.encode('utf-8')
    return StreamingResponse(io.BytesIO(ical_data_bytes), media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=calendar.ics"})

@app.get("/create_calendar")
async def create_calendar_route(request: Request):
    authorization_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(authorization_url)
