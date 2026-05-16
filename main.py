import logging

from course_schedule.cli import build_parser, run
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()
def main():
    parser = build_parser()
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
