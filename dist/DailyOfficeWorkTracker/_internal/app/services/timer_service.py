from datetime import datetime
from PySide6.QtCore import QObject, Signal, QTimer
from app.utils.logger import logger

class TimerService(QObject):
    # Signals
    tick = Signal(str, int)  # Emits (formatted_time_str, elapsed_seconds)
    status_changed = Signal(str)  # Emits (status_str)
    minute_passed = Signal()  # Emits every 60 seconds for auto-save

    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        
        self.elapsed_seconds: int = 0
        self.start_time: datetime = None
        self.end_time: datetime = None
        self.is_running: bool = False
        self.is_paused: bool = False
        
        self.current_task_id: int = None
        self.current_task_uuid: str = None
        self.accumulated_seconds_this_session: int = 0

    def start(self, task_id: int, task_uuid: str, current_duration: int = 0):
        """Starts the timer for a specific task."""
        if self.is_running and not self.is_paused:
            logger.warning("Timer is already running!")
            return

        self.current_task_id = task_id
        self.current_task_uuid = task_uuid
        self.elapsed_seconds = current_duration
        self.accumulated_seconds_this_session = 0
        
        if not self.is_paused:
            self.start_time = datetime.now()
            logger.info(f"Timer started for task {task_uuid} at {self.start_time}")
        else:
            logger.info(f"Timer resumed for task {task_uuid} after pause")

        self.is_running = True
        self.is_paused = False
        self.timer.start(1000)  # Tick every 1 second
        self.status_changed.emit("In Progress")

    def pause(self):
        """Pauses the timer."""
        if not self.is_running or self.is_paused:
            return
        
        self.timer.stop()
        self.is_paused = True
        logger.info(f"Timer paused for task {self.current_task_uuid}")
        self.status_changed.emit("Paused")

    def resume(self):
        """Resumes the timer."""
        if not self.is_running or not self.is_paused:
            return
        
        self.is_paused = False
        self.timer.start(1000)
        logger.info(f"Timer resumed for task {self.current_task_uuid}")
        self.status_changed.emit("In Progress")

    def stop(self) -> dict:
        """Stops the timer and returns session stats."""
        if not self.is_running:
            return {}

        self.timer.stop()
        self.end_time = datetime.now()
        self.is_running = False
        self.is_paused = False
        
        # Calculate totals
        hours = self.elapsed_seconds // 3600
        minutes = (self.elapsed_seconds % 3600) // 60
        
        stats = {
            "task_id": self.current_task_id,
            "task_uuid": self.current_task_uuid,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.elapsed_seconds,
            "hours": hours,
            "minutes": minutes
        }
        
        logger.info(f"Timer stopped for task {self.current_task_uuid}. Stats: {stats}")
        self.status_changed.emit("Stopped")
        
        # Reset tracker properties
        self.current_task_id = None
        self.current_task_uuid = None
        self.elapsed_seconds = 0
        self.accumulated_seconds_this_session = 0
        
        return stats

    def _on_tick(self):
        """Increments timer counter and emits ticks."""
        self.elapsed_seconds += 1
        self.accumulated_seconds_this_session += 1
        
        formatted = self.format_duration(self.elapsed_seconds)
        self.tick.emit(formatted, self.elapsed_seconds)
        
        # Auto-save trigger check
        if self.accumulated_seconds_this_session % 60 == 0:
            logger.debug("60 seconds elapsed. Triggering auto-save signal.")
            self.minute_passed.emit()

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Helper to format duration in seconds to 00:00:00 format."""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
