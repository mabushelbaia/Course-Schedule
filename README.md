# 📅 Course Schedule

This tool parses a university schedule from an `index.html` file and converts it into an iCalendar `.ics` file compatible with calendar applications.

---

## ✨ Features

- Parses course schedule from HTML.
- Converts schedule to `.ics` iCalendar format.
- Saves output as `schedule.ics`.
- Prints parsed schedule table for preview.
- Loads semester dates and settings from environment variables.

---

## 🛠️ Prerequisites

- Python 3.8 or higher installed on your system.
- Basic familiarity with command line/terminal.

---

## 🚀 Setup Instructions

### 1. Clone or Download the Repository

Download the project files and place your schedule HTML file named `index.html` in the project root directory.

---

### 2. Create a Python Virtual Environment

A virtual environment keeps dependencies isolated from your system Python.

#### On Unix/Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
````

#### On Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> If you get an error about script execution policy, run PowerShell as administrator and execute:

```powershell
Set-ExecutionPolicy RemoteSigned
```

Then activate again.

---

### 3. Install Dependencies

With your virtual environment activated, install required packages:

```bash
pip install -r requirements.txt
```

---

### 4. Set Environment Variables

The script reads semester dates from environment variables loaded by `python-dotenv`:

- `START_DATE` (format: `DD-MM-YYYY`)
- `END_DATE` (format: `DD-MM-YYYY`)

Create a `.env` file in your project root with the following content:

```env
START_DATE=01-07-2025
END_DATE=01-09-2025

```

---

### 5. Running the Script

Run the main script as usual:

```bash
python main.py
```

The script will load these environment variables and use them to process the schedule.

---

## 🐞 Troubleshooting

- **Environment variables not found**:
  Ensure your `.env` file exists and that `python-dotenv` is installed and used in your code to load it.

- **Date format errors**:
  Make sure dates in `.env` use the `YYYY-MM-DD` format.

- **FileNotFoundError**:
  Confirm `index.html` exists in the script's working directory.

- **Encoding issues**:
  Use UTF-8 encoding in your terminal and files.

- **Virtual environment activation**:
  Use the correct command per your OS as shown above.

---
