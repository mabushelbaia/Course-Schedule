from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icalendar import Calendar


async def create_calendar(credentials: Credentials, calendar_name: str, ical_data: str):
    service = build("calendar", "v3", credentials=credentials)
    
    # Create the new calendar
    calendar = {
        "summary": calendar_name,
        "timeZone": "Asia/Jerusalem",
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    calendar_id = created_calendar["id"]

    # Parse the iCal data
    if not ical_data:
        raise ValueError("No iCal data provided")
    ical = Calendar.from_ical(ical_data.encode("utf-8"))

    # Prepare events for asynchronous processing
    for component in ical.walk():
        try:
            if component.name == "VEVENT":
                start_time = component.get("dtstart").dt.isoformat()
                end_time = component.get("dtend").dt.isoformat()
                summary = component.get("summary", "")
                description = component.get("description", "")
                location = component.get("location", "")
                rrule_dict = component.get("rrule")
                # convert it into a string
                rrule = format_rrule(rrule_dict)
                print(rrule)
                time_zone = "Asia/Jerusalem"
                event = {
                    "summary": summary,
                    "description": description,
                    "location": location,
                    "start": {
                        "dateTime": start_time,
                        "timeZone": time_zone,
                    },
                    "end": {
                        "dateTime": end_time,
                        "timeZone": time_zone,
                    },
                    "recurrence": [rrule],
                }

                service.events().insert(calendarId=calendar_id, body=event).execute()
        except HttpError as e:
            print(f"Error creating event: {e}")

    
    # Execute all tasks concurrently
    return calendar_id

def format_rrule(rrule_dict):
    return "RRULE:" + ";".join([
        f"FREQ={','.join(rrule_dict.get('FREQ', []))}",
        f"UNTIL={rrule_dict.get('UNTIL', [None])[0].strftime('%Y%m%dT%H%M%SZ')}" if 'UNTIL' in rrule_dict and rrule_dict['UNTIL'] else '',
        f"BYDAY={','.join(rrule_dict.get('BYDAY', []))}" if 'BYDAY' in rrule_dict and rrule_dict['BYDAY'] else ''
    ])