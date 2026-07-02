import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database.connection import get_db_session, init_db, get_db_path
from app.controllers.settings_controller import SettingsController
from app.controllers.task_controller import TaskController
from app.services.import_export_service import ImportExportService
from app.models import Task, Project, Category, AssignedBy
from app.utils.logger import logger

def run_tests():
    logger.info("Initializing backend verification checks...")
    
    # 1. Initialize DB and create tables
    init_db()
    db_file = get_db_path()
    logger.info(f"Database file located at: {db_file}")
    assert os.path.exists(db_file), "Database file was not created!"
    
    # 2. Instantiate controllers
    sc = SettingsController()
    tc = TaskController()
    
    # 3. Test Projects CRUD
    logger.info("Testing Project operations...")
    orig_proj_count = len(sc.get_all_projects(include_archived=True))
    
    # Add project
    test_proj_name = "Test Verification Project"
    add_ok = sc.add_project(test_proj_name, "Used for verification testing")
    assert add_ok, "Failed to add project"
    
    projects = sc.get_all_projects(include_archived=True)
    assert len(projects) == orig_proj_count + 1, "Project count mismatch"
    
    new_proj = [p for p in projects if p["project_name"] == test_proj_name][0]
    assert new_proj["description"] == "Used for verification testing", "Description mismatch"
    
    # Update project
    update_ok = sc.update_project(new_proj["id"], test_proj_name, "Updated description", False)
    assert update_ok, "Failed to update project"
    
    projects_updated = sc.get_all_projects(include_archived=True)
    updated_proj = [p for p in projects_updated if p["id"] == new_proj["id"]][0]
    assert updated_proj["description"] == "Updated description", "Description update failed"
    assert updated_proj["active"] is False, "Active toggle update failed"
    
    # 4. Test Categories CRUD
    logger.info("Testing Category operations...")
    orig_cat_count = len(sc.get_all_categories())
    
    test_cat_name = "Test Category"
    cat_ok = sc.add_category(test_cat_name)
    assert cat_ok, "Failed to add category"
    
    categories = sc.get_all_categories()
    assert len(categories) == orig_cat_count + 1, "Category count mismatch"
    new_cat = [c for c in categories if c["category_name"] == test_cat_name][0]
    
    # 5. Test Assigned By CRUD
    logger.info("Testing Assignee operations...")
    orig_ab_count = len(sc.get_all_assigned_by())
    
    test_ab_name = "Test Lead Guy"
    ab_ok = sc.add_assigned_by(test_ab_name, "QA Senior")
    assert ab_ok, "Failed to add assignee"
    
    assignees = sc.get_all_assigned_by()
    assert len(assignees) == orig_ab_count + 1, "Assignee count mismatch"
    new_ab = [a for a in assignees if a["person_name"] == test_ab_name][0]
    
    # 6. Test Task operations
    logger.info("Testing Task creation and tracking...")
    task_num = tc.get_next_task_number()
    task_data = {
        "title": "Backend Verification Task Run",
        "description": "Running backend automation checks",
        "project_id": new_proj["id"],
        "category_id": new_cat["id"],
        "assigned_by_id": new_ab["id"],
        "priority": "Critical",
        "status": "In Progress",
        "completion": 20,
        "duration": 3600, # 1 hour
        "remarks": "Automated log entries."
    }
    
    task_created = tc.create_task(task_data)
    assert task_created is not None, "Task creation failed"
    assert task_created["task_number"] == task_num, "Task number mismatch"
    assert task_created["priority"] == "Critical", "Task priority mismatch"
    
    # Verify search and filters
    filters = {
        "project_id": new_proj["id"],
        "priority": "Critical"
    }
    filtered_tasks = tc.search_and_filter_tasks(filters, "Backend")
    assert len(filtered_tasks) == 1, "Filter task query failed"
    
    # 7. Test Dashboard Metrics
    logger.info("Testing Dashboard Statistics calculation...")
    stats = tc.get_dashboard_stats()
    assert stats["today_tasks"] > 0, "Dashboard stats: today_tasks failed"
    assert stats["most_used_category"] == test_cat_name or stats["most_used_category"] != "None", "Dashboard stats: most used category failed"
    
    # 8. Test Export Reports
    logger.info("Testing CSV/Excel Reports generation...")
    report_data = []
    for t in filtered_tasks:
        report_data.append({
            "Task Number": t["task_number"],
            "Title": t["title"],
            "Project": t["project_name"],
            "Category": t["category_name"],
            "Hours": round(t["duration"] / 3600.0, 2),
            "Date": t["created_date"]
        })
    df = pd.DataFrame(report_data)
    
    csv_file = "test_productivity.csv"
    xlsx_file = "test_productivity.xlsx"
    pdf_file = "test_productivity.pdf"
    
    csv_ok = ImportExportService.export_to_csv(df, csv_file)
    xlsx_ok = ImportExportService.export_to_excel(df, xlsx_file)
    pdf_ok = ImportExportService.export_to_pdf(
        ["Task Number", "Title", "Project", "Category", "Hours", "Date"],
        df[["Task Number", "Title", "Project", "Category", "Hours", "Date"]].values.tolist(),
        "Verification Test Report", "Sub-header filters info", pdf_file
    )
    
    assert csv_ok and os.path.exists(csv_file), "CSV export failed"
    assert xlsx_ok and os.path.exists(xlsx_file), "Excel export failed"
    assert pdf_ok and os.path.exists(pdf_file), "PDF export failed"
    
    # Cleanup export test files
    os.remove(csv_file)
    os.remove(xlsx_file)
    os.remove(pdf_file)
    
    # 9. Clean up database items added during tests to keep DB neat
    logger.info("Cleaning up verification items from database...")
    with get_db_session() as session:
        # Delete task
        session.query(Task).filter_by(id=task_created["id"]).delete()
        # Delete project
        session.query(Project).filter_by(id=new_proj["id"]).delete()
        # Delete category
        session.query(Category).filter_by(id=new_cat["id"]).delete()
        # Delete assignee
        session.query(AssignedBy).filter_by(id=new_ab["id"]).delete()
        session.commit()
        
    logger.info("Verification checks completed successfully! All checks passed.")

if __name__ == "__main__":
    run_tests()
