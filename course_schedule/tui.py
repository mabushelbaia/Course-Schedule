import os

import questionary


def interactive_prompts(args) -> None:
    args.username = args.username or os.environ.get("RITAJ_USERNAME")
    if not args.username:
        args.username = questionary.text("Ritaj username:").ask()

    args.password = args.password or os.environ.get("RITAJ_PASSWORD")
    if not args.password:
        args.password = questionary.password("Ritaj password:").ask()

    fs_url = args.flaresolverr_url
    args.flaresolverr_url = questionary.text(
        "FlareSolverr URL:", default=fs_url
    ).ask()

    include_cal = questionary.confirm(
        "Include academic calendar events?", default=True
    ).ask()
    args.no_calendar = not include_cal

    if include_cal:
        sem_choice = questionary.select(
            "Semester:",
            choices=["auto-detect", "Fall", "Spring", "Summer"],
        ).ask()
        if sem_choice != "auto-detect":
            args.semester = sem_choice

        cal_mode = questionary.select(
            "Calendar mode:",
            choices=[
                questionary.Choice("Merged into one .ics file", value="merged"),
                questionary.Choice("Separate .ics files", value="separate"),
            ],
        ).ask()
        args.calendar = cal_mode

    output = questionary.text("Output file:", default=args.output).ask()
    args.output = output

    if include_cal and cal_mode == "separate":
        default_cal = _default_calendar_path(output)
        args.calendar_output = questionary.text(
            "Academic calendar output file:", default=default_cal
        ).ask()

    args.csv = questionary.confirm("Export CSV?", default=False).ask()


def _default_calendar_path(schedule_path: str) -> str:
    import os
    base, ext = os.path.splitext(schedule_path)
    if "schedule" in base:
        return base.replace("schedule", "calendar") + ext
    return "calendar" + ext
