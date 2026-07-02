from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
    QComboBox, QDoubleSpinBox, QCheckBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QFileDialog, QScrollArea
)
from PySide6.QtCore import Slot, Qt
from app.utils.logger import logger

class SettingsView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        heading = QLabel("Application Settings", self)
        heading.setObjectName("SectionHeading")
        main_layout.addWidget(heading)
        
        # Scroll area for configurations
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 10, 0)
        
        # 1. THEME & TARGET HOURS CARD
        card_theme = QFrame(container)
        card_theme.setProperty("class", "Card")
        theme_layout = QVBoxLayout(card_theme)
        theme_layout.addWidget(QLabel("Preferences", card_theme))
        
        # Theme dropdown
        row_theme = QHBoxLayout()
        row_theme.addWidget(QLabel("App Theme:", card_theme))
        self.cmb_theme = QComboBox(card_theme)
        self.cmb_theme.addItems(["Dark Mode", "Light Mode"])
        self.cmb_theme.currentTextChanged.connect(self._on_theme_changed)
        row_theme.addWidget(self.cmb_theme)
        theme_layout.addLayout(row_theme)
        
        # Working Hours spinbox
        row_hours = QHBoxLayout()
        row_hours.addWidget(QLabel("Daily Target Working Hours:", card_theme))
        self.spin_hours = QDoubleSpinBox(card_theme)
        self.spin_hours.setRange(1.0, 24.0)
        self.spin_hours.setSingleStep(0.5)
        row_hours.addWidget(self.spin_hours)
        theme_layout.addLayout(row_hours)
        
        layout.addWidget(card_theme)
        
        # 2. DROP-DOWN CHOICES CARD (Priorities / Statuses)
        card_lists = QFrame(container)
        card_lists.setProperty("class", "Card")
        lists_layout = QVBoxLayout(card_lists)
        lists_layout.addWidget(QLabel("Custom List Fields (Comma-Separated)", card_lists))
        
        lists_layout.addWidget(QLabel("Task Priorities:", card_lists))
        self.txt_priorities = QLineEdit(card_lists)
        lists_layout.addWidget(self.txt_priorities)
        
        lists_layout.addWidget(QLabel("Task Statuses:", card_lists))
        self.txt_statuses = QLineEdit(card_lists)
        lists_layout.addWidget(self.txt_statuses)
        
        layout.addWidget(card_lists)
        
        # 3. NOTIFICATIONS CARD
        card_notif = QFrame(container)
        card_notif.setProperty("class", "Card")
        notif_layout = QVBoxLayout(card_notif)
        notif_layout.addWidget(QLabel("Desktop Notification Triggers", card_notif))
        
        self.chk_task_warn = QCheckBox("Remind me when an active task runs for more than 2 hours", card_notif)
        notif_layout.addWidget(self.chk_task_warn)
        
        self.chk_break_warn = QCheckBox("Remind me to take a break every 90 minutes", card_notif)
        notif_layout.addWidget(self.chk_break_warn)
        
        self.chk_eod_warn = QCheckBox("Alert me to log my hours near End of Day (EOD)", card_notif)
        notif_layout.addWidget(self.chk_eod_warn)
        
        self.chk_incomplete_warn = QCheckBox("Show a summary of incomplete tasks in the morning", card_notif)
        notif_layout.addWidget(self.chk_incomplete_warn)
        
        layout.addWidget(card_notif)
        
        # 4. DATABASE UTILITIES CARD
        card_db = QFrame(container)
        card_db.setProperty("class", "Card")
        db_layout = QVBoxLayout(card_db)
        db_layout.addWidget(QLabel("Database Backup & Restoration", card_db))
        
        db_buttons = QHBoxLayout()
        self.btn_backup = QPushButton("Backup SQLite Database", card_db)
        self.btn_backup.clicked.connect(self.backup_database)
        db_buttons.addWidget(self.btn_backup)
        
        self.btn_restore = QPushButton("Restore Database from File", card_db)
        self.btn_restore.clicked.connect(self.restore_database)
        db_buttons.addWidget(self.btn_restore)
        db_layout.addLayout(db_buttons)
        
        layout.addWidget(card_db)
        
        # 5. GLOBAL SAVE BUTTON
        self.btn_save = QPushButton("Save Configurations", container)
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_save)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def load_settings(self):
        """Pulls settings values from JSON config file."""
        theme = self.controller.settings_controller.get_config_setting("theme", "dark")
        self.cmb_theme.setCurrentText("Dark Mode" if theme == "dark" else "Light Mode")
        
        hours = self.controller.settings_controller.get_config_setting("working_hours", 8.0)
        self.spin_hours.setValue(hours)
        
        pri = self.controller.settings_controller.get_config_setting("priorities", [])
        self.txt_priorities.setText(", ".join(pri))
        
        stat = self.controller.settings_controller.get_config_setting("statuses", [])
        self.txt_statuses.setText(", ".join(stat))
        
        notif = self.controller.settings_controller.get_config_setting("notifications", {})
        self.chk_task_warn.setChecked(notif.get("task_duration_warning", True))
        self.chk_break_warn.setChecked(notif.get("break_reminder", True))
        self.chk_eod_warn.setChecked(notif.get("eod_reminder", True))
        self.chk_incomplete_warn.setChecked(notif.get("incomplete_task_reminder", True))

    def save_settings(self):
        """Saves current fields to config manager."""
        theme_val = "dark" if self.cmb_theme.currentText() == "Dark Mode" else "light"
        
        # Parse comma-separated list
        pri_list = [p.strip() for p in self.txt_priorities.text().split(",") if p.strip()]
        stat_list = [s.strip() for s in self.txt_statuses.text().split(",") if s.strip()]
        
        if not pri_list or not stat_list:
            QMessageBox.warning(self, "Invalid Lists", "Priorities and Statuses lists cannot be empty.")
            return

        notif_dict = {
            "task_duration_warning": self.chk_task_warn.isChecked(),
            "task_warning_hours": 2,
            "break_reminder": self.chk_break_warn.isChecked(),
            "break_interval_minutes": 90,
            "eod_reminder": self.chk_eod_warn.isChecked(),
            "incomplete_task_reminder": self.chk_incomplete_warn.isChecked(),
            "eod_time": "17:30"
        }
        
        # Save setting keys
        self.controller.settings_controller.update_config_setting("working_hours", self.spin_hours.value())
        self.controller.settings_controller.update_config_setting("priorities", pri_list)
        self.controller.settings_controller.update_config_setting("statuses", stat_list)
        self.controller.settings_controller.update_config_setting("notifications", notif_dict)
        
        # Trigger theme switch (if changed)
        self.controller.change_theme(theme_val)
        
        QMessageBox.information(self, "Settings Saved", "Configuration settings saved successfully.")

    def _on_theme_changed(self, text):
        theme_val = "dark" if text == "Dark Mode" else "light"
        if theme_val != self.controller.get_current_theme():
            self.controller.change_theme(theme_val)

    def backup_database(self):
        """Prompts dialog to backup database."""
        dest_dir = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if dest_dir:
            filepath = self.controller.settings_controller.backup_database(dest_dir)
            if filepath:
                QMessageBox.information(self, "Backup Successful", f"Database backed up successfully to:\n{filepath}")
            else:
                QMessageBox.critical(self, "Backup Error", "Could not complete database backup.")

    def restore_database(self):
        """Prompts dialog to select restore file and executes."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Backup File to Restore", "", "Database Files (*.db *.db.bak)")
        if filepath:
            # Warn user
            reply = QMessageBox.warning(
                self, 'Restore Confirmation',
                "Restoring a database will overwrite the current tracking database and all current active logs.\n\nAre you sure you want to proceed?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.controller.settings_controller.restore_database(filepath)
                if success:
                    QMessageBox.information(self, "Restore Successful", "Database restored successfully. The application will refresh lists.")
                    # Refresh the active view
                    main_win = self.parentWidget().parentWidget()
                    main_win.navigate_to_pane(0) # Nav to dashboard
                else:
                    QMessageBox.critical(self, "Restore Error", "Failed to restore database from backup file.")


# ==========================================
# PROJECTS CRUD MANAGEMENT VIEW
# ==========================================

class ProjectsView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_project_id = None
        
        self.setup_ui()
        self.refresh_projects()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        heading = QLabel("Project Management", self)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)
        
        split_layout = QHBoxLayout()
        split_layout.setSpacing(15)
        
        # 1. Projects Table (Left)
        self.table_card = QFrame(self)
        self.table_card.setProperty("class", "Card")
        tc_layout = QVBoxLayout(self.table_card)
        
        self.table = QTableWidget(self.table_card)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Project Name", "Description", "Active"])
        self.table.hideColumn(0)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        tc_layout.addWidget(self.table)
        
        split_layout.addWidget(self.table_card, stretch=3)
        
        # 2. Project Edit Form (Right)
        self.form_card = QFrame(self)
        self.form_card.setProperty("class", "Card")
        self.form_card.setMinimumWidth(300)
        self.form_card.setMaximumWidth(400)
        fc_layout = QVBoxLayout(self.form_card)
        fc_layout.setSpacing(10)
        
        fc_layout.addWidget(QLabel("Project Details", self.form_card))
        
        fc_layout.addWidget(QLabel("Project Name *", self.form_card))
        self.txt_name = QLineEdit(self.form_card)
        fc_layout.addWidget(self.txt_name)
        
        fc_layout.addWidget(QLabel("Description", self.form_card))
        self.txt_desc = QTextEdit(self.form_card)
        self.txt_desc.setMaximumHeight(100)
        fc_layout.addWidget(self.txt_desc)
        
        self.chk_active = QCheckBox("Project Active", self.form_card)
        self.chk_active.setChecked(True)
        fc_layout.addWidget(self.chk_active)
        
        # CRUD Actions Buttons
        self.btn_add = QPushButton("Add Project", self.form_card)
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_add.clicked.connect(self.add_project)
        fc_layout.addWidget(self.btn_add)
        
        self.btn_update = QPushButton("Update Project", self.form_card)
        self.btn_update.setObjectName("SuccessButton")
        self.btn_update.clicked.connect(self.update_project)
        fc_layout.addWidget(self.btn_update)
        
        self.btn_delete = QPushButton("Delete Project", self.form_card)
        self.btn_delete.setObjectName("DangerButton")
        self.btn_delete.clicked.connect(self.delete_project)
        fc_layout.addWidget(self.btn_delete)
        
        self.btn_clear = QPushButton("Clear Fields", self.form_card)
        self.btn_clear.clicked.connect(self.clear_fields)
        fc_layout.addWidget(self.btn_clear)
        
        fc_layout.addStretch()
        split_layout.addWidget(self.form_card, stretch=1)
        
        layout.addLayout(split_layout)

    def refresh_projects(self):
        """Pulls projects from database and refreshes table."""
        projects = self.controller.settings_controller.get_all_projects(include_archived=True)
        self.table.setRowCount(0)
        for i, p in enumerate(projects):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(p["project_name"]))
            self.table.setItem(i, 2, QTableWidgetItem(p["description"]))
            
            act_text = "Yes" if p["active"] else "Archived"
            self.table.setItem(i, 3, QTableWidgetItem(act_text))
            
        self.clear_fields()

    def clear_fields(self):
        self.selected_project_id = None
        self.txt_name.clear()
        self.txt_desc.clear()
        self.chk_active.setChecked(True)
        self.btn_add.setEnabled(True)
        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.table.clearSelection()

    def on_row_selected(self):
        """Populates form fields with selected project rows."""
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return
        row = selected_ranges[0].topRow()
        
        self.selected_project_id = int(self.table.item(row, 0).text())
        self.txt_name.setText(self.table.item(row, 1).text())
        self.txt_desc.setText(self.table.item(row, 2).text())
        
        act_val = self.table.item(row, 3).text() == "Yes"
        self.chk_active.setChecked(act_val)
        
        self.btn_add.setEnabled(False)
        self.btn_update.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def add_project(self):
        name = self.txt_name.text().strip()
        desc = self.txt_desc.toPlainText().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Project name is required.")
            return
            
        success = self.controller.settings_controller.add_project(name, desc)
        if success:
            QMessageBox.information(self, "Success", f"Project '{name}' added successfully.")
            self.refresh_projects()
        else:
            QMessageBox.critical(self, "Error", "Could not add project (might be duplicate name).")

    def update_project(self):
        if not self.selected_project_id:
            return
        name = self.txt_name.text().strip()
        desc = self.txt_desc.toPlainText().strip()
        active = self.chk_active.isChecked()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Project name is required.")
            return
            
        success = self.controller.settings_controller.update_project(self.selected_project_id, name, desc, active)
        if success:
            QMessageBox.information(self, "Success", "Project updated successfully.")
            self.refresh_projects()
        else:
            QMessageBox.critical(self, "Error", "Could not update project (might be duplicate name).")

    def delete_project(self):
        if not self.selected_project_id:
            return
            
        # Confirm delete
        reply = QMessageBox.question(
            self, 'Delete Project Confirmation',
            "Are you sure you want to delete this project? This will fail if the project has tasks logged against it.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.controller.settings_controller.delete_project(self.selected_project_id)
            if success:
                QMessageBox.information(self, "Deleted", "Project deleted successfully.")
                self.refresh_projects()
            else:
                QMessageBox.critical(
                    self, "Deletion Failed", 
                    "Could not delete project. Active projects containing logged tasks cannot be deleted. Consider archiving it instead."
                )


# ==========================================
# CATEGORIES CRUD MANAGEMENT VIEW
# ==========================================

class CategoriesView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_category_id = None
        
        self.setup_ui()
        self.refresh_categories()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        heading = QLabel("Category Management", self)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)
        
        split_layout = QHBoxLayout()
        split_layout.setSpacing(15)
        
        # 1. Categories Table
        self.table_card = QFrame(self)
        self.table_card.setProperty("class", "Card")
        tc_layout = QVBoxLayout(self.table_card)
        
        self.table = QTableWidget(self.table_card)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Category Name"])
        self.table.hideColumn(0)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        tc_layout.addWidget(self.table)
        
        split_layout.addWidget(self.table_card, stretch=3)
        
        # 2. Form Right
        self.form_card = QFrame(self)
        self.form_card.setProperty("class", "Card")
        self.form_card.setMaximumWidth(350)
        fc_layout = QVBoxLayout(self.form_card)
        fc_layout.setSpacing(10)
        
        fc_layout.addWidget(QLabel("Category Details", self.form_card))
        fc_layout.addWidget(QLabel("Category Name *", self.form_card))
        self.txt_name = QLineEdit(self.form_card)
        fc_layout.addWidget(self.txt_name)
        
        self.btn_add = QPushButton("Add Category", self.form_card)
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_add.clicked.connect(self.add_category)
        fc_layout.addWidget(self.btn_add)
        
        self.btn_delete = QPushButton("Delete Category", self.form_card)
        self.btn_delete.setObjectName("DangerButton")
        self.btn_delete.clicked.connect(self.delete_category)
        fc_layout.addWidget(self.btn_delete)
        
        self.btn_clear = QPushButton("Clear Fields", self.form_card)
        self.btn_clear.clicked.connect(self.clear_fields)
        fc_layout.addWidget(self.btn_clear)
        
        fc_layout.addStretch()
        split_layout.addWidget(self.form_card, stretch=1)
        
        layout.addLayout(split_layout)

    def refresh_categories(self):
        cats = self.controller.settings_controller.get_all_categories()
        self.table.setRowCount(0)
        for i, c in enumerate(cats):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(c["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(c["category_name"]))
            
        self.clear_fields()

    def clear_fields(self):
        self.selected_category_id = None
        self.txt_name.clear()
        self.btn_add.setEnabled(True)
        self.btn_delete.setEnabled(False)
        self.table.clearSelection()

    def on_row_selected(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return
        row = selected_ranges[0].topRow()
        
        self.selected_category_id = int(self.table.item(row, 0).text())
        self.txt_name.setText(self.table.item(row, 1).text())
        self.btn_add.setEnabled(False)
        self.btn_delete.setEnabled(True)

    def add_category(self):
        name = self.txt_name.text().strip()
        if not name:
            return
            
        success = self.controller.settings_controller.add_category(name)
        if success:
            QMessageBox.information(self, "Success", f"Category '{name}' added successfully.")
            self.refresh_categories()
        else:
            QMessageBox.critical(self, "Error", "Could not add category (duplicate name).")

    def delete_category(self):
        if not self.selected_category_id:
            return
            
        reply = QMessageBox.question(
            self, 'Delete Category',
            "Are you sure you want to delete this category? It will fail if referenced in tasks.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.controller.settings_controller.delete_category(self.selected_category_id)
            if success:
                QMessageBox.information(self, "Deleted", "Category deleted successfully.")
                self.refresh_categories()
            else:
                QMessageBox.critical(self, "Failed", "Could not delete category. Ensure it is not assigned to any tasks.")


# ==========================================
# ASSIGNED BY CRUD MANAGEMENT VIEW
# ==========================================

class AssignedByView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_ab_id = None
        
        self.setup_ui()
        self.refresh_assigned_by()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        heading = QLabel("Assignee Profiles Management", self)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)
        
        split_layout = QHBoxLayout()
        split_layout.setSpacing(15)
        
        # 1. Table
        self.table_card = QFrame(self)
        self.table_card.setProperty("class", "Card")
        tc_layout = QVBoxLayout(self.table_card)
        
        self.table = QTableWidget(self.table_card)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Designation"])
        self.table.hideColumn(0)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        tc_layout.addWidget(self.table)
        
        split_layout.addWidget(self.table_card, stretch=3)
        
        # 2. Form
        self.form_card = QFrame(self)
        self.form_card.setProperty("class", "Card")
        self.form_card.setMaximumWidth(350)
        fc_layout = QVBoxLayout(self.form_card)
        fc_layout.setSpacing(10)
        
        fc_layout.addWidget(QLabel("Assignee Profile Details", self.form_card))
        
        fc_layout.addWidget(QLabel("Name *", self.form_card))
        self.txt_name = QLineEdit(self.form_card)
        fc_layout.addWidget(self.txt_name)
        
        fc_layout.addWidget(QLabel("Designation", self.form_card))
        self.txt_desg = QLineEdit(self.form_card)
        fc_layout.addWidget(self.txt_desg)
        
        self.btn_add = QPushButton("Add Assignee", self.form_card)
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_add.clicked.connect(self.add_assignee)
        fc_layout.addWidget(self.btn_add)
        
        self.btn_delete = QPushButton("Delete Assignee", self.form_card)
        self.btn_delete.setObjectName("DangerButton")
        self.btn_delete.clicked.connect(self.delete_assignee)
        fc_layout.addWidget(self.btn_delete)
        
        self.btn_clear = QPushButton("Clear Fields", self.form_card)
        self.btn_clear.clicked.connect(self.clear_fields)
        fc_layout.addWidget(self.btn_clear)
        
        fc_layout.addStretch()
        split_layout.addWidget(self.form_card, stretch=1)
        
        layout.addLayout(split_layout)

    def refresh_assigned_by(self):
        entries = self.controller.settings_controller.get_all_assigned_by()
        self.table.setRowCount(0)
        for i, a in enumerate(entries):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(a["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(a["person_name"]))
            self.table.setItem(i, 2, QTableWidgetItem(a["designation"]))
            
        self.clear_fields()

    def clear_fields(self):
        self.selected_ab_id = None
        self.txt_name.clear()
        self.txt_desg.clear()
        self.btn_add.setEnabled(True)
        self.btn_delete.setEnabled(False)
        self.table.clearSelection()

    def on_row_selected(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return
        row = selected_ranges[0].topRow()
        
        self.selected_ab_id = int(self.table.item(row, 0).text())
        self.txt_name.setText(self.table.item(row, 1).text())
        self.txt_desg.setText(self.table.item(row, 2).text())
        self.btn_add.setEnabled(False)
        self.btn_delete.setEnabled(True)

    def add_assignee(self):
        name = self.txt_name.text().strip()
        desg = self.txt_desg.text().strip()
        if not name:
            return
            
        success = self.controller.settings_controller.add_assigned_by(name, desg)
        if success:
            QMessageBox.information(self, "Success", f"Assignee '{name}' added successfully.")
            self.refresh_assigned_by()
        else:
            QMessageBox.critical(self, "Error", "Could not add assignee profile (duplicate name/desg).")

    def delete_assignee(self):
        if not self.selected_ab_id:
            return
            
        reply = QMessageBox.question(
            self, 'Delete Assignee',
            "Are you sure you want to delete this assignee profile? It will fail if referenced in tasks.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.controller.settings_controller.delete_assigned_by(self.selected_ab_id)
            if success:
                QMessageBox.information(self, "Deleted", "Assignee profile deleted successfully.")
                self.refresh_assigned_by()
            else:
                QMessageBox.critical(self, "Failed", "Could not delete assignee. Check that they are not referenced in tasks.")
