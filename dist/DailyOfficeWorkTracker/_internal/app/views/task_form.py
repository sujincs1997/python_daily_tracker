import uuid
from datetime import datetime
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
    QComboBox, QDoubleSpinBox, QSlider, QPushButton, QFrame, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Slot

from app.utils.logger import logger

class TaskFormView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.editing_task_id = None
        
        self.setup_ui()
        
        # Listen to active ticks and timer status changes
        self.controller.timer_service.tick.connect(self.update_form_timer_display)
        self.controller.timer_service.status_changed.connect(self.update_form_timer_buttons)
        
        self.prepare_new_task()

    def setup_ui(self):
        """Builds the scrolling form layout for creating/editing tasks."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Heading
        self.lbl_heading = QLabel("Create New Task", self)
        self.lbl_heading.setObjectName("SectionHeading")
        main_layout.addWidget(heading) if 'heading' in locals() else main_layout.addWidget(self.lbl_heading)
        
        # Scroll Area for Form
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        form_container = QWidget()
        form_container.setStyleSheet("background-color: transparent;")
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(0, 0, 10, 0)
        
        # 1. AUTO GENERATED FIELDS CARD
        self.card_auto = QFrame(form_container)
        self.card_auto.setProperty("class", "Card")
        auto_layout = QHBoxLayout(self.card_auto)
        
        # UUID Display
        self.lbl_uuid = QLabel("UUID: Auto-generated", self.card_auto)
        self.lbl_uuid.setStyleSheet("font-family: monospace; font-size: 11px;")
        auto_layout.addWidget(self.lbl_uuid)
        
        # Task Number Display
        self.lbl_task_num = QLabel("Task #:", self.card_auto)
        self.lbl_task_num.setStyleSheet("font-weight: bold;")
        auto_layout.addWidget(self.lbl_task_num)
        
        # Created Date Display
        self.lbl_created_date = QLabel("Date: " + datetime.now().strftime("%Y-%m-%d"), self.card_auto)
        auto_layout.addWidget(self.lbl_created_date)
        
        # Form running clock
        self.lbl_form_clock = QLabel("00:00:00", self.card_auto)
        self.lbl_form_clock.setStyleSheet("font-size: 18px; font-family: monospace; font-weight: bold; color: #7aa2f7; margin-left: 20px;")
        auto_layout.addWidget(self.lbl_form_clock)
        
        form_layout.addWidget(self.card_auto)

        # 2. TASK INFORMATION CARD
        card_info = QFrame(form_container)
        card_info.setProperty("class", "Card")
        info_layout = QVBoxLayout(card_info)
        info_layout.setSpacing(10)

        # Title/Task Name
        info_layout.addWidget(QLabel("Task Title *", card_info))
        self.txt_title = QLineEdit(card_info)
        self.txt_title.setPlaceholderText("Enter a descriptive title for this task...")
        info_layout.addWidget(self.txt_title)

        # Description
        info_layout.addWidget(QLabel("Description", card_info))
        self.txt_desc = QTextEdit(card_info)
        self.txt_desc.setPlaceholderText("Provide details about what needs to be done...")
        self.txt_desc.setMaximumHeight(80)
        info_layout.addWidget(self.txt_desc)

        # Category & Project & Assigned By Dropdowns (Horizontal Layout)
        dropdowns_layout = QHBoxLayout()
        dropdowns_layout.setSpacing(15)

        # Category
        cat_box = QVBoxLayout()
        cat_box.addWidget(QLabel("Category *", card_info))
        self.cmb_category = QComboBox(card_info)
        cat_box.addWidget(self.cmb_category)
        dropdowns_layout.addLayout(cat_box)

        # Project
        proj_box = QVBoxLayout()
        proj_box.addWidget(QLabel("Project *", card_info))
        self.cmb_project = QComboBox(card_info)
        proj_box.addWidget(self.cmb_project)
        dropdowns_layout.addLayout(proj_box)

        # Assigned By
        ab_box = QVBoxLayout()
        ab_box.addWidget(QLabel("Assigned By *", card_info))
        self.cmb_assigned_by = QComboBox(card_info)
        ab_box.addWidget(self.cmb_assigned_by)
        dropdowns_layout.addLayout(ab_box)

        info_layout.addLayout(dropdowns_layout)
        
        # Priority & Status & Estimated Hours (Horizontal)
        more_dropdowns = QHBoxLayout()
        more_dropdowns.setSpacing(15)
        
        # Priority
        pri_box = QVBoxLayout()
        pri_box.addWidget(QLabel("Priority", card_info))
        self.cmb_priority = QComboBox(card_info)
        more_dropdowns.addLayout(pri_box)
        
        # Status
        stat_box = QVBoxLayout()
        stat_box.addWidget(QLabel("Status", card_info))
        self.cmb_status = QComboBox(card_info)
        more_dropdowns.addLayout(stat_box)
        
        # Est Hours
        est_box = QVBoxLayout()
        est_box.addWidget(QLabel("Estimated Hours", card_info))
        self.spin_est = QDoubleSpinBox(card_info)
        self.spin_est.setRange(0, 999.0)
        self.spin_est.setSingleStep(0.5)
        est_box.addWidget(self.spin_est)
        more_dropdowns.addLayout(est_box)
        
        info_layout.addLayout(more_dropdowns)
        
        # Completion slider
        comp_box = QHBoxLayout()
        comp_box.addWidget(QLabel("Completion %", card_info))
        self.slider_comp = QSlider(Qt.Horizontal, card_info)
        self.slider_comp.setRange(0, 10) # 0%, 10%, 20%, ..., 100%
        self.slider_comp.setTickInterval(1)
        self.slider_comp.setTickPosition(QSlider.TicksBelow)
        self.lbl_comp_percent = QLabel("0%", card_info)
        self.lbl_comp_percent.setMinimumWidth(35)
        self.slider_comp.valueChanged.connect(self._on_slider_changed)
        comp_box.addWidget(self.slider_comp)
        comp_box.addWidget(self.lbl_comp_percent)
        info_layout.addLayout(comp_box)
        
        # Remarks
        info_layout.addWidget(QLabel("Remarks", card_info))
        self.txt_remarks = QTextEdit(card_info)
        self.txt_remarks.setPlaceholderText("Enter notes, obstacles, or completion remarks...")
        self.txt_remarks.setMaximumHeight(80)
        info_layout.addWidget(self.txt_remarks)
        
        form_layout.addWidget(card_info)

        # 3. ACTION BUTTONS ROW
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.btn_save = QPushButton("Save Task (Ctrl+S)", form_container)
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.clicked.connect(self.save_task)
        buttons_layout.addWidget(self.btn_save)
        
        self.btn_pause = QPushButton("Pause Timer", form_container)
        self.btn_pause.clicked.connect(self.pause_form_timer)
        buttons_layout.addWidget(self.btn_pause)
        
        self.btn_resume = QPushButton("Resume Timer", form_container)
        self.btn_resume.setObjectName("SuccessButton")
        self.btn_resume.clicked.connect(self.resume_form_timer)
        buttons_layout.addWidget(self.btn_resume)
        
        self.btn_stop = QPushButton("Stop & Save", form_container)
        self.btn_stop.setObjectName("DangerButton")
        self.btn_stop.clicked.connect(self.stop_form_timer)
        buttons_layout.addWidget(self.btn_stop)
        
        self.btn_cancel = QPushButton("Discard Task", form_container)
        self.btn_cancel.clicked.connect(self.discard_task)
        buttons_layout.addWidget(self.btn_cancel)
        
        form_layout.addLayout(buttons_layout)
        
        scroll.setWidget(form_container)
        main_layout.addWidget(scroll)

    def _on_slider_changed(self, val):
        self.lbl_comp_percent.setText(f"{val * 10}%")

    def populate_combos(self):
        """Fetches drop-down items from settings controllers."""
        # 1. Categories
        self.cmb_category.clear()
        self.cmb_category.addItem("- Select Category -", None)
        for cat in self.controller.settings_controller.get_all_categories():
            self.cmb_category.addItem(cat["category_name"], cat["id"])
            
        # 2. Projects
        self.cmb_project.clear()
        self.cmb_project.addItem("- Select Project -", None)
        for proj in self.controller.settings_controller.get_all_projects(include_archived=False):
            self.cmb_project.addItem(proj["project_name"], proj["id"])
            
        # 3. Assigned By
        self.cmb_assigned_by.clear()
        self.cmb_assigned_by.addItem("- Select Assignee -", None)
        for ab in self.controller.settings_controller.get_all_assigned_by():
            self.cmb_assigned_by.addItem(ab["person_name"], ab["id"])
            
        # 4. Priority
        self.cmb_priority.clear()
        for p in self.controller.settings_controller.get_config_setting("priorities", []):
            self.cmb_priority.addItem(p)
            
        # 5. Status
        self.cmb_status.clear()
        for s in self.controller.settings_controller.get_config_setting("statuses", []):
            self.cmb_status.addItem(s)

    def prepare_new_task(self):
        """Prepares a new task, starting the timer immediately if no active timer is running."""
        # 1. Check if a timer is running
        if self.controller.timer_service.is_running:
            active_uuid = self.controller.timer_service.current_task_uuid
            active_task = self.controller.task_controller.get_task_by_uuid(active_uuid)
            active_title = active_task["title"] if active_task else "Running Task"
            
            reply = QMessageBox.question(
                self, "Timer Running",
                f"A timer is already running for task:\n'{active_title}'\n\nWould you like to stop it and start a new task?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.controller.auto_save_active_task()
                self.controller.timer_service.stop()
            else:
                # Load the currently running task to edit it
                if active_task:
                    self.load_task_to_edit(active_task["id"])
                return

        # 2. Get defaults from DB
        projects = self.controller.settings_controller.get_all_projects(include_archived=False)
        categories = self.controller.settings_controller.get_all_categories()
        assignees = self.controller.settings_controller.get_all_assigned_by()
        
        if not projects or not categories or not assignees:
            QMessageBox.critical(
                self, "Configuration Required",
                "Please configure at least one active Project, Category, and Assigned By profile in Settings before starting a task."
            )
            # Redirect to Settings
            main_win = self.parentWidget().parentWidget()
            main_win.nav_list.setCurrentRow(10) # Settings index
            return

        # Create task immediately in DB
        next_num = self.controller.task_controller.get_next_task_number()
        default_title = f"Tracking Task {next_num}"
        
        task_data = {
            "uuid": str(uuid.uuid4()),
            "task_number": next_num,
            "title": default_title,
            "description": "",
            "category_id": categories[0]["id"],
            "project_id": projects[0]["id"],
            "assigned_by_id": assignees[0]["id"],
            "priority": "Medium",
            "status": "In Progress",
            "completion": 0,
            "duration": 0,
            "remarks": ""
        }
        
        new_task = self.controller.task_controller.create_task(task_data)
        if new_task:
            self.editing_task_id = new_task["id"]
            # Start timer
            self.controller.timer_service.start(new_task["id"], new_task["uuid"], 0)
            # Load task details into fields
            self.load_task_to_edit(new_task["id"])

    def load_task_to_edit(self, task_id: int):
        """Fills form fields with existing task details to perform edits."""
        task = self.controller.task_controller.get_task_by_id(task_id)
        if not task:
            QMessageBox.critical(self, "Error", "Task details could not be retrieved.")
            return
            
        self.editing_task_id = task_id
        self.lbl_heading.setText(f"Edit Task: {task['task_number']}")
        
        self.populate_combos()
        
        self.lbl_uuid.setText(f"UUID: {task['uuid']}")
        self.lbl_task_num.setText(f"Task #: {task['task_number']}")
        self.lbl_created_date.setText(f"Created: {task['created_date']} {task['created_time']}")
        
        self.txt_title.setText(task["title"])
        self.txt_desc.setText(task["description"])
        
        # Select Combos (with fallback in case project/category is archived or deleted)
        idx_cat = self.cmb_category.findData(task["category_id"])
        self.cmb_category.setCurrentIndex(idx_cat if idx_cat >= 0 else 0)
        
        idx_proj = self.cmb_project.findData(task["project_id"])
        self.cmb_project.setCurrentIndex(idx_proj if idx_proj >= 0 else 0)
        
        idx_ab = self.cmb_assigned_by.findData(task["assigned_by_id"])
        self.cmb_assigned_by.setCurrentIndex(idx_ab if idx_ab >= 0 else 0)
        
        self.cmb_priority.setCurrentText(task["priority"])
        self.cmb_status.setCurrentText(task["status"])
        self.slider_comp.setValue(task["completion"] // 10)
        self.txt_remarks.setText(task["remarks"])
        
        self.update_form_timer_buttons()

    def validate_inputs(self) -> bool:
        """Checks for mandatory task creation fields."""
        if not self.txt_title.text().strip():
            QMessageBox.warning(self, "Validation Error", "Task Title is a required field.")
            return False
            
        if self.cmb_category.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select a Category.")
            return False
            
        if self.cmb_project.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select a Project.")
            return False
            
        if self.cmb_assigned_by.currentData() is None:
            QMessageBox.warning(self, "Validation Error", "Please select an Assignee.")
            return False
            
        return True

    def save_task(self) -> Optional[dict]:
        """Saves or updates task in database."""
        if not self.validate_inputs():
            return None
            
        task_data = {
            "title": self.txt_title.text().strip(),
            "description": self.txt_desc.toPlainText().strip(),
            "category_id": self.cmb_category.currentData(),
            "project_id": self.cmb_project.currentData(),
            "assigned_by_id": self.cmb_assigned_by.currentData(),
            "priority": self.cmb_priority.currentText(),
            "status": self.cmb_status.currentText(),
            "completion": self.slider_comp.value() * 10,
            "remarks": self.txt_remarks.toPlainText().strip()
        }
        
        if self.editing_task_id:
            success = self.controller.task_controller.update_task(self.editing_task_id, task_data)
            if success:
                QMessageBox.information(self, "Success", "Task updated successfully.")
                # Reload window
                self.load_task_to_edit(self.editing_task_id)
                return self.controller.task_controller.get_task_by_id(self.editing_task_id)
        else:
            # Generate UUID/Num
            task_data["uuid"] = self.lbl_uuid.text().replace("UUID: ", "")
            task_data["task_number"] = self.lbl_task_num.text().replace("Task #: ", "")
            
            new_task = self.controller.task_controller.create_task(task_data)
            if new_task:
                QMessageBox.information(self, "Success", "Task created successfully.")
                self.editing_task_id = new_task["id"]
                self.lbl_heading.setText(f"Edit Task: {new_task['task_number']}")
                return new_task
                
        return None

    @Slot(str, int)
    def update_form_timer_display(self, formatted_time: str, elapsed_seconds: int):
        """Updates the clock label inside the form if this task is the running task."""
        if self.editing_task_id and self.controller.timer_service.current_task_id == self.editing_task_id:
            self.lbl_form_clock.setText(formatted_time)

    def update_form_timer_buttons(self):
        """Updates the state of timer control buttons on the form."""
        is_running = self.controller.timer_service.is_running
        active_task_id = self.controller.timer_service.current_task_id
        
        # If this task is the active task
        is_this_active = (self.editing_task_id and active_task_id == self.editing_task_id)
        
        if is_this_active and is_running:
            is_paused = self.controller.timer_service.is_paused
            self.btn_pause.setEnabled(not is_paused)
            self.btn_resume.setEnabled(is_paused)
            self.btn_stop.setEnabled(True)
            self.lbl_form_clock.setVisible(True)
        else:
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.lbl_form_clock.setVisible(False)
            
    def pause_form_timer(self):
        self.controller.timer_service.pause()
        self.update_form_timer_buttons()
        
    def resume_form_timer(self):
        self.controller.timer_service.resume()
        self.update_form_timer_buttons()
        
    def stop_form_timer(self):
        """Stops the timer, prompts for final status, and saves."""
        live_remarks = self.txt_remarks.toPlainText().strip()
        live_comp = self.slider_comp.value() * 10
        
        stats = self.controller.timer_service.stop()
        if not stats:
            return
            
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Timer Stopped")
        msg_box.setText(f"Timer stopped for task.\nTotal Duration: {stats['hours']} hrs, {stats['minutes']} mins.\n\nSet final task status:")
        btn_completed = msg_box.addButton("Completed", QMessageBox.YesRole)
        btn_paused = msg_box.addButton("Paused", QMessageBox.NoRole)
        btn_cancel = msg_box.addButton("Cancelled", QMessageBox.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_completed:
            status_value = "Completed"
            live_comp = 100
        elif msg_box.clickedButton() == btn_paused:
            status_value = "Paused"
        elif msg_box.clickedButton() == btn_cancel:
            status_value = "Cancelled"
            
        self.cmb_status.setCurrentText(status_value)
        self.slider_comp.setValue(live_comp // 10)
        
        # Save task final details
        self.controller.task_controller.update_task(
            task_id=stats["task_id"],
            data={
                "duration": stats["duration"],
                "start_time": stats["start_time"],
                "end_time": stats["end_time"],
                "status": status_value,
                "completion": live_comp,
                "remarks": live_remarks,
                "title": self.txt_title.text().strip(),
                "description": self.txt_desc.toPlainText().strip(),
                "category_id": self.cmb_category.currentData(),
                "project_id": self.cmb_project.currentData(),
                "assigned_by_id": self.cmb_assigned_by.currentData(),
                "priority": self.cmb_priority.currentText()
            }
        )
        
        QMessageBox.information(self, "Task Saved", "Task logs updated and successfully saved in SQLite database.")
        self.update_form_timer_buttons()
        self.parentWidget().parentWidget().nav_list.setCurrentRow(3)
        
    def discard_task(self):
        """Stops the timer and deletes this task log from the database."""
        if not self.editing_task_id:
            return
            
        reply = QMessageBox.question(
            self, "Discard Task Log",
            "Are you sure you want to discard this task log? All time tracked for this session will be permanently deleted.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.controller.timer_service.current_task_id == self.editing_task_id:
                self.controller.timer_service.stop()
            self.controller.task_controller.delete_task(self.editing_task_id)
            QMessageBox.information(self, "Discarded", "Task log discarded and deleted.")
            self.prepare_new_task()


class ActiveTimerWidget(QWidget):
    """The central widget embedded in 'Running Task' to handle starts/stops."""
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        # Connect timer service ticks and status alerts
        self.controller.timer_service.tick.connect(self.update_timer_display)
        self.controller.timer_service.status_changed.connect(self.update_status_display)
        
        self.setup_ui()
        self.refresh_active_timer()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Primary container frame
        self.frame = QFrame(self)
        self.frame.setProperty("class", "Card")
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setSpacing(15)
        
        # Label displaying task details
        self.lbl_task_title = QLabel("No Running Task", self.frame)
        self.lbl_task_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7aa2f7;")
        self.lbl_task_title.setWordWrap(True)
        frame_layout.addWidget(self.lbl_task_title)
        
        self.lbl_task_meta = QLabel("Start a task from New Task or History to monitor here.", self.frame)
        self.lbl_task_meta.setStyleSheet("font-size: 12px; color: #565f89;")
        frame_layout.addWidget(self.lbl_task_meta)
        
        # Giant Timer Readout
        self.lbl_clock = QLabel("00:00:00", self.frame)
        self.lbl_clock.setAlignment(Qt.AlignCenter)
        self.lbl_clock.setStyleSheet("font-size: 48px; font-family: monospace; font-weight: bold; color: #c0caf5; padding: 20px;")
        frame_layout.addWidget(self.lbl_clock)
        
        # Live status label
        self.lbl_status = QLabel("Status: Idle", self.frame)
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 14px; font-weight: 500; color: #565f89;")
        frame_layout.addWidget(self.lbl_status)
        
        # Controls Row
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)
        
        self.btn_pause = QPushButton("Pause", self.frame)
        self.btn_pause.clicked.connect(self.controller.timer_service.pause)
        ctrl_layout.addWidget(self.btn_pause)
        
        self.btn_resume = QPushButton("Resume", self.frame)
        self.btn_resume.clicked.connect(self.controller.timer_service.resume)
        ctrl_layout.addWidget(self.btn_resume)
        
        self.btn_stop = QPushButton("Stop & Save", self.frame)
        self.btn_stop.setObjectName("DangerButton")
        self.btn_stop.clicked.connect(self.stop_and_log_task)
        ctrl_layout.addWidget(self.btn_stop)
        
        frame_layout.addLayout(ctrl_layout)
        
        # Completion slider (useful to update progress during the day)
        comp_box = QHBoxLayout()
        comp_box.addWidget(QLabel("Update Completion:", self.frame))
        self.slider_comp = QSlider(Qt.Horizontal, self.frame)
        self.slider_comp.setRange(0, 10)
        self.slider_comp.setTickInterval(1)
        self.slider_comp.setTickPosition(QSlider.TicksBelow)
        self.lbl_comp_percent = QLabel("0%", self.frame)
        self.lbl_comp_percent.setMinimumWidth(35)
        self.slider_comp.valueChanged.connect(self._on_slider_changed)
        comp_box.addWidget(self.slider_comp)
        comp_box.addWidget(self.lbl_comp_percent)
        frame_layout.addLayout(comp_box)

        # Remarks live update box
        frame_layout.addWidget(QLabel("Live Remarks / Work Log Entries:", self.frame))
        self.txt_remarks = QTextEdit(self.frame)
        self.txt_remarks.setPlaceholderText("Keep track of issues, log outputs, or milestones in real-time...")
        self.txt_remarks.setMaximumHeight(85)
        frame_layout.addWidget(self.txt_remarks)

        layout.addWidget(self.frame)
        
    def _on_slider_changed(self, val):
        self.lbl_comp_percent.setText(f"{val * 10}%")
        # Save completion value live if there's a running task
        active_task_id = self.controller.timer_service.current_task_id
        if active_task_id:
            self.controller.task_controller.update_task(active_task_id, {"completion": val * 10})

    def toggle_timer_state(self):
        """Toggles between Start/Pause when keyboard space bar is pressed."""
        if not self.controller.timer_service.is_running:
            return
            
        if self.controller.timer_service.is_paused:
            self.controller.timer_service.resume()
        else:
            self.controller.timer_service.pause()

    def refresh_active_timer(self):
        """Reloads UI state variables reflecting the active running task."""
        is_running = self.controller.timer_service.is_running
        active_task_uuid = self.controller.timer_service.current_task_uuid
        
        self.btn_pause.setEnabled(is_running and not self.controller.timer_service.is_paused)
        self.btn_resume.setEnabled(is_running and self.controller.timer_service.is_paused)
        self.btn_stop.setEnabled(is_running)
        self.slider_comp.setEnabled(is_running)
        self.txt_remarks.setEnabled(is_running)
        
        if is_running and active_task_uuid:
            task = self.controller.task_controller.get_task_by_uuid(active_task_uuid)
            if task:
                self.lbl_task_title.setText(task["title"])
                self.lbl_task_meta.setText(f"Project: {task['project_name']} | Category: {task['category_name']} | Priority: {task['priority']}")
                self.slider_comp.setValue(task["completion"] // 10)
                self.txt_remarks.setText(task["remarks"])
                
                # Check status
                if self.controller.timer_service.is_paused:
                    self.lbl_status.setText("Status: Paused")
                else:
                    self.lbl_status.setText("Status: Running")
        else:
            self.lbl_task_title.setText("No Active Task Running")
            self.lbl_task_meta.setText("Start a task from New Task or History to monitor here.")
            self.lbl_clock.setText("00:00:00")
            self.lbl_status.setText("Status: Idle")
            self.slider_comp.setValue(0)
            self.txt_remarks.clear()

    @Slot(str, int)
    def update_timer_display(self, formatted_time: str, elapsed_seconds: int):
        """Listens to timer ticks to update clock labels."""
        self.lbl_clock.setText(formatted_time)

    @Slot(str)
    def update_status_display(self, status: str):
        """Listens to status transitions to update button states."""
        self.refresh_active_timer()

    def stop_and_log_task(self):
        """Stops the timer, pulls stats, updates remarks and saves logs to SQLite database."""
        # Pull live remarks and completion values
        live_remarks = self.txt_remarks.toPlainText().strip()
        live_comp = self.slider_comp.value() * 10
        
        # Stop timer
        stats = self.controller.timer_service.stop()
        if not stats:
            return
            
        # Update database with final durations, timestamps, remarks, and complete status
        # If progress is 100%, we set status to Completed, else to whatever fits (or Completed by default on stop)
        status_value = "Completed" if live_comp == 100 else "Paused"
        
        # Ask user what final status they want
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Timer Stopped")
        msg_box.setText(f"Timer stopped for task.\nTotal Duration: {stats['hours']} hrs, {stats['minutes']} mins.\n\nSet final task status:")
        btn_completed = msg_box.addButton("Completed", QMessageBox.YesRole)
        btn_paused = msg_box.addButton("Paused", QMessageBox.NoRole)
        btn_cancel = msg_box.addButton("Cancelled", QMessageBox.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_completed:
            status_value = "Completed"
            live_comp = 100
        elif msg_box.clickedButton() == btn_paused:
            status_value = "Paused"
        elif msg_box.clickedButton() == btn_cancel:
            status_value = "Cancelled"
            
        success = self.controller.task_controller.update_task(
            task_id=stats["task_id"],
            data={
                "duration": stats["duration"],
                "start_time": stats["start_time"],
                "end_time": stats["end_time"],
                "status": status_value,
                "completion": live_comp,
                "remarks": live_remarks
            }
        )
        
        if success:
            QMessageBox.information(self, "Task Saved", "Task logs updated and successfully saved in SQLite database.")
            self.refresh_active_timer()
            # Switch back to history view
            self.parentWidget().parentWidget().nav_list.setCurrentRow(3)
        else:
            QMessageBox.critical(self, "Save Error", "Could not write final task logs to database.")
