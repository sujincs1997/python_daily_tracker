from datetime import datetime, time
from PySide6.QtCore import QObject, Signal, QTimer
from app.utils.config import config_manager
from app.utils.logger import logger
from app.database.connection import get_db_session
from app.models.task import Task

class NotificationService(QObject):
    # Signals to UI
    notify = Signal(str, str)  # Emits (title, message)

    def __init__(self, timer_service):
        super().__init__()
        self.timer_service = timer_service
        
        # Connect to task timer ticks to monitor single task duration
        self.timer_service.tick.connect(self._check_task_duration)
        
        # Internal timers for background checks
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self._perform_periodic_checks)
        self.check_timer.start(60 * 1000)  # Check every 1 minute
        
        # Track timers in minutes/seconds
        self.break_timer_seconds: int = 0
        self.eod_notified_today: bool = False
        self.incomplete_notified_today: bool = False
        self.last_checked_day: int = datetime.now().day

    def start_break_monitoring(self):
        """Starts monitoring elapsed time for breaks."""
        # We can hook into a 1-second timer or rely on a QTimer tick.
        # Let's run a QTimer for break monitoring
        self.break_monitoring_timer = QTimer(self)
        self.break_monitoring_timer.timeout.connect(self._tick_break_timer)
        self.break_monitoring_timer.start(1000)  # Tick every second

    def _tick_break_timer(self):
        """Ticks the break timer. Every 90 mins (or break_interval_minutes), prompts a reminder."""
        cfg = config_manager.get("notifications", {})
        if not cfg.get("break_reminder", True):
            return

        self.break_timer_seconds += 1
        interval_secs = cfg.get("break_interval_minutes", 90) * 60
        
        if self.break_timer_seconds >= interval_secs:
            self.break_timer_seconds = 0
            logger.info("Triggering break reminder.")
            self.notify.emit("Take a Break!", "You've been working continuously for 90 minutes. Step away and stretch!")

    def reset_break_timer(self):
        """Resets the break timer (e.g. when user takes a break)."""
        self.break_timer_seconds = 0

    def _check_task_duration(self, formatted_time: str, elapsed_seconds: int):
        """Triggered on every timer service tick to monitor running task duration."""
        cfg = config_manager.get("notifications", {})
        if not cfg.get("task_duration_warning", True):
            return

        warning_secs = cfg.get("task_warning_hours", 2) * 3600
        
        # Trigger reminder exactly at multiples of 2 hours
        if elapsed_seconds > 0 and elapsed_seconds % warning_secs == 0:
            hours = elapsed_seconds // 3600
            logger.info(f"Task running for {hours} hours. Sending alert.")
            self.notify.emit("Long-Running Task", f"Your current task has been running for {hours} hours. Remember to update its status or take a break!")

    def _perform_periodic_checks(self):
        """Checks for end-of-day and incomplete tasks every minute."""
        now = datetime.now()
        
        # Reset daily notification trackers if the day changes
        if now.day != self.last_checked_day:
            self.eod_notified_today = False
            self.incomplete_notified_today = False
            self.last_checked_day = now.day

        cfg = config_manager.get("notifications", {})
        
        # 1. End of Day Reminder
        if cfg.get("eod_reminder", True) and not self.eod_notified_today:
            eod_time_str = cfg.get("eod_time", "17:30")
            try:
                eod_h, eod_m = map(int, eod_time_str.split(":"))
                eod_t = time(eod_h, eod_m)
                if now.time() >= eod_t:
                    self.notify.emit("End of Day", "It's near the end of your standard working hours. Don't forget to stop running tasks and log your work!")
                    self.eod_notified_today = True
                    logger.info("EOD reminder triggered.")
            except Exception as e:
                logger.error(f"Error parsing EOD time {eod_time_str}: {e}")

        # 2. Incomplete Tasks Reminder
        # Trigger once in the morning (e.g., after 9:00 AM) if not notified today
        if cfg.get("incomplete_task_reminder", True) and not self.incomplete_notified_today:
            if now.hour >= 9:
                self.check_and_notify_incomplete_tasks()

    def check_and_notify_incomplete_tasks(self):
        """Queries database for incomplete tasks and notifies the user."""
        try:
            with get_db_session() as session:
                # Incomplete statuses: 'Not Started', 'In Progress', 'Paused'
                incomplete_count = session.query(Task).filter(
                    Task.status.in_(["Not Started", "In Progress", "Paused"])
                ).count()
                
                if incomplete_count > 0:
                    self.notify.emit("Incomplete Tasks", f"You have {incomplete_count} incomplete tasks. Open the dashboard to resume or complete them!")
                    self.incomplete_notified_today = True
                    logger.info(f"Incomplete task reminder triggered. Found {incomplete_count} tasks.")
        except Exception as e:
            logger.error(f"Error checking incomplete tasks: {e}")
