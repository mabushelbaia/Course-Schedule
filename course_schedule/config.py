import os
import datetime
import warnings
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def parse_date(date_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_str, "%d-%m-%Y")

start_date_str = os.getenv("START_DATE")
end_date_str = os.getenv("END_DATE")

if start_date_str and end_date_str:
    START_DATE = parse_date(start_date_str)
    END_DATE = parse_date(end_date_str)
else:
    if start_date_str or end_date_str:
        warnings.warn("Both START_DATE and START_END must be set; ignoring partial config.")
    START_DATE = None
    END_DATE = None
