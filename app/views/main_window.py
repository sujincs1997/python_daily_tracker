import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, 
    QListWidget, QStackedWidget, QLabel, QMessageBox, QSystemTrayIcon, QStyle
)
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QKeySequence, QShortcut, QCloseEvent

# Style Sheets
from app.views.styles import DARK_THEME, LIGHT_THEME
from app.utils.logger import logger

class TimeoutMessageBox(QMessageBox):
    """Custom QMessageBox with countdown timer that clicks 'No' on timeout."""
    def __init__(self, timeout_secs, title, text, parent=None):
        super().__init__(parent)
        self.timeout_secs = timeout_secs
        self.remaining = timeout_secs
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.Yes)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        
    def showEvent(self, event):
        super().showEvent(event)
        self._update_text()
        self.timer.start(1000)
        
    def _tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.timer.stop()
            # Default to 'No' (idle / stopped working)
            no_btn = self.button(QMessageBox.No)
            if no_btn:
                no_btn.click()
            else:
                self.reject()
        else:
            self._update_text()
            
    def _update_text(self):
        self.setInformativeText(f"This prompt will auto-decline (Stop Task) in {self.remaining} seconds if there is no response.")

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Configure Window
        self.setWindowTitle("Daily Office Work Tracker")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 750)
        
        # Setup Core System Tray Icon
        self.tray_icon = QSystemTrayIcon(self)
        # Fallback to standard Qt icon if icon files aren't found
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setToolTip("Daily Office Work Tracker")
        self.tray_icon.show()
        
        # Connect Notification Service
        self.controller.notification_service.notify.connect(self.show_desktop_notification)
        self.controller.notification_service.ask_still_working.connect(self.prompt_still_working)
        self.controller.notification_service.start_break_monitoring()
        
        # Theme Changes listener
        self.controller.theme_changed.connect(self.apply_theme)
        
        self.setup_ui()
        self.setup_shortcuts()
        
        # Load theme
        self.apply_theme(self.controller.get_current_theme())
        
        # Auto-select Dashboard
        self.nav_list.setCurrentRow(0)

    def setup_ui(self):
        """Constructs the sidebar and stacked content area layout."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Sidebar Frame
        self.sidebar = QFrame(self)
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        sidebar_title = QLabel("Daily Tracker", self.sidebar)
        sidebar_title.setObjectName("SidebarTitle")
        sidebar_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(sidebar_title)
        
        self.nav_list = QListWidget(self.sidebar)
        self.nav_list.setObjectName("NavList")
        
        # Define sidebar items
        self.nav_items = [
            "Dashboard",
            "New Task",
            "Running Task",
            "Task History",
            "Projects",
            "Categories",
            "Assigned By",
            "Reports",
            "Import Data",
            "Export Data",
            "Settings",
            "About"
        ]
        self.nav_list.addItems(self.nav_items)
        self.nav_list.currentRowChanged.connect(self.navigate_to_pane)
        sidebar_layout.addWidget(self.nav_list)
        
        main_layout.addWidget(self.sidebar)
        
        # 2. Content Pane Stacked Widget
        self.content_stack = QStackedWidget(self)
        self.content_stack.setObjectName("ContentFrame")
        
        # Lazy imports of child views to avoid circular imports during setup
        from app.views.dashboard import DashboardView
        from app.views.task_form import TaskFormView
        from app.views.task_history import TaskHistoryView
        from app.views.settings_view import SettingsView, ProjectsView, CategoriesView, AssignedByView
        from app.views.reports_view import ReportsView
        from app.views.import_export_view import ImportView, ExportView, AboutView
        
        # Instantiate and add views
        self.dashboard_view = DashboardView(self.controller, self)
        self.task_form_view = TaskFormView(self.controller, self)
        self.running_task_view = QWidget(self) # We will bind running task widget dynamically
        self.task_history_view = TaskHistoryView(self.controller, self)
        self.projects_view = ProjectsView(self.controller, self)
        self.categories_view = CategoriesView(self.controller, self)
        self.assigned_by_view = AssignedByView(self.controller, self)
        self.reports_view = ReportsView(self.controller, self)
        self.import_view = ImportView(self.controller, self)
        self.export_view = ExportView(self.controller, self)
        self.settings_view = SettingsView(self.controller, self)
        self.about_view = AboutView(self.controller, self)
        
        # Running task widget is a customized task card/form
        self.setup_running_task_tab()
        
        # Add to stack in index order matching self.nav_items
        self.content_stack.addWidget(self.dashboard_view)      # 0
        self.content_stack.addWidget(self.task_form_view)       # 1
        self.content_stack.addWidget(self.running_task_view)    # 2
        self.content_stack.addWidget(self.task_history_view)    # 3
        self.content_stack.addWidget(self.projects_view)        # 4
        self.content_stack.addWidget(self.categories_view)      # 5
        self.content_stack.addWidget(self.assigned_by_view)    # 6
        self.content_stack.addWidget(self.reports_view)         # 7
        self.content_stack.addWidget(self.import_view)          # 8
        self.content_stack.addWidget(self.export_view)          # 9
        self.content_stack.addWidget(self.settings_view)        # 10
        self.content_stack.addWidget(self.about_view)           # 11
        
        main_layout.addWidget(self.content_stack)

    def setup_running_task_tab(self):
        """Constructs a custom layout for the 'Running Task' screen."""
        layout = QVBoxLayout(self.running_task_view)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel("Active Timer Monitor", self.running_task_view)
        title_label.setObjectName("SectionHeading")
        layout.addWidget(title_label)
        
        # Embed a Running Task Panel (imported from task_form)
        from app.views.task_form import ActiveTimerWidget
        self.active_timer_widget = ActiveTimerWidget(self.controller, self)
        layout.addWidget(self.active_timer_widget)
        layout.addStretch()

    def setup_shortcuts(self):
        """Initializes application-wide keyboard shortcuts."""
        # Ctrl+N -> New Task
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new.activated.connect(lambda: self.nav_list.setCurrentRow(1))
        
        # Ctrl+F -> Search
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.activated.connect(self.focus_search)
        
        # Ctrl+S -> Save
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.trigger_save)
        
        # Space -> Start/Pause Active Timer
        self.shortcut_space = QShortcut(QKeySequence("Space"), self)
        self.shortcut_space.activated.connect(self.trigger_timer_toggle)

    def focus_search(self):
        """Navigates to Task History and sets focus on the search input box."""
        self.nav_list.setCurrentRow(3)
        self.task_history_view.search_input.setFocus()

    def trigger_save(self):
        """Triggers submit operations on the active view (e.g. Save Task Form)."""
        current_idx = self.content_stack.currentIndex()
        if current_idx == 1:
            self.task_form_view.save_task()
        else:
            logger.debug("Ctrl+S pressed, but current screen does not support saving.")

    def trigger_timer_toggle(self):
        """Toggles between Start/Pause on active running timer."""
        # Spaces trigger timer actions in the timer view
        self.active_timer_widget.toggle_timer_state()

    @Slot(int)
    def navigate_to_pane(self, index: int):
        """Switches content panel and refreshes state variables."""
        self.content_stack.setCurrentIndex(index)
        
        # Refresh target views on transition
        if index == 0:
            self.dashboard_view.refresh_dashboard()
        elif index == 1:
            self.task_form_view.prepare_new_task()
        elif index == 2:
            self.active_timer_widget.refresh_active_timer()
        elif index == 3:
            self.task_history_view.refresh_history()
        elif index == 4:
            self.projects_view.refresh_projects()
        elif index == 5:
            self.categories_view.refresh_categories()
        elif index == 6:
            self.assigned_by_view.refresh_assigned_by()
        elif index == 7:
            self.reports_view.refresh_combos()
        elif index == 10:
            self.settings_view.load_settings()

    @Slot(str)
    def apply_theme(self, theme_name: str):
        """Applies QSS styles to the main window."""
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)
            
    @Slot(str, str)
    def show_desktop_notification(self, title: str, message: str):
        """Pushes system tray notification message bubbles."""
        if QSystemTrayIcon.supportsMessages():
            # Show message (title, message, icon, duration_ms)
            self.tray_icon.showMessage(
                title, message, 
                QSystemTrayIcon.Information, 
                5000
            )
        else:
            logger.warning(f"Notifications not supported. Alert: {title} - {message}")
            QMessageBox.information(self, title, message)

    @Slot(str, str)
    def prompt_still_working(self, task_uuid, task_title):
        """Prompts the user to check if they are still working on the active task."""
        logger.info(f"Displaying activity check prompt for task {task_uuid}.")
        
        dialog = TimeoutMessageBox(
            timeout_secs=60,
            title="Activity Check",
            text=f"Are you still working on the task:\n'{task_title}'?",
            parent=self
        )
        
        result = dialog.exec()
        
        if result == QMessageBox.No:
            logger.info(f"User selected 'No' or prompt timed out for task {task_uuid}. Stopping task.")
            # Stop timer and auto-save stats
            stats = self.controller.timer_service.stop()
            if stats:
                # Update task status to Paused and duration in DB
                self.controller.task_controller.update_task(
                    task_id=stats["task_id"],
                    data={
                        "duration": stats["duration"],
                        "start_time": stats["start_time"],
                        "end_time": stats["end_time"],
                        "status": "Paused"
                    }
                )
            
            # Switch to Task History tab to select new task
            self.nav_list.setCurrentRow(3)
            QMessageBox.information(
                self, "Task Paused", 
                "The active task timer has been stopped and saved as 'Paused' due to inactivity or selection.\n\nPlease select or create a new task."
            )
        else:
            logger.info(f"User is still working on task {task_uuid}. Continuing tracking.")

    def closeEvent(self, event: QCloseEvent):
        """Intercepts window close to warning user if timer is active."""
        if self.controller.timer_service.is_running:
            reply = QMessageBox.question(
                self, 'Exit Confirmation',
                "A task timer is currently running. Closing the application will stop and save the current timer session.\n\nAre you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Stop and save progress
                logger.info("Stopping timer and saving during application exit.")
                self.controller.auto_save_active_task()
                self.controller.timer_service.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
