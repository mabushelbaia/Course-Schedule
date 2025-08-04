import datetime
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

start_date_str = os.getenv("START_DATE")
end_date_str = os.getenv("END_DATE")

if start_date_str is None:
	raise ValueError("START_DATE environment variable is not set")
if end_date_str is None:
	raise ValueError("END_DATE environment variable is not set")

START_DATE = datetime.datetime.strptime(start_date_str, "%d-%m-%Y")
END_DATE = datetime.datetime.strptime(end_date_str, "%d-%m-%Y")
