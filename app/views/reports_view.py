import os
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Slot, Qt
from app.views.dashboard import MplCanvas
from app.utils.logger import logger

class ReportsView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        self.current_report_df = pd.DataFrame()
        self.setup_ui()
        self.refresh_combos()

    def setup_ui(self):
        """Constructs the report configuration filter and preview pane layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        heading = QLabel("Productivity Reports & Chart Exports", self)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)
        
        # 1. FILTERS BLOCK CARD
        filters_card = QFrame(self)
        filters_card.setProperty("class", "Card")
        f_layout = QVBoxLayout(filters_card)
        f_layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        row1.addWidget(QLabel("Report Type:", filters_card))
        self.cmb_report_type = QComboBox(filters_card)
        self.cmb_report_type.addItems([
            "Daily Report", 
            "Weekly Report", 
            "Monthly Report", 
            "Project Wise Report", 
            "Category Wise Report",
            "Employee Productivity Report"
        ])
        self.cmb_report_type.currentTextChanged.connect(self._on_report_type_changed)
        row1.addWidget(self.cmb_report_type)
        
        # Dropdowns
        self.cmb_project = QComboBox(filters_card)
        row1.addWidget(self.cmb_project)
        
        self.cmb_category = QComboBox(filters_card)
        row1.addWidget(self.cmb_category)
        
        self.cmb_assigned_by = QComboBox(filters_card)
        row1.addWidget(self.cmb_assigned_by)
        
        f_layout.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        self.cmb_priority = QComboBox(filters_card)
        row2.addWidget(self.cmb_priority)
        
        self.cmb_status = QComboBox(filters_card)
        row2.addWidget(self.cmb_status)
        
        self.btn_generate = QPushButton("Generate Report", filters_card)
        self.btn_generate.setObjectName("PrimaryButton")
        self.btn_generate.clicked.connect(self.generate_report)
        row2.addWidget(self.btn_generate)
        
        f_layout.addLayout(row2)
        layout.addWidget(filters_card)
        
        # 2. SPLIT LAYOUT (Table Preview on Left, Matplotlib Chart on Right)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(15)
        
        # Preview Table Block
        self.table_card = QFrame(self)
        self.table_card.setProperty("class", "Card")
        t_layout = QVBoxLayout(self.table_card)
        t_layout.addWidget(QLabel("Report Data Preview", self.table_card))
        
        self.table = QTableWidget(self.table_card)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Task #", "Title", "Project", "Category", "Hours", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        t_layout.addWidget(self.table)
        
        split_layout.addWidget(self.table_card, stretch=3)
        
        # Chart Block
        self.chart_card = QFrame(self)
        self.chart_card.setProperty("class", "Card")
        self.chart_card.setMinimumWidth(350)
        c_layout = QVBoxLayout(self.chart_card)
        self.lbl_chart_title = QLabel("Report Chart Visualization", self.chart_card)
        self.lbl_chart_title.setObjectName("SubHeading")
        c_layout.addWidget(self.lbl_chart_title)
        
        is_dark = self.controller.get_current_theme() == "dark"
        self.canvas = MplCanvas(self.chart_card, width=4, height=3, dpi=100, is_dark=is_dark)
        c_layout.addWidget(self.canvas)
        
        split_layout.addWidget(self.chart_card, stretch=2)
        
        layout.addLayout(split_layout)
        
        # 3. EXPORT BUTTONS ROW
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)
        
        self.btn_csv = QPushButton("Export to CSV", self)
        self.btn_csv.clicked.connect(self.export_csv)
        export_layout.addWidget(self.btn_csv)
        
        self.btn_excel = QPushButton("Export to Excel", self)
        self.btn_excel.clicked.connect(self.export_excel)
        export_layout.addWidget(self.btn_excel)
        
        self.btn_pdf = QPushButton("Export to PDF", self)
        self.btn_pdf.clicked.connect(self.export_pdf)
        export_layout.addWidget(self.btn_pdf)
        
        layout.addLayout(export_layout)

    def refresh_combos(self):
        """Prepares drop-downs with settings fields."""
        self.cmb_project.blockSignals(True)
        self.cmb_category.blockSignals(True)
        self.cmb_assigned_by.blockSignals(True)
        self.cmb_priority.blockSignals(True)
        self.cmb_status.blockSignals(True)
        
        self.cmb_project.clear()
        self.cmb_project.addItem("All Projects", None)
        for p in self.controller.settings_controller.get_all_projects(include_archived=True):
            self.cmb_project.addItem(p["project_name"], p["id"])
            
        self.cmb_category.clear()
        self.cmb_category.addItem("All Categories", None)
        for c in self.controller.settings_controller.get_all_categories():
            self.cmb_category.addItem(c["category_name"], c["id"])
            
        self.cmb_assigned_by.clear()
        self.cmb_assigned_by.addItem("All Assignees", None)
        for ab in self.controller.settings_controller.get_all_assigned_by():
            self.cmb_assigned_by.addItem(ab["person_name"], ab["id"])
            
        self.cmb_priority.clear()
        self.cmb_priority.addItem("All Priorities")
        for pr in self.controller.settings_controller.get_config_setting("priorities", []):
            self.cmb_priority.addItem(pr)
            
        self.cmb_status.clear()
        self.cmb_status.addItem("All Statuses")
        for st in self.controller.settings_controller.get_config_setting("statuses", []):
            self.cmb_status.addItem(st)

        self.cmb_project.blockSignals(False)
        self.cmb_category.blockSignals(False)
        self.cmb_assigned_by.blockSignals(False)
        self.cmb_priority.blockSignals(False)
        self.cmb_status.blockSignals(False)

    def _on_report_type_changed(self, text):
        # We can dynamically configure visible dropdowns, but keeping simple
        pass

    @Slot()
    def generate_report(self):
        """Queries datasets, displays them in the table, and calls chart plotting functions."""
        rep_type = self.cmb_report_type.currentText()
        
        # Build query filters based on report type mapping
        # Maps report type to date filter names
        date_map = {
            "Daily Report": "Today",
            "Weekly Report": "Last 7 Days",
            "Monthly Report": "Current Month",
            "Project Wise Report": "All Time",
            "Category Wise Report": "All Time",
            "Employee Productivity Report": "All Time"
        }
        
        filters = {
            "date_filter": date_map.get(rep_type, "All Time"),
            "project_id": self.cmb_project.currentData(),
            "category_id": self.cmb_category.currentData(),
            "assigned_by_id": self.cmb_assigned_by.currentData(),
            "priority": self.cmb_priority.currentText() if self.cmb_priority.currentIndex() > 0 else None,
            "status": self.cmb_status.currentText() if self.cmb_status.currentIndex() > 0 else None
        }
        
        tasks = self.controller.task_controller.search_and_filter_tasks(filters, "")
        
        if not tasks:
            self.table.setRowCount(0)
            self.current_report_df = pd.DataFrame()
            self.canvas.axes.clear()
            self.canvas.draw()
            QMessageBox.information(self, "No Data", "No task logs found matching the selected filters.")
            return

        # Build Pandas DataFrame from results for summaries and exports
        data_list = []
        for t in tasks:
            hours = round(t["duration"] / 3600.0, 2)
            data_list.append({
                "Task Number": t["task_number"],
                "Title": t["title"],
                "Project": t["project_name"],
                "Category": t["category_name"],
                "Assigned By": t["assigned_by_name"],
                "Priority": t["priority"],
                "Status": t["status"],
                "Completion %": t["completion"],
                "Hours": hours,
                "Duration (s)": t["duration"],
                "Date": t["created_date"]
            })
            
        self.current_report_df = pd.DataFrame(data_list)
        
        # Populate Preview Table (showing top columns)
        self.table.setRowCount(0)
        for i, row in self.current_report_df.iterrows():
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row["Task Number"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row["Title"])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row["Project"])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row["Category"])))
            self.table.setItem(i, 4, QTableWidgetItem(f"{row['Hours']:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(str(row["Date"])))

        # Update Chart display
        self.draw_chart(rep_type)

    def draw_chart(self, report_type: str):
        """Plots charts dynamically inside the Matplotlib canvas."""
        self.canvas.axes.clear()
        is_dark = self.controller.get_current_theme() == "dark"
        self.canvas.apply_style(is_dark)
        
        df = self.current_report_df
        if df.empty:
            return
            
        accent_color = "#7aa2f7" if is_dark else "#1e90ff"
        grid_line_color = "#414868" if is_dark else "#ced6e0"
        
        if report_type == "Category Wise Report":
            self.lbl_chart_title.setText("Task Category Distribution (Hours)")
            # Group by category
            grouped = df.groupby("Category")["Hours"].sum()
            labels = grouped.index.tolist()
            values = grouped.values.tolist()
            
            # Pie Chart
            pie_theme = plt.cm.tab20c.colors if len(labels) <= 20 else plt.cm.viridis.colors
            self.canvas.axes.pie(
                values, labels=labels, autopct='%1.1f%%', 
                startangle=140, colors=pie_theme,
                textprops={'color': "#a9b1d6" if is_dark else "#2f3640", 'fontsize': 8}
            )
            
        elif report_type == "Project Wise Report":
            self.lbl_chart_title.setText("Hours Spent Per Project")
            grouped = df.groupby("Project")["Hours"].sum()
            labels = grouped.index.tolist()
            values = grouped.values.tolist()
            
            # Horizontal Bar Chart
            self.canvas.axes.barh(labels, values, color=accent_color, zorder=3)
            self.canvas.axes.set_xlabel("Logged Hours")
            
        elif report_type == "Employee Productivity Report":
            self.lbl_chart_title.setText("Hours Logged by Assignee")
            grouped = df.groupby("Assigned By")["Hours"].sum()
            labels = grouped.index.tolist()
            values = grouped.values.tolist()
            
            # Bar Chart
            self.canvas.axes.bar(labels, values, color="#9ece6a" if is_dark else "#2ed573", width=0.4, zorder=3)
            self.canvas.axes.set_ylabel("Logged Hours")
            
        else: # Daily, Weekly, Monthly - Line charts
            self.lbl_chart_title.setText("Daily Working Hours Trend")
            grouped = df.groupby("Date")["Hours"].sum().sort_index()
            dates = grouped.index.tolist()
            values = grouped.values.tolist()
            
            # Line Chart
            self.canvas.axes.plot(dates, values, marker='o', color=accent_color, linewidth=2, zorder=3)
            self.canvas.axes.set_ylabel("Hours Worked")
            # Rotate x dates
            self.canvas.fig.autofmt_xdate()
            
        self.canvas.draw()

    # ==========================================
    # EXPORT HOOKS
    # ==========================================

    def export_csv(self):
        if self.current_report_df.empty:
            QMessageBox.warning(self, "No Data", "Generate a report before attempting to export.")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(self, "Save CSV Report", "productivity_report.csv", "CSV Files (*.csv)")
        if filepath:
            from app.services.import_export_service import ImportExportService
            success = ImportExportService.export_to_csv(self.current_report_df, filepath)
            if success:
                QMessageBox.information(self, "Export Complete", "CSV report exported successfully.")

    def export_excel(self):
        if self.current_report_df.empty:
            QMessageBox.warning(self, "No Data", "Generate a report before attempting to export.")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Excel Report", "productivity_report.xlsx", "Excel Files (*.xlsx)")
        if filepath:
            from app.services.import_export_service import ImportExportService
            success = ImportExportService.export_to_excel(self.current_report_df, filepath)
            if success:
                QMessageBox.information(self, "Export Complete", "Excel report exported successfully.")

    def export_pdf(self):
        if self.current_report_df.empty:
            QMessageBox.warning(self, "No Data", "Generate a report before attempting to export.")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "productivity_report.pdf", "PDF Files (*.pdf)")
        if filepath:
            from app.services.import_export_service import ImportExportService
            
            # Prepare ReportLab inputs
            # Columns to export
            cols = ["Task Number", "Title", "Project", "Category", "Priority", "Status", "Hours", "Date"]
            df_sub = self.current_report_df[cols]
            
            headers = cols
            data = df_sub.values.tolist()
            
            rep_title = f"{self.cmb_report_type.currentText()} - Productivity Log"
            subtitle = f"Filters Applied - Project: {self.cmb_project.currentText()} | Category: {self.cmb_category.currentText()}"
            
            success = ImportExportService.export_to_pdf(headers, data, rep_title, subtitle, filepath)
            if success:
                QMessageBox.information(self, "Export Complete", "PDF report exported successfully.")
            else:
                QMessageBox.critical(self, "Export Error", "Could not generate PDF report.")
