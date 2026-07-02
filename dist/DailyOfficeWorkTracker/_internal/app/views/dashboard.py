from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from PySide6.QtCore import Qt, Slot
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from app.utils.logger import logger

class MplCanvas(FigureCanvas):
    """A canvas that embeds a Matplotlib figure into PySide6."""
    def __init__(self, parent=None, width=5, height=3, dpi=100, is_dark=True):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.apply_style(is_dark)

    def apply_style(self, is_dark: bool):
        """Styles the plot axes, grid, labels, and ticks to match QSS themes."""
        bg_color = "#1f2335" if is_dark else "#ffffff"
        text_color = "#a9b1d6" if is_dark else "#2f3640"
        grid_color = "#414868" if is_dark else "#ced6e0"
        
        self.fig.patch.set_facecolor(bg_color)
        self.axes.set_facecolor(bg_color)
        self.axes.xaxis.label.set_color(text_color)
        self.axes.yaxis.label.set_color(text_color)
        self.axes.title.set_color(text_color)
        self.axes.tick_params(colors=text_color, which='both', labelsize=9)
        self.axes.grid(True, color=grid_color, linestyle='--', alpha=0.3)
        
        for spine in self.axes.spines.values():
            spine.set_color(grid_color)
            spine.set_linewidth(0.8)


