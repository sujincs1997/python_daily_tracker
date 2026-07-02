# Modern Fluent UI Styling Sheet for Python Daily Work Tracker

DARK_THEME = """
/* Global styles */
QWidget {
    background-color: #1a1b26;
    color: #a9b1d6;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Sidebar navigation */
QFrame#Sidebar {
    background-color: #16161e;
    border-right: 1px solid #24283b;
    min-width: 220px;
    max-width: 220px;
}

QLabel#SidebarTitle {
    color: #7aa2f7;
    font-size: 16px;
    font-weight: bold;
    padding: 15px 10px;
    border-bottom: 2px solid #24283b;
    margin-bottom: 10px;
}

QListWidget#NavList {
    background-color: transparent;
    border: none;
    outline: none;
    padding: 5px;
}

QListWidget#NavList::item {
    padding: 10px 15px;
    border-radius: 6px;
    color: #a9b1d6;
    margin-bottom: 4px;
}

QListWidget#NavList::item:hover {
    background-color: #20233d;
    color: #7aa2f7;
}

QListWidget#NavList::item:selected {
    background-color: #2b3052;
    color: #7aa2f7;
    font-weight: bold;
    border-left: 3px solid #7aa2f7;
}

/* Content Pane */
QFrame#ContentFrame {
    background-color: #1a1b26;
    border: none;
}

/* Dashboard Cards */
QFrame.Card {
    background-color: #1f2335;
    border: 1px solid #24283b;
    border-radius: 8px;
    padding: 15px;
}

QLabel#CardTitle {
    color: #565f89;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
}

QLabel#CardValue {
    color: #c0caf5;
    font-size: 20px;
    font-weight: bold;
    margin-top: 5px;
}

/* Headings */
QLabel#SectionHeading {
    color: #7aa2f7;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
}

QLabel#SubHeading {
    color: #c0caf5;
    font-size: 14px;
    font-weight: bold;
    margin-top: 10px;
}

/* Buttons */
QPushButton {
    background-color: #24283b;
    color: #c0caf5;
    border: 1px solid #414868;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #3b4261;
}

QPushButton:pressed {
    background-color: #1f2335;
}

QPushButton#PrimaryButton {
    background-color: #7aa2f7;
    color: #1a1b26;
    border: none;
    font-weight: bold;
}

QPushButton#PrimaryButton:hover {
    background-color: #89ddff;
}

QPushButton#PrimaryButton:pressed {
    background-color: #3d59a1;
}

QPushButton#DangerButton {
    background-color: #f7768e;
    color: #1a1b26;
    border: none;
    font-weight: bold;
}

QPushButton#DangerButton:hover {
    background-color: #ff9e64;
}

QPushButton#DangerButton:pressed {
    background-color: #c53b53;
}

QPushButton#SuccessButton {
    background-color: #9ece6a;
    color: #1a1b26;
    border: none;
    font-weight: bold;
}

QPushButton#SuccessButton:hover {
    background-color: #b4f9f8;
}

QPushButton#SuccessButton:pressed {
    background-color: #73daca;
}

/* Input Fields */
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #24283b;
    border: 1px solid #414868;
    border-radius: 6px;
    padding: 6px 12px;
    color: #c0caf5;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #7aa2f7;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border: none;
}

/* Table Design */
QTableWidget {
    background-color: #1f2335;
    border: 1px solid #24283b;
    border-radius: 8px;
    gridline-color: #24283b;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #24283b;
}

QTableWidget::item:selected {
    background-color: #2b3052;
    color: #7aa2f7;
}

QHeaderView::section {
    background-color: #16161e;
    color: #7aa2f7;
    padding: 8px;
    border: none;
    font-weight: bold;
    border-bottom: 2px solid #24283b;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #16161e;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #414868;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #565f89;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #24283b;
    border-radius: 6px;
    background-color: #1f2335;
}

QTabBar::tab {
    background-color: #16161e;
    color: #a9b1d6;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: #1f2335;
    color: #7aa2f7;
}

QSlider::groove:horizontal {
    border: 1px solid #414868;
    height: 6px;
    background: #24283b;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #7aa2f7;
    border: 1px solid #7aa2f7;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
"""

