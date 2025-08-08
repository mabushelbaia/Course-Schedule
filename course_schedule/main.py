from icalendar import Calendar, Event
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import datetime
import re   
from .config import START_DATE, END_DATE


class Schedule:
    def __init__(self, html_content: str, start_date=START_DATE, end_date=END_DATE):
        self.start_date = start_date
        self.end_date = end_date
        self.rrdays = {"M": "MO", "T": "TU", "W": "WE", "R": "TH", "F": "FR", "S": "SA", "U": "SU"}
        self.wdays = {"M": 0, "T": 1, "W": 2, "R": 3, "F": 4, "S": 5, "U": 6}
        self.load(html_content)

    def next_weekday(self, days: list[str]) -> datetime.datetime:
        w_days = [self.wdays[d] for d in days]
        current = self.start_date.weekday()
        delta = min((d - current) % 7 for d in w_days)
        return self.start_date + datetime.timedelta(days=delta)

    def load(self, html: str) -> None:
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        if table is None:
            raise ValueError("No table found in HTML.")

        df = pd.read_html(StringIO(str(table)))[0]
        df = df.rename(columns={"Class": "Section", "time": "Time", "Room Number": "Room"})
        df.columns = ["Course Label", "Section", "Course Title", "Instructor", "Days", "Time", "Room"]
        self.df = df

    def to_ical(self) -> Calendar:
        cal = Calendar()
        cal.add("version", "2.0")
        cal.add("prodid", "-//Birzeit University//Schedule Exporter//EN")
        cal.add("calscale", "GREGORIAN")

        for i, row in self.df.iterrows():
            if any(isinstance(row[col], float) for col in ["Time", "Room", "Days"]):
                continue

            row["Room"] = re.sub(r"[\u0600-\u06FF\-]+", "", row["Room"]).strip().split()
            self.df.at[i, "Room"] = row["Room"]

            days = [d for d in re.split(r"[\s,]+", row["Days"]) if d in self.rrdays]
            bydays = [self.rrdays[d] for d in days]
            if not days or len(row["Time"].split()) < 3:
                continue

            time_parts = row["Time"].split()
            start_time = datetime.datetime.strptime(time_parts[0], "%H:%M").time()
            end_time = datetime.datetime.strptime(time_parts[2], "%H:%M").time()
            event_date = self.next_weekday(days)

            e = Event()
            e.add("summary", " ".join(row["Course Title"].split()))
            e.add("dtstart", datetime.datetime.combine(event_date, start_time))
            e.add("dtend", datetime.datetime.combine(event_date, end_time))
            e.add("dtstamp", datetime.datetime.now(datetime.timezone.utc))
            e.add("uid", f"{row['Course Label']}-{row['Section']}-{i}@birzeit.edu")
            e.add("rrule", {"freq": "weekly", "until": self.end_date, "byday": bydays})
            e.add("location", ", ".join(row["Room"]))
            e.add("description", f"Section: {row['Section']}\nCode: {row['Course Label']}\nInstructor: {row['Instructor']}")

            cal.add_component(e)

        return cal

    def to_csv(self, path: str = "schedule.csv"):
        self.df.to_csv(path, index=False)

    def __str__(self) -> str:
        return self.df.to_string(index=False)
