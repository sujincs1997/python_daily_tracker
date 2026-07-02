from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox
)
from PySide6.QtCore import Slot, Qt

from app.utils.logger import logger

class TaskHistoryView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        self.setup_ui()
        self.refresh_history()

    def setup_ui(self):
        """Constructs the search filters and data table logs layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        heading = QLabel("Task History & Logs", self)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)
        
        # 1. SEARCH & FILTER CARD
        filter_card = QFrame(self)
        filter_card.setProperty("class", "Card")
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setSpacing(10)
        
        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(filter_card)
        self.search_input.setPlaceholderText("Search by Task Name, Project, Category, Assignee, UUID... (Ctrl+F)")
        self.search_input.textChanged.connect(self.apply_filters)
        search_layout.addWidget(self.search_input)
        
        self.btn_clear = QPushButton("Clear Filters", filter_card)
        self.btn_clear.clicked.connect(self.clear_all_filters)
        search_layout.addWidget(self.btn_clear)
        filter_layout.addLayout(search_layout)
        
        # Dropdown Filters Row
        combos_layout = QHBoxLayout()
        combos_layout.setSpacing(10)
        
        # Date Filter
        self.cmb_date = QComboBox(filter_card)
        self.cmb_date.addItems(["All Time", "Today", "Yesterday", "Last 7 Days", "Current Month"])
        self.cmb_date.currentTextChanged.connect(self.apply_filters)
        combos_layout.addWidget(self.cmb_date)
        
        # Project Filter
        self.cmb_project = QComboBox(filter_card)
        self.cmb_project.currentTextChanged.connect(self.apply_filters)
        combos_layout.addWidget(self.cmb_project)
        
        # Category Filter
        self.cmb_category = QComboBox(filter_card)
        self.cmb_category.currentTextChanged.connect(self.apply_filters)
        combos_layout.addWidget(self.cmb_category)
        
        # Assigned By Filter
        self.cmb_assigned_by = QComboBox(filter_card)
        self.cmb_assigned_by.currentTextChanged.connect(self.apply_filters)
        combos_layout.addWidget(self.cmb_assigned_by)
        
        # Priority Filter
        self.cmb_priority = QComboBox(filter_card)
        self.cmb_priority.currentTextChanged.connect(self.apply_filters)
        combos_layout.addWidget(self.cmb_priority)
        
        # Status Filter
        self.cmb_status = QComboBox(filter_card)
        self.cmb_status.currentTextChanged.connect(self.apply_filters)
        combos_layout.addWidget(self.cmb_status)
        
        filter_layout.addLayout(combos_layout)
        layout.addWidget(filter_card)

        # 2. MAIN LOGS TABLE CARD
        table_card = QFrame(self)
        table_card.setProperty("class", "Card")
        table_layout = QVBoxLayout(table_card)
        
        self.table = QTableWidget(table_card)
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID", "Fav", "Task #", "Title", "Category", 
            "Project", "Assigned By", "Priority", "Status", 
            "Completion", "Duration", "Date"
        ])
        
        # Hide ID column
        self.table.hideColumn(0)
        
        # Resize parameters
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Stretch Title
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_row_double_clicked)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_card)
        
        # 3. ACTIONS PANEL ROW
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        self.btn_new = QPushButton("New Task", self)
        self.btn_new.setObjectName("PrimaryButton")
        self.btn_new.clicked.connect(self.create_new_task_redirect)
        actions_layout.addWidget(self.btn_new)
        
        self.btn_start = QPushButton("Start/Resume Timer", self)
        self.btn_start.setObjectName("SuccessButton")
        self.btn_start.clicked.connect(self.start_selected_task)
        actions_layout.addWidget(self.btn_start)
        
        self.btn_edit = QPushButton("Edit Details", self)
        self.btn_edit.clicked.connect(self.edit_selected_task)
        actions_layout.addWidget(self.btn_edit)
        
        self.btn_duplicate = QPushButton("Duplicate Task", self)
        self.btn_duplicate.clicked.connect(self.duplicate_selected_task)
        actions_layout.addWidget(self.btn_duplicate)
        
        self.btn_fav = QPushButton("Toggle Favorite", self)
        self.btn_fav.clicked.connect(self.favorite_selected_task)
        actions_layout.addWidget(self.btn_fav)
        
        self.btn_delete = QPushButton("Delete Log", self)
        self.btn_delete.setObjectName("DangerButton")
        self.btn_delete.clicked.connect(self.delete_selected_task)
        actions_layout.addWidget(self.btn_delete)
        
        layout.addLayout(actions_layout)

    def create_new_task_redirect(self):
        """Redirects to the New Task tab."""
        self.parentWidget().parentWidget().nav_list.setCurrentRow(1)

    def populate_combos(self):
        """Loads items dynamically without triggering recursive filters."""
        # Block signals temporarily to prevent infinite loop of apply_filters
        self.cmb_project.blockSignals(True)
        self.cmb_category.blockSignals(True)
        self.cmb_assigned_by.blockSignals(True)
        self.cmb_priority.blockSignals(True)
        self.cmb_status.blockSignals(True)
        
        # Reset combos
        self.cmb_project.clear()
        self.cmb_project.addItem("All Projects", None)
        for proj in self.controller.settings_controller.get_all_projects(include_archived=True):
            self.cmb_project.addItem(proj["project_name"], proj["id"])
            
        self.cmb_category.clear()
        self.cmb_category.addItem("All Categories", None)
        for cat in self.controller.settings_controller.get_all_categories():
            self.cmb_category.addItem(cat["category_name"], cat["id"])
            
        self.cmb_assigned_by.clear()
        self.cmb_assigned_by.addItem("All Assignees", None)
        for ab in self.controller.settings_controller.get_all_assigned_by():
            self.cmb_assigned_by.addItem(ab["person_name"], ab["id"])
            
        self.cmb_priority.clear()
        self.cmb_priority.addItem("All Priorities")
        for p in self.controller.settings_controller.get_config_setting("priorities", []):
            self.cmb_priority.addItem(p)
            
        self.cmb_status.clear()
        self.cmb_status.addItem("All Statuses")
        for s in self.controller.settings_controller.get_config_setting("statuses", []):
            self.cmb_status.addItem(s)

        self.cmb_project.blockSignals(False)
        self.cmb_category.blockSignals(False)
        self.cmb_assigned_by.blockSignals(False)
        self.cmb_priority.blockSignals(False)
        self.cmb_status.blockSignals(False)

    def get_filter_values(self) -> dict:
        """Collects filter choices from GUI dropdowns."""
        return {
            "date_filter": self.cmb_date.currentText(),
            "project_id": self.cmb_project.currentData(),
            "category_id": self.cmb_category.currentData(),
            "assigned_by_id": self.cmb_assigned_by.currentData(),
            "priority": self.cmb_priority.currentText() if self.cmb_priority.currentIndex() > 0 else None,
            "status": self.cmb_status.currentText() if self.cmb_status.currentIndex() > 0 else None
        }

    def refresh_history(self):
        """Loads settings, populates combos, and performs default queries."""
        self.populate_combos()
        self.apply_filters()

    @Slot()
    def apply_filters(self):
        """Fetches filtered logs from TaskController and displays in the table."""
        filters = self.get_filter_values()
        search_query = self.search_input.text().strip()
        
        tasks = self.controller.task_controller.search_and_filter_tasks(filters, search_query)
        
        self.table.setRowCount(0)
        for i, t in enumerate(tasks):
            self.table.insertRow(i)
            
            # Formulate items
            item_id = QTableWidgetItem(str(t["id"]))
            
            is_fav = self.controller.task_controller.is_favorite(t["id"])
            item_fav = QTableWidgetItem("★" if is_fav else "☆")
            item_fav.setTextAlignment(Qt.AlignCenter)
            if is_fav:
                item_fav.setForeground(Qt.yellow)
            
            self.table.setItem(i, 0, item_id)
            self.table.setItem(i, 1, item_fav)
            self.table.setItem(i, 2, QTableWidgetItem(t["task_number"]))
            self.table.setItem(i, 3, QTableWidgetItem(t["title"]))
            self.table.setItem(i, 4, QTableWidgetItem(t["category_name"]))
            self.table.setItem(i, 5, QTableWidgetItem(t["project_name"]))
            self.table.setItem(i, 6, QTableWidgetItem(t["assigned_by_name"]))
            self.table.setItem(i, 7, QTableWidgetItem(t["priority"]))
            self.table.setItem(i, 8, QTableWidgetItem(t["status"]))
            
            item_comp = QTableWidgetItem(f"{t['completion']}%")
            item_comp.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 9, item_comp)
            
            self.table.setItem(i, 10, QTableWidgetItem(t["duration_formatted"]))
            self.table.setItem(i, 11, QTableWidgetItem(t["created_date"]))

    def get_selected_task_id(self) -> int:
        """Helper to retrieve active selected row Task ID."""
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return -1
        row = selected_ranges[0].topRow()
        return int(self.table.item(row, 0).text())

    def edit_selected_task(self):
        """Loads selected task into TaskForm and switches tabs."""
        task_id = self.get_selected_task_id()
        if task_id < 0:
            QMessageBox.warning(self, "No Selection", "Please select a task from the list to edit.")
            return
            
        main_win = self.parentWidget().parentWidget() # Main shell
        main_win.task_form_view.load_task_to_edit(task_id)
        main_win.nav_list.setCurrentRow(1) # Navigate to task form (index 1)

    def on_row_double_clicked(self, model_index):
        """Double clicking a row triggers task edit."""
        self.edit_selected_task()

    def start_selected_task(self):
        """Starts timer service tracking on selected task."""
        task_id = self.get_selected_task_id()
        if task_id < 0:
            QMessageBox.warning(self, "No Selection", "Please select a task from the list to track.")
            return

        task = self.controller.task_controller.get_task_by_id(task_id)
        if not task:
            return
            
        if task["status"] in ["Completed", "Cancelled"]:
            QMessageBox.warning(self, "Task Complete", "Cannot start a timer on a completed or cancelled task.")
            return

        if self.controller.timer_service.is_running:
            QMessageBox.warning(self, "Timer Running", "An active timer is already running. Stop or pause it first.")
            return

        # Start timer
        self.controller.task_controller.update_task(task["id"], {"status": "In Progress"})
        self.controller.timer_service.start(task["id"], task["uuid"], task["duration"])
        
        QMessageBox.information(self, "Timer Started", f"Timer is now tracking: {task['title']}")
        
        # Switch to Running Task pane
        self.parentWidget().parentWidget().nav_list.setCurrentRow(2)

    def duplicate_selected_task(self):
        """Duplicates selected task properties."""
        task_id = self.get_selected_task_id()
        if task_id < 0:
            QMessageBox.warning(self, "No Selection", "Please select a task from the list to duplicate.")
            return
            
        new_task = self.controller.task_controller.duplicate_task(task_id)
        if new_task:
            QMessageBox.information(self, "Success", f"Task duplicated successfully as: {new_task['task_number']}")
            self.apply_filters()

    def favorite_selected_task(self):
        """Toggles favorite state on selected task."""
        task_id = self.get_selected_task_id()
        if task_id < 0:
            QMessageBox.warning(self, "No Selection", "Please select a task to add to favorites.")
            return
            
        is_fav = self.controller.task_controller.toggle_favorite(task_id)
        self.apply_filters()
        logger.info(f"Toggled favorite on Task {task_id}. New state: {is_fav}")

    def delete_selected_task(self):
        """Deletes selected task log from database."""
        task_id = self.get_selected_task_id()
        if task_id < 0:
            QMessageBox.warning(self, "No Selection", "Please select a task to delete.")
            return

        # Confirm before delete
        reply = QMessageBox.question(
            self, 'Delete Log Confirmation',
            "Are you sure you want to permanently delete this task log? This action is irreversible.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.controller.task_controller.delete_task(task_id)
            if success:
                QMessageBox.information(self, "Deleted", "Task log deleted successfully.")
                self.apply_filters()

    def clear_all_filters(self):
        """Resets all search query text and combo selections."""
        self.search_input.clear()
        self.cmb_date.setCurrentIndex(0)
        self.cmb_project.setCurrentIndex(0)
        self.cmb_category.setCurrentIndex(0)
        self.cmb_assigned_by.setCurrentIndex(0)
        self.cmb_priority.setCurrentIndex(0)
        self.cmb_status.setCurrentIndex(0)
        self.apply_filters()
