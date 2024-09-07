from icalendar import Calendar, Event
from fastapi import HTTPException
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import datetime
import re
from . import START_DATE, END_DATE

class Schedule:
    def __init__(self, html_file):
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

    # A function  to get the next weekday from a given date
    def next_weekday(self, days) -> datetime.datetime:
        w_days = [self.wdays[x] for x in days]
        current_day = START_DATE.weekday()
        # Get the next day that is in the list of days (Minimum Difference)
        next_day = min(w_days, key=lambda x: (x - current_day) % 7)
        return START_DATE + datetime.timedelta(days=(next_day - current_day) % 7)

    def load(self, html_file) -> None:
        try:
            with html_file:
                soup = BeautifulSoup(html_file, "lxml")
                table = soup.find("table")
                self.df = pd.read_html(StringIO(str(table)))[0]
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
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload a valid schedule file",
            )

    def to_ical(self) -> Calendar:
        calendar = Calendar()
        for index, row in self.df.iterrows():
            # Check if the course has a time, days, and room
            if isinstance(row["Time"], float):  # check if nan => skip
                continue
            if isinstance(row["Room"], float):
                continue
            if isinstance(row["Days"], float):
                continue
            row["Room"] = re.sub(r"[\u0600-\u06FF\-]+", "", row["Room"]).strip().split()
            self.df.at[index, "Room"] = row["Room"]
            if (
                len(row["Room"]) - 1
            ):  # check if it has multiple rooms => create multiple events
                for i, room in enumerate(row["Room"]):
                    e = Event()
                    start_time = datetime.datetime.strptime(
                        row["Time"].split()[0 + 3 * i], "%H:%M"
                    )
                    start_time = datetime.datetime.combine(
                        self.next_weekday(row["Days"].split(" ")[i]), start_time.time()
                    )
                    end_time = datetime.datetime.strptime(
                        row["Time"].split()[2 + 3 * i], "%H:%M"
                    )
                    end_time = datetime.datetime.combine(
                        self.next_weekday(row["Days"].split(" ")[i]), end_time.time()
                    )
                    e.add("summary", row["Course Title"])
                    e.add("dtstart", start_time)
                    e.add("dtend", end_time)
                    e.add(
                        "rrule",
                        {
                            "freq": "weekly",
                            "until": END_DATE,
                            "byday": self.rrdays[row["Days"].split(" ")[i]],
                        },
                    )
                    e.add("location", room)
                    e.add(
                        "description",
                        f"Section: {row['Section']}\nCode: {row['Course Label']}\nInstructor: {row['Instructor']}",
                    )
                    calendar.add_component(e)
            else:
                e = Event()
                start_time = datetime.datetime.strptime(row["Time"].split()[0], "%H:%M")
                start_time = datetime.datetime.combine(
                    self.next_weekday(row["Days"].split(", ")), start_time.time()
                )
                end_time = datetime.datetime.strptime(row["Time"].split()[2], "%H:%M")
                end_time = datetime.datetime.combine(
                    self.next_weekday(row["Days"].split(", ")), end_time.time()
                )
                e.add("summary", row["Course Title"])
                e.add("dtstart", start_time)
                e.add("dtend", end_time)
                days = [self.rrdays[x] for x in row["Days"].split(", ")]
                e.add(
                    "rrule", {"freq": "weekly", "until": END_DATE, "byday": days}
                )
                e.add("location", row["Room"][0])
                e.add(
                    "description",
                    f"Section: {row['Section']}\nCode: {row['Course Label']}\nInstructor: {row['Instructor']}",
                )
                calendar.add_component(e)
        return calendar.to_ical()

    def __str__(self) -> str:
        return self.df.to_string()
