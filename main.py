from bs4 import BeautifulSoup
import pandas as pd
from icalendar import Calendar, Event
import datetime
from io import StringIO
import re

pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_colwidth', 1000)

rrdays = {"M": "MO", "T": "TU", "W": "WE",
          "R": "TH", "F": "FR", "S": "SA", "U": "SU"}
wdays = {"M": 0, "T": 1, "W": 2, "R": 3, "F": 4, "S": 5, "U": 6}


class Schedule:
    def __init__(self, start_date, end_date) -> None:
        try:
            self.start_date = datetime.datetime.strptime(
                start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            self.end_date = datetime.datetime.strptime(
                end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            if self.start_date > self.end_date:
                raise Exception("Start date must be before end date")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
            exit(1)
        self.read_courses()

    # A function  to get the next weekday from a given date
    def next_weekday(self, days) -> datetime.datetime:
        min_date = 7
        for day in days:
            days_ahead = wdays[day] - self.start_date.weekday()
            if days_ahead < min_date and days_ahead >= 0:
                min_date = days_ahead
        return self.start_date + datetime.timedelta(days=min_date)

    def read_courses(self) -> None:
        try:
            with open('index.html', encoding='utf-8') as html_file:
                soup = BeautifulSoup(html_file, 'lxml')
                table = soup.find('table')
                self.df = pd.read_html(StringIO(str(table)))[0]
                self.df = self.df.rename(
                    columns={"Class": "Section", "time": "Time", "Room Number": "Room"})

        except Exception as e:
            print(e)
            exit(1)

    def to_ical(self) -> Calendar:
        calendar = Calendar()
        for index, row in self.df.iterrows():
            # Check if the course has a time, days, and room
            if isinstance(row['Time'], float):  # check if nan => skip
                continue
            if isinstance(row['Room'], float):
                continue
            if isinstance(row['Days'], float):
                continue
            row['Room'] = re.sub(r'[\u0600-\u06FF\-]+', '',
                                 row['Room']).strip().split()
            self.df.at[index, 'Room'] = row['Room']
            if len(row['Room']) - 1:  # check if it has multiple rooms => create multiple events
                print(row['Course Title'], row['Room'])
                for i, room in enumerate(row['Room']):
                    e = Event()
                    start_time = datetime.datetime.strptime(
                        row['Time'].split()[0 + 3*i], '%H:%M')
                    start_time = datetime.datetime.combine(self.next_weekday(
                        row['Days'].split(" ")[i]), start_time.time())
                    end_time = datetime.datetime.strptime(
                        row['Time'].split()[2 + 3*i], '%H:%M')
                    end_time = datetime.datetime.combine(self.next_weekday(
                        row['Days'].split(" ")[i]), end_time.time())
                    e.add('summary', row['Course Title'])
                    e.add('dtstart', start_time)
                    e.add('dtend', end_time)
                    e.add('rrule', {'freq': 'weekly', 'until': self.end_date,
                          'byday': rrdays[row['Days'].split(' ')[i]]})
                    e.add('location', room)
                    e.add(
                        'description', f"Section: {row['Section']}\nCode: {row['Course Label']}\nInstructor: {row['Instructor']}")
                    calendar.add_component(e)
            else:
                e = Event()
                start_time = datetime.datetime.strptime(
                    row['Time'].split()[0], '%H:%M')
                start_time = datetime.datetime.combine(
                    self.next_weekday(row['Days'].split(", ")), start_time.time())
                end_time = datetime.datetime.strptime(
                    row['Time'].split()[2], '%H:%M')
                end_time = datetime.datetime.combine(
                    self.next_weekday(row['Days'].split(", ")), end_time.time())
                e.add('summary', row['Course Title'])
                e.add('dtstart', start_time)
                e.add('dtend', end_time)
                days = [rrdays[x] for x in row['Days'].split(', ')]
                e.add('rrule', {'freq': 'weekly',
                      'until': self.end_date, 'byday': days})
                e.add('location', row['Room'][0])
                e.add(
                    'description', f"Section: {row['Section']}\nCode: {row['Course Label']}\nInstructor: {row['Instructor']}")
                calendar.add_component(e)
        with open('calendar.ics', 'wb') as f:  # Write the calendar to a file
            f.write(calendar.to_ical())

    def __str__(self) -> str:
        return self.df.to_string()


if __name__ == '__main__':
    # start_date = input("Enter the start date (YYYY-MM-DD): ")
    # end_date = input("Enter the end date (YYYY-MM-DD): ")
    start_date = "2023-9-23"
    end_date = "2024-1-22"
    schedule = Schedule(start_date, end_date)
    schedule.to_ical()
    print(schedule)