class DashboardView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        # Connect timer signal to update the active card timer dynamically
        self.controller.timer_service.tick.connect(self.update_active_timer_card)
        self.controller.timer_service.status_changed.connect(self.handle_timer_status_change)
        
        self.setup_ui()
        self.refresh_dashboard()

    def setup_ui(self):
        """Constructs the dashboard view layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        heading = QLabel("Dashboard", self)
        heading.setObjectName("SectionHeading")
        layout.addWidget(heading)
        
        # 1. Statistics Cards Row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # Today's Hours Card
        self.card_hours = QFrame(self)
        self.card_hours.setProperty("class", "Card")
        ch_layout = QVBoxLayout(self.card_hours)
        ch_title = QLabel("TODAY'S HOURS", self.card_hours)
        ch_title.setObjectName("CardTitle")
        self.lbl_hours_val = QLabel("0.00 hrs", self.card_hours)
        self.lbl_hours_val.setObjectName("CardValue")
        ch_layout.addWidget(ch_title)
        ch_layout.addWidget(self.lbl_hours_val)
        cards_layout.addWidget(self.card_hours)
        
        # Today's Tasks Count Card (Completed / Total)
        self.card_tasks = QFrame(self)
        self.card_tasks.setProperty("class", "Card")
        ct_layout = QVBoxLayout(self.card_tasks)
        ct_title = QLabel("TODAY'S TASKS", self.card_tasks)
        ct_title.setObjectName("CardTitle")
        self.lbl_tasks_val = QLabel("0 completed (0 pending)", self.card_tasks)
        self.lbl_tasks_val.setObjectName("CardValue")
        self.lbl_tasks_val.setStyleSheet("font-size: 15px;") # Slight reduction to fit text
        ct_layout.addWidget(ct_title)
        ct_layout.addWidget(self.lbl_tasks_val)
        cards_layout.addWidget(self.card_tasks)
        
        # Completion Rate Card
        self.card_completion = QFrame(self)
        self.card_completion.setProperty("class", "Card")
        cc_layout = QVBoxLayout(self.card_completion)
        cc_title = QLabel("COMPLETION RATE", self.card_completion)
        cc_title.setObjectName("CardTitle")
        self.lbl_completion_val = QLabel("0.0%", self.card_completion)
        self.lbl_completion_val.setObjectName("CardValue")
        cc_layout.addWidget(cc_title)
        cc_layout.addWidget(self.lbl_completion_val)
        cards_layout.addWidget(self.card_completion)
        
        # Running Timer Card
        self.card_timer = QFrame(self)
        self.card_timer.setProperty("class", "Card")
        ctm_layout = QVBoxLayout(self.card_timer)
        ctm_title = QLabel("CURRENTLY RUNNING", self.card_timer)
        ctm_title.setObjectName("CardTitle")
        self.lbl_timer_task_title = QLabel("No Running Task", self.card_timer)
        self.lbl_timer_task_title.setObjectName("CardValue")
        self.lbl_timer_task_title.setStyleSheet("font-size: 14px; font-weight: normal;")
        self.lbl_timer_clock = QLabel("00:00:00", self.card_timer)
        self.lbl_timer_clock.setObjectName("CardValue")
        self.lbl_timer_clock.setStyleSheet("color: #7aa2f7; font-size: 18px;")
        ctm_layout.addWidget(ctm_title)
        ctm_layout.addWidget(self.lbl_timer_task_title)
        ctm_layout.addWidget(self.lbl_timer_clock)
        cards_layout.addWidget(self.card_timer)
        
        layout.addLayout(cards_layout)
        
        # 2. Main content split (Graph on Left, Recent Tasks on Right)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(15)
        
        # Graph Block
        self.graph_frame = QFrame(self)
        self.graph_frame.setProperty("class", "Card")
        gf_layout = QVBoxLayout(self.graph_frame)
        gf_title = QLabel("Weekly Productivity Trend (Hours)", self.graph_frame)
        gf_title.setObjectName("SubHeading")
        gf_layout.addWidget(gf_title)
        
        is_dark = self.controller.get_current_theme() == "dark"
        self.canvas = MplCanvas(self.graph_frame, width=5, height=3, dpi=100, is_dark=is_dark)
        gf_layout.addWidget(self.canvas)
        split_layout.addWidget(self.graph_frame, stretch=3)
        
        # Recent Activities Table Block
        self.recent_frame = QFrame(self)
        self.recent_frame.setProperty("class", "Card")
        rf_layout = QVBoxLayout(self.recent_frame)
        rf_title = QLabel("Recent Tasks Today", self.recent_frame)
        rf_title.setObjectName("SubHeading")
        rf_layout.addWidget(rf_title)
        
        self.table = QTableWidget(self.recent_frame)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Task #", "Title", "Category", "Duration"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        rf_layout.addWidget(self.table)
        
        split_layout.addWidget(self.recent_frame, stretch=2)
        
        layout.addLayout(split_layout)

    def refresh_dashboard(self):
        """Requests updated statistics and updates graph and tables."""
        stats = self.controller.task_controller.get_dashboard_stats()
        
        # Update labels
        self.lbl_hours_val.setText(f"{stats['today_hours']:.2f} hrs")
        self.lbl_tasks_val.setText(f"{stats['completed_tasks_today']} completed ({stats['pending_tasks_today']} pending)")
        self.lbl_completion_val.setText(f"{stats['completion_percentage']:.1f}%")
        
        # Active task
        if stats["current_task_uuid"]:
            self.lbl_timer_task_title.setText(stats["current_task"])
            formatted_dur = self.controller.timer_service.format_duration(self.controller.timer_service.elapsed_seconds)
            self.lbl_timer_clock.setText(formatted_dur)
        else:
            self.lbl_timer_task_title.setText("No Running Task")
            self.lbl_timer_clock.setText("00:00:00")

        # Redraw Chart
        self.plot_weekly_productivity()
        
        # Load Recent Activities (Limit 5)
        recent_tasks = self.controller.task_controller.get_recent_tasks(limit=5)
        self.table.setRowCount(0)
        for i, t in enumerate(recent_tasks):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(t["task_number"]))
            self.table.setItem(i, 1, QTableWidgetItem(t["title"]))
            self.table.setItem(i, 2, QTableWidgetItem(t["category_name"]))
            self.table.setItem(i, 3, QTableWidgetItem(t["duration_formatted"]))

    def plot_weekly_productivity(self):
        """Queries weekly hours logged and draws the bar graph."""
        weekly_data = self.controller.task_controller.get_weekly_productivity_data()
        
        # Reset axes
        self.canvas.axes.clear()
        is_dark = self.controller.get_current_theme() == "dark"
        self.canvas.apply_style(is_dark)
        
        days = list(weekly_data.keys())
        hours = list(weekly_data.values())
        
        # Plot styling colors
        bar_color = "#7aa2f7" if is_dark else "#1e90ff"
        
        # Draw bar chart
        self.canvas.axes.bar(days, hours, color=bar_color, width=0.5, zorder=3)
        self.canvas.axes.set_ylabel("Logged Hours")
        self.canvas.axes.set_ylim(bottom=0, top=max(hours + [8.0]) + 1.0) # Show at least up to 8 hours mark
        
        # Redraw
        self.canvas.draw()

    @Slot(str, int)
    def update_active_timer_card(self, formatted_time: str, elapsed_seconds: int):
        """Updates the running timer clock on the dashboard card."""
        active_task_uuid = self.controller.timer_service.current_task_uuid
        if active_task_uuid:
            task_details = self.controller.task_controller.get_task_by_uuid(active_task_uuid)
            title = task_details["title"] if task_details else "Running Task"
            self.lbl_timer_task_title.setText(title[:25] + "..." if len(title) > 25 else title)
            self.lbl_timer_clock.setText(formatted_time)

    @Slot(str)
    def handle_timer_status_change(self, status: str):
        """Updates the timer card elements on stop."""
        if status == "Stopped":
            self.lbl_timer_task_title.setText("No Running Task")
            self.lbl_timer_clock.setText("00:00:00")
            self.refresh_dashboard()
