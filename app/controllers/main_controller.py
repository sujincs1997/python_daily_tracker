from PySide6.QtCore import QObject, Signal
from app.controllers.task_controller import TaskController
from app.controllers.settings_controller import SettingsController
from app.services.timer_service import TimerService
from app.services.notification_service import NotificationService
from app.utils.config import config_manager
from app.utils.logger import logger

class MainController(QObject):
    # Signals
    theme_changed = Signal(str)  # Emits "dark" or "light"

    def __init__(self):
        super().__init__()
        
        # Instantiate sub-controllers and services
        self.task_controller = TaskController()
        self.settings_controller = SettingsController()
        self.timer_service = TimerService()
        self.notification_service = NotificationService(self.timer_service)
        
        # Connect auto-save trigger from timer service
        self.timer_service.minute_passed.connect(self.auto_save_active_task)

    def change_theme(self, theme_name: str) -> bool:
        """Saves theme configuration and notifies GUI views."""
        if theme_name not in ["dark", "light"]:
            return False
        
        success = self.settings_controller.update_config_setting("theme", theme_name)
        if success:
            logger.info(f"Theme switched to: {theme_name}")
            self.theme_changed.emit(theme_name)
        return success

    def get_current_theme(self) -> str:
        """Retrieves active UI theme preference."""
        return self.settings_controller.get_config_setting("theme", "dark")

    def auto_save_active_task(self):
        """Automatically saves the running task's duration and state to the database every minute."""
        active_task_uuid = self.timer_service.current_task_uuid
        active_task_id = self.timer_service.current_task_id
        
        if not active_task_uuid or not active_task_id:
            logger.debug("Auto-save skipped: No active task running.")
            return

        elapsed_duration = self.timer_service.elapsed_seconds
        logger.info(f"Auto-saving task {active_task_uuid} with duration: {elapsed_duration}s")
        
        # Update database task duration and timestamps
        success = self.task_controller.update_task(
            task_id=active_task_id,
            data={
                "duration": elapsed_duration,
                "status": "In Progress"  # Ensure status is synced
            }
        )
        
        if success:
            logger.debug("Auto-save completed successfully.")
        else:
            logger.error("Auto-save failed to update task in database.")
            
    def shutdown(self) -> bool:
        """Performs cleanup tasks before application closure.
        
        Returns True if safe to close, False if closure should be cancelled (e.g. running timer).
        """
        if self.timer_service.is_running:
            # Caller/view should prompt user confirmation
            logger.warning("Attempted shutdown with running timer.")
            return False
            
        logger.info("MainController shutdown complete.")
        return True
