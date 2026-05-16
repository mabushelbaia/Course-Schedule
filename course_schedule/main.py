from icalendar import Calendar, Event
from bs4 import BeautifulSoup, Tag
from io import StringIO
import pandas as pd
import datetime
import re

RRDAYS = {"M": "MO", "T": "TU", "W": "WE", "R": "TH", "F": "FR", "S": "SA", "U": "SU"}
WDAYS = {"M": 0, "T": 1, "W": 2, "R": 3, "F": 4, "S": 5, "U": 6}
COLUMN_NAMES = ["Course Label", "Section", "Course Title", "Instructor", "Days", "Time", "Room"]


class Schedule:
    def __init__(self, html_content: str, start_date=None, end_date=None):
        if start_date is None or end_date is None:
            raise ValueError(
                "start_date and end_date are required. Set START_DATE/END_DATE "
                "env vars, or use --live mode for auto-detection."
            )
        self.start_date = start_date
        self.end_date = end_date
        self.df = self._parse(html_content)

    def _next_weekday(self, days: list[str]) -> datetime.datetime:
        w_days = [WDAYS[d] for d in days]
        current = self.start_date.weekday()
        delta = min((d - current) % 7 for d in w_days)
        return self.start_date + datetime.timedelta(days=delta)

    def _parse(self, html: str) -> pd.DataFrame:
        soup = BeautifulSoup(html, "lxml")
        table = self._find_table(soup)
        if table is None:
            df = self._parse_manual(soup)
        else:
            df = self._parse_pandas(table)
        df["Days"] = df["Days"].apply(lambda x: " ".join(str(x).split()))
        return df

    def _find_table(self, soup: BeautifulSoup) -> Tag | None:
        for tbl in soup.find_all("table"):
            try:
                test_df = pd.read_html(StringIO(str(tbl)))[0]
                if test_df.shape[1] >= 5:
                    return tbl
            except Exception:
                continue
        return None

    def _parse_pandas(self, table: Tag) -> pd.DataFrame:
        df = pd.read_html(StringIO(str(table)))[0]
        num_cols = df.shape[1]

        if num_cols == 5:
            return self._parse_manual_rows(table)
        if num_cols == 7:
            return self._normalize_7col(df)
        if num_cols == 9:
            return self._normalize_9col(df)
        raise ValueError(f"Unexpected number of columns: {num_cols}")

    def _normalize_7col(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns={"Class": "Section", "time": "Time", "Room Number": "Room"})
        df.columns = COLUMN_NAMES
        return df

    def _normalize_9col(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            "Course Label", "Section", "Course Title",
            "Registered Number", "Max Number", "Days", "Time", "Room", "Extra",
        ]
        df = df.drop(columns=["Registered Number", "Max Number", "Extra"])
        df["Instructor"] = "N/A"
        return df

    def _parse_manual(self, soup: BeautifulSoup) -> pd.DataFrame:
        for tbl in soup.find_all("table"):
            data = self._parse_manual_rows(tbl)
            if data:
                return pd.DataFrame(data)
        raise ValueError("Could not parse schedule table from HTML.")

    def _parse_manual_rows(self, table: Tag) -> list[dict] | pd.DataFrame:
        data = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue
            record = self._parse_row(cells)
            if record:
                data.append(record)
        if not data:
            raise ValueError("Could not parse schedule table from HTML.")
        return pd.DataFrame(data)

    def _parse_row(self, cells: list[Tag]) -> dict | None:
        course_cell = cells[0]
        label_elem = course_cell.find("a")
        if not label_elem:
            return None

        course_label = label_elem.get_text(strip=True)
        section = "N/A"
        section_span = course_cell.find("span", string=lambda x: x and "Section:" in x)
        if section_span:
            section = section_span.get_text(strip=True).replace("Section:", "").strip()
        title_div = course_cell.find("div", class_="title")
        course_title = title_div.get_text(strip=True) if title_div else "N/A"

        days = cells[1].get_text(strip=True) if len(cells) > 1 else "N/A"
        time = cells[2].get_text(strip=True) if len(cells) > 2 else "N/A"
        room = cells[3].get_text(strip=True) if len(cells) > 3 else "N/A"

        if time in ("N/A", "") or "-" not in time:
            return None

        return {
            "Course Label": course_label,
            "Section": section,
            "Course Title": course_title,
            "Instructor": "N/A",
            "Days": days,
            "Time": time,
            "Room": room,
        }

    def to_csv(self, filename: str = "schedule.csv") -> None:
        self.df.to_csv(filename, index=False)

    def to_ical(self) -> Calendar:
        cal = Calendar()
        cal.add("version", "2.0")
        cal.add("prodid", "-//Birzeit University//Schedule Exporter//EN")
        cal.add("calscale", "GREGORIAN")

        for i, row in self.df.iterrows():
            event = self._build_event(i, row)
            if event:
                cal.add_component(event)
        return cal

    def _build_event(self, idx: int, row: pd.Series) -> Event | None:
        if any(pd.isna(row[col]) for col in ["Time", "Room", "Days"]):
            return None

        rooms = re.sub(r"[\u0600-\u06FF\-]+", "", row["Room"]).strip().split()
        days_raw = re.split(r"[\s,]+", row["Days"])
        days = [d for d in days_raw if d in RRDAYS]
        if not days:
            return None
        bydays = [RRDAYS[d] for d in days]

        time_parts = row["Time"].split()
        if len(time_parts) < 3:
            return None

        try:
            start_time = datetime.datetime.strptime(time_parts[0], "%H:%M").time()
            end_time = datetime.datetime.strptime(time_parts[2], "%H:%M").time()
        except ValueError:
            return None

        event_date = self._next_weekday(days)
        e = Event()
        e.add("summary", " ".join(row["Course Title"].split()))
        e.add("dtstart", datetime.datetime.combine(event_date, start_time))
        e.add("dtend", datetime.datetime.combine(event_date, end_time))
        e.add("dtstamp", datetime.datetime.now(datetime.timezone.utc))
        e.add("uid", f"{row['Course Label']}-{row['Section']}-{idx}@birzeit.edu")
        e.add("rrule", {"freq": "weekly", "until": self.end_date, "byday": bydays})
        e.add("location", ", ".join(rooms))
        instructor = row.get("Instructor", "N/A")
        e.add(
            "description",
            f"Section: {row['Section']}\nCode: {row['Course Label']}\nInstructor: {instructor}",
        )
        return e

    def __str__(self) -> str:
        return self.df.to_string(index=False)
