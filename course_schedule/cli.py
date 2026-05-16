import argparse
import asyncio
import datetime
import logging
import os
import sys

from course_schedule import Schedule
from course_schedule.calendar import AcademicCalendar
from course_schedule.client import RitajClient, RitajError, fetch_academic_calendar
from icalendar import Calendar as ICalendar

from course_schedule.tui import interactive_prompts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Ritaj schedule to iCalendar"
    )
    parser.add_argument("html", nargs="?", help="Path to the HTML file (not needed with --live)")
    parser.add_argument("-o", "--output", default="schedule.ics", help="Output .ics filename")
    parser.add_argument("--csv", action="store_true", help="Also export as CSV")
    parser.add_argument("--live", action="store_true", help="Fetch schedule live from Ritaj via FlareSolverr")
    parser.add_argument("--interactive", action="store_true", help="Run interactive prompts")
    parser.add_argument("--username", help="Ritaj username (env: RITAJ_USERNAME)")
    parser.add_argument("--password", help="Ritaj password (env: RITAJ_PASSWORD)")
    parser.add_argument(
        "--flaresolverr-url",
        default="http://localhost:8191/v1",
        help="FlareSolverr URL (default: http://localhost:8191/v1)",
    )
    parser.add_argument(
        "--no-calendar",
        action="store_true",
        help="Skip fetching academic calendar events",
    )
    parser.add_argument(
        "--semester",
        help='Force semester detection (e.g. "Fall", "Spring", "Summer")',
    )
    parser.add_argument(
        "--calendar",
        choices=["merged", "separate"],
        default="merged",
        help="Merge calendar events into schedule .ics or write separate file (default: merged)",
    )
    parser.add_argument(
        "--calendar-output",
        help="Output file for academic calendar (only with --calendar separate)",
    )
    return parser


def run(args: argparse.Namespace) -> None:
    if args.interactive or (not args.live and not args.html):
        interactive_prompts(args)
        args.live = True

    if args.live:
        _run_live(args)
    elif args.html:
        _run_file(args)


def _run_file(args: argparse.Namespace) -> None:
    try:
        with open(args.html, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        logging.error("File '%s' not found.", args.html)
        sys.exit(1)

    from course_schedule.config import START_DATE, END_DATE
    _build_schedule(html, args, start_date=START_DATE, end_date=END_DATE)


def _run_live(args: argparse.Namespace) -> None:
    username = args.username or os.environ.get("RITAJ_USERNAME")
    password = args.password or os.environ.get("RITAJ_PASSWORD")

    if not username or not password:
        logging.error("--username/--password or RITAJ_USERNAME/RITAJ_PASSWORD env vars required.")
        sys.exit(1)

    calendar_html = None
    calendar_obj = None

    if not args.no_calendar:
        try:
            logging.info("Fetching academic calendar...")
            calendar_html = asyncio.run(fetch_academic_calendar(args.flaresolverr_url))
            calendar_obj = AcademicCalendar(calendar_html)
        except Exception as e:
            logging.warning("Failed to fetch academic calendar: %s", e)

    start_date = None
    end_date = None

    if calendar_obj:
        semester = None
        if args.semester:
            semester = calendar_obj.find_semester(args.semester)
        if not semester:
            semester = calendar_obj.detect_current_semester()
        if semester:
            start_date = semester.start_date
            end_date = semester.end_date
            logging.info(
                "Detected semester: %s (%s to %s)",
                semester.name,
                start_date.strftime("%d-%m-%Y"),
                end_date.strftime("%d-%m-%Y"),
            )
        else:
            logging.warning("Could not detect current semester from calendar.")

    if not start_date or not end_date:
        from course_schedule.config import START_DATE, END_DATE
        start_date = START_DATE
        end_date = END_DATE

    if not start_date or not end_date:
        logging.error(
            "Semester dates not available. Set START_DATE/END_DATE env vars "
            "or use auto-detection from academic calendar (remove --no-calendar)."
        )
        sys.exit(1)

    async def fetch_schedule():
        client = RitajClient(
            flaresolverr_url=args.flaresolverr_url,
            username=username,
            password=password,
        )
        try:
            logging.info("Logging in and fetching schedule...")
            await client.login()
            html = await client.fetch_schedule()
            return html
        except RitajError as e:
            logging.error("%s", e)
            sys.exit(1)
        finally:
            await client.close()

    schedule_html = asyncio.run(fetch_schedule())

    _build_schedule(
        schedule_html, args,
        calendar=calendar_obj,
        start_date=start_date,
        end_date=end_date,
    )


def _build_schedule(
    html: str,
    args: argparse.Namespace,
    calendar: AcademicCalendar | None = None,
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
) -> None:
    try:
        schedule = Schedule(html, start_date=start_date, end_date=end_date)
    except ValueError as e:
        logging.error("Failed to parse schedule: %s", e)
        sys.exit(1)

    ical = schedule.to_ical()

    if calendar and args.calendar == "merged":
        calendar.add_to_ical(ical)

    with open(args.output, "wb") as out:
        out.write(ical.to_ical())
    logging.info("iCalendar file '%s' created successfully.", args.output)

    if calendar and args.calendar == "separate":
        cal_ics = args.calendar_output or _calendar_output_path(args.output)
        cal_cal = ICalendar()
        cal_cal.add("version", "2.0")
        cal_cal.add("prodid", "-//Birzeit University//Academic Calendar//EN")
        cal_cal.add("calscale", "GREGORIAN")
        calendar.add_to_ical(cal_cal)
        with open(cal_ics, "wb") as out:
            out.write(cal_cal.to_ical())
        logging.info("Calendar file '%s' created successfully.", cal_ics)

    if args.csv:
        csv_path = args.output.rsplit(".", 1)[0] + ".csv"
        schedule.to_csv(csv_path)
        logging.info("CSV file '%s' created successfully.", csv_path)

    print(schedule)


def _calendar_output_path(schedule_path: str) -> str:
    base, ext = os.path.splitext(schedule_path)
    return base.replace("schedule", "calendar") + ext if "schedule" in base else "calendar" + ext
