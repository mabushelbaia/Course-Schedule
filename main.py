from icalendar import Calendar, Event, Alarm
from courses import Courses
from datetime import datetime, timedelta
valid = False
# while not valid:
#     inp = input("Type Start Date dd/mm/yy: ")
#     try:
#         start = datetime.strptime(inp, "%d/%m/%Y")
#         valid = True
#     except:
#         print("Invalid Input try again.")
# valid = False
# while not valid:
#     inp = input("Type End Date dd/mm/yy: ")
#     try:
#         end = datetime.strptime(inp, "%d/%m/%Y")
#         valid = True
#     except:
#         print("Invalid Input try again.")
c = Calendar()
start = datetime(2022, 11, 7)
end = datetime(2023, 2, 14)

days = {"M": 0, "T": 1, "W": 2, "R": 3, "F": 4, "S": 5, "U": 6}
rrdays = {"M": "MO", "T": "TU", "W": "WE", "R": "TH", "F": "FR", "S": "SA", "U": "SU"}
# ==============================================================================
#        Generated by copilot
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    return d + timedelta(days_ahead)
# ==============================================================================
for course in Courses:

    if course.hasMultipleRooms:
        for i, day in enumerate(course.days):
            e = Event()
            a = Alarm()
            a.add('action', 'DISPLAY')
            a.add('description', 'Reminder')
            a.add('trigger', timedelta(minutes=-10))
            e.add_component(a)
            start_hour, end_hour = course.time[i][0].split(":")[0], course.time[i][1].split(":")[0]
            start_minute, end_minute = course.time[i][0].split(":")[1], course.time[i][1].split(":")[1]
            e.add('location', course.room[i])
            e.add('description', f"Class: {course.Class} \nCode: {course.code} \nInstructor: {course.instructor} \nBuilding: {course.building[i]}")
            e.add('summary', course.title)
            e.add('dtstart', next_weekday(start, days[day]).replace(hour=int(start_hour), minute=int(start_minute)))
            e.add('dtend', next_weekday(start, days[day]).replace(hour=int(end_hour), minute=int(end_minute)))
            e.add('rrule', {'freq': 'weekly', 'until': end, 'byday': rrdays[day]})
            c.add_component(e)

    else:
        e = Event()
        a = Alarm()
        a.add('action', 'DISPLAY')
        a.add('description', 'Reminder')
        a.add('trigger', timedelta(minutes=-10))
        e.add_component(a)
        start_hour, end_hour = course.time[0].split(":")[0], course.time[1].split(":")[0]
        start_minute, end_minute = course.time[0].split(":")[1], course.time[1].split(":")[1]
        e.add('location', course.room)
        e.add('description', f"Class: {course.Class} \nCode: {course.code} \nInstructor: {course.instructor} \nBuilding: {course.building}")
        e.add('summary', course.title)
        e.add('dtstart', next_weekday(start, days[course.days[0]]).replace(hour=int(start_hour), minute=int(start_minute)))
        e.add('dtend', next_weekday(start, days[course.days[0]]).replace(hour=int(end_hour), minute=int(end_minute)))
        temp = [rrdays[day] for day in course.days]
        e.add('rrule', {'freq': 'weekly', 'until': end, 'byday': temp})
        c.add_component(e)

f = open("calendar.ics", 'wb')
f.write(c.to_ical())
f.close()

