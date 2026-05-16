import re
import datetime
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from icalendar import Calendar as ICalendar, Event


@dataclass
class CalendarEvent:
    date: datetime.date
    title: str
    end_date: datetime.date | None = None

    def __post_init__(self):
        if self.end_date is None:
            self.end_date = self.date


@dataclass
class SemesterInfo:
    name: str
    start_date: datetime.datetime
    end_date: datetime.datetime


class AcademicCalendar:
    def __init__(self, html: str):
        self.events: list[CalendarEvent] = []
        self.semesters: list[SemesterInfo] = []
        self.academic_year: tuple[int, int] | None = None
        self._parse(html)

    def _parse(self, html: str) -> None:
        soup = BeautifulSoup(html, "lxml")
        self._extract_academic_year(soup)
        self._parse_events(soup)
        self._merge_paired_events()
        self._extract_semesters()

    def _extract_academic_year(self, soup: BeautifulSoup) -> None:
        text = soup.get_text()
        m = re.search(r"Academic Calendar for the Academic Year (\d{4})/(\d{4})", text)
        if m:
            self.academic_year = (int(m.group(1)), int(m.group(2)))

    def _parse_events(self, soup: BeautifulSoup) -> None:
        table = soup.find("table")
        if not table:
            return

        current_month: int | None = None
        current_year: int | None = None

        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            first_cell = cells[0]
            month_match = re.match(
                r"(?:e_)?mon_(\d+)_(\d+)", first_cell.get("id", "")
            )
            if month_match:
                current_month = int(month_match.group(1))
                current_year = int(month_match.group(2))
                cells = cells[1:]

            if current_month is None:
                continue
            if len(cells) < 3:
                continue

            day_str = cells[0].get_text(strip=True) if len(cells) > 0 else ""
            title_cell = cells[2] if len(cells) > 2 else cells[-1]

            p_tags = title_cell.find_all("p")
            titles = []
            for p in p_tags:
                direct = "".join(p.find_all(string=True, recursive=False)).strip()
                if not direct:
                    continue
                direct = re.sub(r" +", " ", direct).strip()
                direct = re.sub(r"\b(Start of )\s*(Start of )", r"\1", direct)
                direct = re.sub(r"\b(End of )\s*(Start of )", r"\1", direct)
                direct = re.sub(r"\s*\(\d+:\d+\s*(?:AM|PM)\)", "", direct).strip()
                titles.append(direct)
            if not titles:
                raw = title_cell.get_text(strip=True)
                if raw:
                    titles.append(raw)
            if not titles:
                continue

            try:
                day = int(day_str.strip())
            except ValueError:
                continue

            date = datetime.date(current_year, current_month, day)
            for title in titles:
                self.events.append(CalendarEvent(date=date, title=title))

    def _merge_paired_events(self) -> None:
        self.events.sort(key=lambda e: e.date)
        result = []
        skip: set[int] = set()

        for i, event in enumerate(self.events):
            if i in skip:
                continue
            if event.title.startswith("Start of "):
                desc = event.title[len("Start of "):]
                found = False
                for j in range(i + 1, len(self.events)):
                    if j in skip:
                        continue
                    other = self.events[j]
                    if other.title == f"End of {desc}":
                        result.append(CalendarEvent(
                            date=event.date,
                            title=desc,
                            end_date=other.date,
                        ))
                        skip.add(j)
                        found = True
                        break
                if not found:
                    result.append(event)
            else:
                result.append(event)

        self.events = result

    def _extract_semesters(self) -> None:
        for event in self.events:
            m = re.match(
                r"Start of teaching for the (.+ (?:Semester|Course) \d{4}/\d{4})",
                event.title,
            )
            if m:
                name = m.group(1)
                end_pattern = rf"Last day of teaching for the {re.escape(name)}"
                for other in self.events:
                    if re.match(end_pattern, other.title):
                        start = datetime.datetime.combine(event.date, datetime.time())
                        end = datetime.datetime.combine(other.date, datetime.time())
                        self.semesters.append(SemesterInfo(
                            name=name,
                            start_date=start,
                            end_date=end,
                        ))
                        break

    def detect_current_semester(
        self, today: datetime.date | None = None,
    ) -> SemesterInfo | None:
        if today is None:
            today = datetime.date.today()
        for sem in self.semesters:
            if sem.start_date.date() <= today <= sem.end_date.date():
                return sem
        return None

    def find_semester(self, name: str) -> SemesterInfo | None:
        lower = name.lower()
        for sem in self.semesters:
            if lower in sem.name.lower():
                return sem
        return None

    def add_to_ical(self, cal: ICalendar) -> None:
        for event in self.events:
            e = Event()
            e.add("summary", event.title)
            e.add("dtstart", event.date)
            e.add("dtend", event.end_date + datetime.timedelta(days=1))
            e.add("dtstamp", datetime.datetime.now(datetime.timezone.utc))
            uid_hash = abs(hash(f"{event.date.isoformat()}-{event.title}"))
            e.add("uid", f"academic-{uid_hash}@birzeit.edu")
            cal.add_component(e)
