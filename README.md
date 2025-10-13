# 📅 Course Schedule

This tool parses a university schedule exported as an `index.html` file and converts it into an iCalendar `.ics` file compatible with calendar applications (e.g., Google Calendar, Outlook).

---
## ⚠️ Important Notice

**The university has updated their schedule format, which has broken the current parser.** 

To fix this issue, we need a sample HTML file exported from a **student account** (not faculty/admin). If you're a student and can help, please:

1. Export your schedule as HTML from the student portal
2. Share the `index.html` file (remove any personal information first)
3. Open an issue on GitHub or contact us

This will help us update the parser to work with the new format.

---
## ✨ Features

* Parses course schedule from HTML exported from Ritaj.
* Converts schedule data to `.ics` iCalendar format with recurring weekly events.
* Saves output as `schedule.ics` (default) or a custom filename via CLI.
* Optionally exports schedule as CSV.
* Prints the parsed schedule table for preview.
* Loads semester start and end dates from environment variables.

---

## 🛠️ Prerequisites

* Python 3.8 or higher
* Basic command line / terminal knowledge

---

## 🚀 Setup Instructions

### 1. Clone or Download the Repository

Place your exported `index.html` schedule file in the project root directory.

---

### 2. Create and Activate a Python Virtual Environment

#### Unix/Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*If you get a script execution policy error:*

Run PowerShell as administrator and execute:

```powershell
Set-ExecutionPolicy RemoteSigned
```

Then reactivate the virtual environment.

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set Environment Variables

The script loads semester dates from environment variables via `python-dotenv`.

Create a `.env` file in your project root with these variables (date format flexible but recommended `DD-MM-YYYY`):

```env
START_DATE=01-07-2025
END_DATE=01-09-2025
```

---

### 5. Running the Script

Run the script with:

```bash
python main.py -o my_schedule.ics --csv
```

Options:

* `-o` or `--output`: specify output `.ics` filename (default: `schedule.ics`)
* `--csv`: export a CSV file (`schedule.csv`) alongside `.ics`

---

## 📦 Package Structure

```
course-schedule/       
├── course_schedule/    
│   ├── __init__.py     # package init + config + maybe main.py
│   ├── config.py       # env vars loading
│   └── main.py         # Schedule class and core logic
├── main.py             # CLI entry point script at repo root
├── requirements.txt
├── .env
├── index.html

```

---

## 📞 Support / Contributing

Feel free to open issues or pull requests on GitHub! Contributions and feedback are welcome.

---
