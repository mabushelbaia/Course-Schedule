import logging
import sys

from course_schedule.cli import build_parser, run
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()


def main():
    parser = build_parser()
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the web UI server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the web UI server (default: 8000)",
    )
    args = parser.parse_args()

    if args.serve:
        import uvicorn
        uvicorn.run("course_schedule.web:app", host="0.0.0.0", port=args.port)
        return

    run(args)


if __name__ == "__main__":
    main()
