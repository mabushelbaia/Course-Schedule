# Course Schedule

A Python script that scrapes course schedule out from **[Course Schedule](https://ritaj.birzeit.edu/student/schedule)** and converts it to a calendar file <kbd>.ics</kbd> that you can later upload to any calendaring app.


## Installation
- Clone the repository.
- Save the **[Course Schedule](https://ritaj.birzeit.edu/student/schedule)** HTML page into index.html.

    - You can alternatively press <kbd>ctrl</kbd> + <kbd>u</kbd> to view the source code in your browser, then copy it to index.html.

- Install the requirements.txt file

    -  ```pip install -r requirements.txt```

- Run the script
  - ```python main.py```

---



## Future Work
- [ ] Find a way to bypass Cloudflare protection to send GET requests directly to Ritaj.
- [ ] Include the building name in the exported calendar.
- [ ] Add a way to automatically upload the file to Google Calendar.
