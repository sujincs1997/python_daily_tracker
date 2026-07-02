import sys
import os
from PySide6.QtWidgets import QApplication
from app.utils.logger import logger
from app.database.connection import init_db, get_db_session
from app.models.project import Project
from app.controllers.main_controller import MainController
from app.views.main_window import MainWindow
from seed_db import seed_database

def check_and_seed_if_needed():
    """Checks if database contains any projects; if not, triggers the seeder."""
    try:
        with get_db_session() as session:
            project_count = session.query(Project).count()
            if project_count == 0:
                logger.info("Database is empty. Seeding default data...")
                seed_database()
    except Exception as e:
        logger.error(f"Error checking database state: {e}")

def main():
    logger.info("Starting Daily Office Work Tracker application...")
    
    # 1. Initialize DB and create tables if needed
    init_db()
    
    # 2. Automatically seed defaults if database is brand new
    check_and_seed_if_needed()
    
    # 3. Initialize PySide6 Application
    app = QApplication(sys.argv)
    app.setApplicationName("DailyOfficeWorkTracker")
    app.setApplicationDisplayName("Daily Office Work Tracker")
    
    # 4. Instantiate Controllers
    controller = MainController()
    
    # 5. Instantiate Views
    window = MainWindow(controller)
    window.show()
    
    # 6. Run Event Loop
    sys.exit(app.exec())

if __name__ == "__main__":
    # Add current directory to python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    main()
