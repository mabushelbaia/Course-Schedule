import io
import fastapi
from fastapi.responses import StreamingResponse
from package.main import Schedule
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = fastapi.FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/")
def index():
    return fastapi.responses.FileResponse("templates/index.html")


@app.post("/upload")
async def upload_file(file: fastapi.UploadFile = fastapi.File(...)):

    schedule = Schedule(file.file)
    buffer = io.BytesIO(schedule.to_ical())
    buffer.seek(0)

    # Return the iCal content as a downloadable file
    return StreamingResponse(
        buffer,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=calendar.ics"},
    )
