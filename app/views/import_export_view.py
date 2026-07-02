from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QMessageBox, QFileDialog, QScrollArea
)
from PySide6.QtCore import Slot, Qt
from app.services.import_export_service import ImportExportService
from app.utils.logger import logger

# ==========================================
# IMPORT VIEW
# ==========================================

class ImportView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        heading = QLabel("Import Configurations & Task Logs", self)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)
        
        # Descriptions
        desc = QLabel(
            "Upload Excel (.xlsx) or CSV files containing configurations or past work logs to populate the database.\n"
            "Ensure sheets contain appropriate column headers before importing.", 
            self
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #565f89; line-height: 1.4;")
        layout.addWidget(desc)
        
        # 1. Projects Import Card
        self.card_proj = QFrame(self)
        self.card_proj.setProperty("class", "Card")
        cp_layout = QHBoxLayout(self.card_proj)
        cp_info = QVBoxLayout()
        cp_info.addWidget(QLabel("Import Projects from Excel", self.card_proj))
        cp_info.addWidget(QLabel("Required Header: 'project_name' (Optional: 'description', 'active')", self.card_proj))
        cp_info.itemAt(1).widget().setStyleSheet("font-size: 11px; color: #565f89;")
        cp_layout.addLayout(cp_info)
        
        btn_import_proj = QPushButton("Choose File...", self.card_proj)
        btn_import_proj.setObjectName("PrimaryButton")
        btn_import_proj.clicked.connect(self.import_projects)
        cp_layout.addWidget(btn_import_proj)
        layout.addWidget(self.card_proj)
        
        # 2. Categories Import Card
        self.card_cat = QFrame(self)
        self.card_cat.setProperty("class", "Card")
        cc_layout = QHBoxLayout(self.card_cat)
        cc_info = QVBoxLayout()
        cc_info.addWidget(QLabel("Import Categories from Excel", self.card_cat))
        cc_info.addWidget(QLabel("Required Header: 'category_name'", self.card_cat))
        cc_info.itemAt(1).widget().setStyleSheet("font-size: 11px; color: #565f89;")
        cc_layout.addLayout(cc_info)
        
        btn_import_cat = QPushButton("Choose File...", self.card_cat)
        btn_import_cat.setObjectName("PrimaryButton")
        btn_import_cat.clicked.connect(self.import_categories)
        cc_layout.addWidget(btn_import_cat)
        layout.addWidget(self.card_cat)
        
        # 3. Assigned By Import Card
        self.card_ab = QFrame(self)
        self.card_ab.setProperty("class", "Card")
        ca_layout = QHBoxLayout(self.card_ab)
        ca_info = QVBoxLayout()
        ca_info.addWidget(QLabel("Import Assignee List from Excel", self.card_ab))
        ca_info.addWidget(QLabel("Required Header: 'person_name' (Optional: 'designation')", self.card_ab))
        ca_info.itemAt(1).widget().setStyleSheet("font-size: 11px; color: #565f89;")
        ca_layout.addLayout(ca_info)
        
        btn_import_ab = QPushButton("Choose File...", self.card_ab)
        btn_import_ab.setObjectName("PrimaryButton")
        btn_import_ab.clicked.connect(self.import_assigned_by)
        ca_layout.addWidget(btn_import_ab)
        layout.addWidget(self.card_ab)
        
        # 4. Tasks Import Card
        self.card_tasks = QFrame(self)
        self.card_tasks.setProperty("class", "Card")
        ct_layout = QHBoxLayout(self.card_tasks)
        ct_info = QVBoxLayout()
        ct_info.addWidget(QLabel("Import Previous Task Logs", self.card_tasks))
        ct_info.addWidget(QLabel("Required Headers: 'title', 'project', 'category', 'assigned_by'", self.card_tasks))
        ct_info.itemAt(1).widget().setStyleSheet("font-size: 11px; color: #565f89;")
        ct_layout.addLayout(ct_info)
        
        btn_import_tasks = QPushButton("Choose File...", self.card_tasks)
        btn_import_tasks.setObjectName("SuccessButton")
        btn_import_tasks.clicked.connect(self.import_tasks)
        ct_layout.addWidget(btn_import_tasks)
        layout.addWidget(self.card_tasks)
        
        layout.addStretch()

    def import_projects(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Projects Excel Sheet", "", "Excel Files (*.xlsx *.xls)")
        if filepath:
            count = ImportExportService.import_projects_from_excel(filepath)
            if count > 0:
                QMessageBox.information(self, "Import Complete", f"Successfully imported {count} new projects.")
            else:
                QMessageBox.warning(self, "Import Status", "No new projects were imported. Verify file schema format.")

    def import_categories(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Categories Excel Sheet", "", "Excel Files (*.xlsx *.xls)")
        if filepath:
            count = ImportExportService.import_categories_from_excel(filepath)
            if count > 0:
                QMessageBox.information(self, "Import Complete", f"Successfully imported {count} new categories.")
            else:
                QMessageBox.warning(self, "Import Status", "No new categories were imported. Verify file schema format.")

    def import_assigned_by(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Assignee Excel Sheet", "", "Excel Files (*.xlsx *.xls)")
        if filepath:
            count = ImportExportService.import_assigned_by_from_excel(filepath)
            if count > 0:
                QMessageBox.information(self, "Import Complete", f"Successfully imported {count} new assignee profiles.")
            else:
                QMessageBox.warning(self, "Import Status", "No new assignee profiles were imported. Verify file schema format.")

    def import_tasks(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Task Logs File", "", "Spreadsheets (*.xlsx *.xls *.csv)")
        if filepath:
            count = ImportExportService.import_tasks_from_file(filepath)
            if count > 0:
                QMessageBox.information(self, "Import Complete", f"Successfully imported {count} task logs.")
            else:
                QMessageBox.warning(self, "Import Status", "No task logs were imported. Verify column headers and file contents.")


# ==========================================
# EXPORT VIEW
# ==========================================

class ExportView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        heading = QLabel("Bulk Export Database Data", self)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)
        
        desc = QLabel(
            "Export the entire contents of the database tables directly into Excel or CSV spreadsheets. "
            "This provides a quick way to backup your data in tabular format.", 
            self
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #565f89; line-height: 1.4;")
        layout.addWidget(desc)
        
        # Table cards list
        tables = [
            ("tasks", "Task Logs (Full History)"),
            ("projects", "Projects Metadata list"),
            ("categories", "Category Configurations list"),
            ("assigned_by", "Assignee Profiles list")
        ]
        
        for table_key, title in tables:
            card = QFrame(self)
            card.setProperty("class", "Card")
            card_layout = QHBoxLayout(card)
            
            card_layout.addWidget(QLabel(title, card))
            
            btn_csv = QPushButton("Export CSV", card)
            btn_csv.clicked.connect(lambda checked=False, tk=table_key: self.export_table(tk, "csv"))
            card_layout.addWidget(btn_csv)
            
            btn_excel = QPushButton("Export Excel", card)
            btn_excel.clicked.connect(lambda checked=False, tk=table_key: self.export_table(tk, "excel"))
            card_layout.addWidget(btn_excel)
            
            layout.addWidget(card)
            
        layout.addStretch()

    def export_table(self, table_key: str, format_type: str):
        """Pulls raw table log objects and saves them as files."""
        # Query task history
        import pandas as pd
        from app.database.connection import get_db_session
        from app.models.task import Task
        from app.models.project import Project
        from app.models.category import Category
        from app.models.assigned_by import AssignedBy
        
        try:
            with get_db_session() as session:
                if table_key == "tasks":
                    tasks = session.query(Task).all()
                    data = []
                    for t in tasks:
                        data.append({
                            "uuid": t.uuid,
                            "task_number": t.task_number,
                            "title": t.title,
                            "description": t.description,
                            "project": t.project.project_name if t.project else "",
                            "category": t.category.category_name if t.category else "",
                            "assigned_by": t.assigned_by.person_name if t.assigned_by else "",
                            "priority": t.priority,
                            "status": t.status,
                            "completion": t.completion,
                            "start_time": t.start_time,
                            "end_time": t.end_time,
                            "duration_seconds": t.duration,
                            "remarks": t.remarks,
                            "created_at": t.created_at
                        })
                    df = pd.DataFrame(data)
                elif table_key == "projects":
                    projects = session.query(Project).all()
                    df = pd.DataFrame([{
                        "id": p.id,
                        "project_name": p.project_name,
                        "description": p.description,
                        "active": p.active
                    } for p in projects])
                elif table_key == "categories":
                    cats = session.query(Category).all()
                    df = pd.DataFrame([{"id": c.id, "category_name": c.category_name} for c in cats])
                elif table_key == "assigned_by":
                    ab = session.query(AssignedBy).all()
                    df = pd.DataFrame([{
                        "id": a.id,
                        "person_name": a.person_name,
                        "designation": a.designation
                    } for a in ab])
                else:
                    return

            if df.empty:
                QMessageBox.warning(self, "No Data", f"The table '{table_key}' has no records to export.")
                return
                
            filename = f"export_{table_key}.xlsx" if format_type == "excel" else f"export_{table_key}.csv"
            filter_str = "Excel Files (*.xlsx)" if format_type == "excel" else "CSV Files (*.csv)"
            
            filepath, _ = QFileDialog.getSaveFileName(self, f"Export {table_key} data", filename, filter_str)
            if filepath:
                if format_type == "excel":
                    df.to_excel(filepath, index=False)
                else:
                    df.to_csv(filepath, index=False, encoding="utf-8-sig")
                QMessageBox.information(self, "Export Successful", f"Table data exported successfully to:\n{filepath}")
        except Exception as e:
            logger.error(f"Error bulk exporting table {table_key}: {e}")
            QMessageBox.critical(self, "Export Error", f"Error occurred during bulk export:\n{e}")


# ==========================================
# ABOUT VIEW
# ==========================================

class AboutView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        heading = QLabel("About Daily Office Work Tracker", self)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)
        
        # Info Card
        info_card = QFrame(self)
        info_card.setProperty("class", "Card")
        ic_layout = QVBoxLayout(info_card)
        ic_layout.setSpacing(10)
        
        title = QLabel("Daily Office Work Tracker v1.0.0", info_card)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #7aa2f7;")
        ic_layout.addWidget(title)
        
        desc = QLabel(
            "A lightweight, offline-first task and time tracking desktop application built in Python.\n"
            "Keep logs of your tasks, priority status, categories, projects, and analyze your productivity "
            "locally and securely with zero network latency.",
            info_card
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("line-height: 1.4; color: #a9b1d6;")
        ic_layout.addWidget(desc)
        
        ic_layout.addWidget(QLabel("Built using: Python 3.12, PySide6 (Qt6), SQLite3, SQLAlchemy ORM, Matplotlib, and Pandas.", info_card))
        layout.addWidget(info_card)
        
        # Shortcuts Card
        shortcuts_card = QFrame(self)
        shortcuts_card.setProperty("class", "Card")
        sc_layout = QVBoxLayout(shortcuts_card)
        sc_layout.setSpacing(10)
        
        sc_layout.addWidget(QLabel("Keyboard Shortcuts Cheatsheet", shortcuts_card))
        sc_layout.itemAt(0).widget().setStyleSheet("font-weight: bold; color: #7aa2f7;")
        
        sc_list = [
            ("Ctrl + N", "Navigate to create a New Task"),
            ("Ctrl + S", "Save/Submit current task forms"),
            ("Ctrl + F", "Jump to History Log and focus search box"),
            ("Space", "Start / Pause active timer inside Running Task page")
        ]
        
        for keys, description in sc_list:
            row = QHBoxLayout()
            lbl_keys = QLabel(keys, shortcuts_card)
            lbl_keys.setStyleSheet("font-family: monospace; font-weight: bold; color: #9ece6a; min-width: 100px;")
            row.addWidget(lbl_keys)
            
            lbl_desc = QLabel(description, shortcuts_card)
            row.addWidget(lbl_desc)
            sc_layout.addLayout(row)
            
        layout.addWidget(shortcuts_card)
        layout.addStretch()
