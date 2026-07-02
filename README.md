# Daily Office Work Tracker

A lightweight, modern, and offline-first Python desktop application built to track daily office tasks, work durations, productivity, and work completion.

## Features

- **Dashboard Statistics**: Real-time cards listing today's total hours, completed/pending tasks, average task duration, and longest/shortest tasks.
- **Task Tracking**: Start, pause, resume, and stop timers directly. Automatically calculates task durations and logs start/end times.
- **Weekly Productivity Graph**: A visual Matplotlib bar chart plotting hours worked per day over the last week (auto-adjusts to Light/Dark mode themes).
- **Search & Filters**: Search task names, descriptions, or assignee names. Filter by today, yesterday, last 7 days, projects, categories, priority, or status.
- **Reporting & Exports**: Generate custom category-wise, project-wise, or productivity reports and export them to **CSV**, **Excel**, or **PDF** layouts.
- **Theme Support**: Fluent UI styling with dynamic **Dark Mode** and **Light Mode** toggles.
- **Desktop Alerts**: Notifications for 2-hour task duration warnings, 90-minute break stretch reminders, and end-of-day warnings.
- **Auto-Save**: Active task durations are automatically backed up to the database every 60 seconds of running time.
- **Data Imports**: Bulk import projects, categories, assignee profiles, or task history from Excel and CSV sheets.
- **Database Utilities**: Create and restore database backups with file-handling security directly from the UI.

---

## Technology Stack

- **GUI framework**: PySide6 (Qt6 for Python)
- **Database ORM**: SQLAlchemy with SQLite
- **Plotting & Visuals**: Matplotlib
- **Data Analytics**: Pandas
- **Reporting & Exporting**: OpenPyXL (Excel), ReportLab (PDF)
- **Packaging**: PyInstaller

---

## Folder Architecture

```text
python_daily_tracker/
│
├── main.py                 # Application entry point
├── seed_db.py              # Script to populate sample metadata
├── verify_backend.py       # Programmatic backend validation script
├── requirements.txt        # Third-party library dependencies
├── tracker.spec            # PyInstaller packaging configuration
│
└── app/
    ├── database/           # Engine and connection context managers
    ├── models/             # SQLAlchemy schemas (Task, Project, Category, etc.)
    ├── controllers/        # Business logic bridging Views and Models
    ├── services/           # Backend timer, imports/exports, notifications
    ├── utils/              # JSON configs, rolling file logger configurations
    └── views/              # PySide6 windows, layouts, QSS stylesheet definitions
```

---

## Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.12+** installed on your Windows machine.

### 2. Install Dependencies
Open PowerShell or Command Prompt, navigate to the project directory, and install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Database Seeding (Optional)
The application automatically seeds default projects, categories, and assignees on its very first launch. However, you can manually trigger database seeding at any time:
```bash
python seed_db.py
```

### 4. Running the Application
Launch the graphical interface:
```bash
python main.py
```

---

## Packaging Standalone Executable (Windows)

To bundle the application into a standalone Windows folder/executable containing all libraries:
1. Ensure PyInstaller is installed (`pip install pyinstaller`).
2. Run the packaging command in the root folder:
   ```bash
   pyinstaller tracker.spec
   ```
3. Once completed, the standalone application files can be found in `dist/DailyOfficeWorkTracker/`. Double click `DailyOfficeWorkTracker.exe` to run.

---

## Keyboard Shortcuts

The application registers the following global keyboard shortcuts to speed up daily work:

| Shortcut | Action |
| --- | --- |
| **Ctrl + N** | Navigate to create a New Task |
| **Ctrl + S** | Save/Submit the active task form |
| **Ctrl + F** | Navigate to Task History and focus the search box |
| **Space** | Play/Pause the active timer (when on the Running Task screen) |
