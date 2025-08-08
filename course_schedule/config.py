import os
import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def parse_date(date_str: str) -> datetime.datetime:
    # your date parsing with multiple formats here, or simple strptime
    return datetime.datetime.strptime(date_str, "%d-%m-%Y")

start_date_str = os.getenv("START_DATE")
end_date_str = os.getenv("END_DATE")

if start_date_str is None or end_date_str is None:
    raise ValueError("START_DATE and END_DATE must be set in the environment.")

START_DATE = parse_date(start_date_str)
END_DATE = parse_date(end_date_str)