LIGHT_THEME = """
/* Global styles */
QWidget {
    background-color: #f5f6fa;
    color: #2f3640;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Sidebar navigation */
QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 1px solid #dcdde1;
    min-width: 220px;
    max-width: 220px;
}

QLabel#SidebarTitle {
    color: #2f3542;
    font-size: 16px;
    font-weight: bold;
    padding: 15px 10px;
    border-bottom: 2px solid #f5f6fa;
    margin-bottom: 10px;
}

QListWidget#NavList {
    background-color: transparent;
    border: none;
    outline: none;
    padding: 5px;
}

QListWidget#NavList::item {
    padding: 10px 15px;
    border-radius: 6px;
    color: #57606f;
    margin-bottom: 4px;
}

QListWidget#NavList::item:hover {
    background-color: #f1f2f6;
    color: #1e90ff;
}

QListWidget#NavList::item:selected {
    background-color: #e8f4fd;
    color: #1e90ff;
    font-weight: bold;
    border-left: 3px solid #1e90ff;
}

/* Content Pane */
QFrame#ContentFrame {
    background-color: #f5f6fa;
    border: none;
}

/* Dashboard Cards */
QFrame.Card {
    background-color: #ffffff;
    border: 1px solid #dcdde1;
    border-radius: 8px;
    padding: 15px;
}

QLabel#CardTitle {
    color: #a4b0be;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
}

QLabel#CardValue {
    color: #2f3542;
    font-size: 20px;
    font-weight: bold;
    margin-top: 5px;
}

/* Headings */
QLabel#SectionHeading {
    color: #1e90ff;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
}

QLabel#SubHeading {
    color: #2f3542;
    font-size: 14px;
    font-weight: bold;
    margin-top: 10px;
}

/* Buttons */
QPushButton {
    background-color: #ffffff;
    color: #2f3640;
    border: 1px solid #ced6e0;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #f1f2f6;
}

QPushButton:pressed {
    background-color: #e4e7eb;
}

QPushButton#PrimaryButton {
    background-color: #1e90ff;
    color: #ffffff;
    border: none;
    font-weight: bold;
}

QPushButton#PrimaryButton:hover {
    background-color: #70a1ff;
}

QPushButton#PrimaryButton:pressed {
    background-color: #0070e0;
}

QPushButton#DangerButton {
    background-color: #ff4757;
    color: #ffffff;
    border: none;
    font-weight: bold;
}

QPushButton#DangerButton:hover {
    background-color: #ff6b81;
}

QPushButton#DangerButton:pressed {
    background-color: #cf2130;
}

QPushButton#SuccessButton {
    background-color: #2ed573;
    color: #ffffff;
    border: none;
    font-weight: bold;
}

QPushButton#SuccessButton:hover {
    background-color: #7bed9f;
}

QPushButton#SuccessButton:pressed {
    background-color: #1a9e50;
}

/* Input Fields */
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #ced6e0;
    border-radius: 6px;
    padding: 6px 12px;
    color: #2f3542;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #1e90ff;
}

/* Table Design */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #ced6e0;
    border-radius: 8px;
    gridline-color: #f1f2f6;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #f1f2f6;
}

QTableWidget::item:selected {
    background-color: #e8f4fd;
    color: #1e90ff;
}

QHeaderView::section {
    background-color: #ffffff;
    color: #1e90ff;
    padding: 8px;
    border: none;
    font-weight: bold;
    border-bottom: 2px solid #ced6e0;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #f1f2f6;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #ced6e0;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a4b0be;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #ced6e0;
    border-radius: 6px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #e4e7eb;
    color: #57606f;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background-color: #ffffff;
    color: #1e90ff;
}

QSlider::groove:horizontal {
    border: 1px solid #ced6e0;
    height: 6px;
    background: #e4e7eb;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #1e90ff;
    border: 1px solid #1e90ff;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
"""
