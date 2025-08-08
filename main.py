import argparse
import logging

from course_schedule import Schedule


logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Ritaj schedule HTML to iCalendar"
    )
    parser.add_argument("html", help="Path to the HTML file exported from Ritaj")
    parser.add_argument(
        "-o", "--output", default="schedule.ics", help="Output .ics filename"
    )
    parser.add_argument("--csv", action="store_true", help="Also export as CSV")
    args = parser.parse_args()

    try:
        with open(args.html, "r", encoding="utf-8") as f:
            html = f.read()
            schedule = Schedule(html)
            ical = schedule.to_ical()

            with open(args.output, "wb") as out:
                out.write(ical.to_ical())
            logging.info(f"iCalendar file '{args.output}' created successfully.")

            if args.csv:
                schedule.to_csv()
                logging.info("CSV file 'schedule.csv' created successfully.")

            print(schedule)

    except FileNotFoundError:
        logging.error(f"File '{args.html}' not found.")
    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()
