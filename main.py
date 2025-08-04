

from package.main import Schedule


if __name__ == "__main__":
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            schedule = Schedule(f)

            ical_file = schedule.to_ical()

            if not ical_file:
                raise ValueError("Failed to generate the iCalendar file.")
            # Save the iCalendar file
            with open("schedule.ics", "wb") as ical_f:
                ical_f.write(ical_file.to_ical())
            print(schedule)
            print("iCalendar file 'schedule.ics' created successfully.")
            # print pandas DataFrame

    except FileNotFoundError:
        print("Error: 'index.html' not found. Please make sure the file exists in the current directory.")
    