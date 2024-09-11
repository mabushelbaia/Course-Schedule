import datetime
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

START_DATE = datetime.datetime.strptime(os.getenv("START_DATE"), "%d-%m-%Y")
END_DATE = datetime.datetime.strptime(os.getenv("END_DATE"), "%d-%m-%Y")
