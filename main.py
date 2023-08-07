"""
This project is poorly done, but if it works don't fix it.
"""

from icalendar import Calendar, Event
from courses import Course, get_courses
from datetime import datetime, timedelta

c = Calendar()
start = datetime(2023, 8, 1)
end = datetime(2023, 9, 1)

days = {"M": 0, "T": 1, "W": 2, "R": 3, "F": 4, "S": 5, "U": 6}
rrdays = {"M": "MO", "T": "TU", "W": "WE", "R": "TH", "F": "FR", "S": "SA", "U": "SU"}

def next_weekday(d, weekday): # A function  to get the next weekday from a given date
    days_ahead = weekday - d.weekday()
    return d + timedelta(days_ahead)
for course in get_courses():
    if course.days[0] not in days or course.time[0] == ["N/A"]: # Skip courses with no time or days
        continue
    if course.hasMultipleRooms: # Split courses with multiple rooms into multiple events
        for i, day in enumerate(course.days):
            e = Event()
            start_hour, end_hour = course.time[i][0].split(":")[0], course.time[i][1].split(":")[0]
            start_minute, end_minute = course.time[i][0].split(":")[1], course.time[i][1].split(":")[1]
            e.add('location', course.room[i])
            e.add('description', f"Class: {course.Class}\nCode: {course.code}\nInstructor: {course.instructor}\nBuilding: {course.building[i]}")
            e.add('summary', course.title)
            e.add('dtstart', next_weekday(start, days[day]).replace(hour=int(start_hour), minute=int(start_minute)))
            e.add('dtend', next_weekday(start, days[day]).replace(hour=int(end_hour), minute=int(end_minute)))
            e.add('rrule', {'freq': 'weekly', 'until': end, 'byday': rrdays[day]})
            c.add_component(e)

    else:  # Add courses with single rooms as a single event
        e = Event()
        start_hour, end_hour = course.time[0].split(":")[0], course.time[1].split(":")[0]
        start_minute, end_minute = course.time[0].split(":")[1], course.time[1].split(":")[1]
        e.add('location', course.room)
        e.add('description', f"Class: {course.Class}\nCode: {course.code}\nInstructor: {course.instructor}\nBuilding: {course.building}")
        e.add('summary', course.title)
        e.add('dtstart', min(next_weekday(start, days[course.days[0]]), next_weekday(start, days[course.days[-1]])).replace(hour=int(start_hour), minute=int(start_minute)))
        e.add('dtend', min(next_weekday(start, days[course.days[0]]), next_weekday(start, days[course.days[-1]])).replace(hour=int(end_hour), minute=int(end_minute))) # the min here to get the earlier day
        course_days = [rrdays[day] for day in course.days]
        e.add('rrule', {'freq': 'weekly', 'until': end, 'byday': course_days})
        c.add_component(e)
with open ('calendar.ics', 'wb') as f: # Write the calendar to a file
    f.write(c.to_ical())

