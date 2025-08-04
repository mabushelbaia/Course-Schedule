from icalendar import Calendar, Event
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import datetime
import re
from . import START_DATE, END_DATE

class Schedule:
    from typing import IO

    def __init__(self, html_file: IO[str]):
        self.load(html_file)
        self.rrdays = {
            "M": "MO",
            "T": "TU",
            "W": "WE",
            "R": "TH",
            "F": "FR",
            "S": "SA",
            "U": "SU",
        }
        self.wdays = {"M": 0, "T": 1, "W": 2, "R": 3, "F": 4, "S": 5, "U": 6}

    def next_weekday(self, days: list[str]) -> datetime.datetime:
        w_days = [self.wdays[x] for x in days]
        current_day = START_DATE.weekday()
        next_day = min(w_days, key=lambda x: (x - current_day) % 7)
        return START_DATE + datetime.timedelta(days=(next_day - current_day) % 7)

    def load(self, html_file: IO[str]) -> None:
        try:
            with html_file:
                soup = BeautifulSoup(html_file, "lxml")
                table = soup.find("table")
                self.df: pd.DataFrame = pd.read_html(StringIO(str(table)))[0]  # type: ignore
                self.df = self.df.rename(
                    columns={"Class": "Section", "time": "Time", "Room Number": "Room"}
                )
                self.df.columns = [
                    "Course Label",
                    "Section",
                    "Course Title",
                    "Instructor",
                    "Days",
                    "Time",
                    "Room",
                ]
        except Exception as e:
            print(e)
            raise ValueError("Failed to load the schedule from the HTML file.")

    def to_ical(self) -> Calendar:
        calendar = Calendar()
        calendar.add("version", "2.0")
        calendar.add("prodid", "-//Birzeit University//Schedule Exporter//EN")
        calendar.add("calscale", "GREGORIAN")

        for index, row in self.df.iterrows():
            if any(isinstance(row[col], float) for col in ["Time", "Room", "Days"]):
                continue

            # Clean Room and split if multiple entries
            row["Room"] = re.sub(r"[\u0600-\u06FF\-]+", "", row["Room"]).strip().split()
            self.df.at[index, "Room"] = row["Room"] # type: ignore

            # Clean and normalize days
            raw_days = re.split(r"[\s,]+", row["Days"])
            days = [d for d in raw_days if d in self.rrdays]
            bydays = [self.rrdays[d] for d in days]

            # Split time values
            time_parts = row["Time"].split()

            # Collapse long summaries
            summary = " ".join(row["Course Title"].split())

            # Event creation
            e = Event()
            e.add("summary", summary)
            e.add("dtstart", datetime.datetime.combine(self.next_weekday(days), datetime.datetime.strptime(time_parts[0], "%H:%M").time()))
            e.add("dtend", datetime.datetime.combine(self.next_weekday(days), datetime.datetime.strptime(time_parts[2], "%H:%M").time()))
            e.add("dtstamp", datetime.datetime.now(datetime.timezone.utc))
            e.add("uid", f"{row['Course Label']}-{row['Section']}-{index}@birzeit.edu")
            e.add("rrule", {"freq": "weekly", "until": END_DATE, "byday": bydays})
            e.add("location", row["Room"][0])
            e.add("description", f"Section: {row['Section']}\nCode: {row['Course Label']}\nInstructor: {row['Instructor']}")

            calendar.add_component(e)

        return calendar

    def __str__(self) -> str:
        return self.df.to_string(buf=None, index=False, header=True) # type: ignore