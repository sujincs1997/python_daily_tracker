from app.database.connection import get_db_session, init_db
from app.models.project import Project
from app.models.category import Category
from app.models.assigned_by import AssignedBy
from app.utils.logger import logger

def seed_database():
    """Seeds the initial dataset into the database."""
    init_db()  # Ensure database and tables exist
    
    with get_db_session() as session:
        # 1. Seed Categories
        categories_data = [
            "Design", "GIS", "Development", "QA", "Documentation",
            "Meeting", "Site Work", "Research", "Training", "Support",
            "Administration", "Other"
        ]
        
        logger.info("Seeding categories...")
        for cat_name in categories_data:
            existing = session.query(Category).filter_by(category_name=cat_name).first()
            if not existing:
                session.add(Category(category_name=cat_name))
                logger.info(f"Added category: {cat_name}")
            else:
                logger.debug(f"Category already exists: {cat_name}")

        # 2. Seed Projects
        projects_data = [
            {"name": "FTTH Project", "desc": "Fiber To The Home network rollout design and execution", "active": True},
            {"name": "GIS Migration", "desc": "Migrate legacy spatial data to ArcGIS Enterprise", "active": True},
            {"name": "Telecom Survey", "desc": "On-site utility survey of telecom towers", "active": True},
            {"name": "Utility Mapping", "desc": "Water and electrical network asset mapping", "active": True},
            {"name": "Internal Development", "desc": "Development of internal helper tools", "active": True},
            {"name": "Customer Support", "desc": "Post-deployment support services", "active": True}
        ]
        
        logger.info("Seeding projects...")
        for proj in projects_data:
            existing = session.query(Project).filter_by(project_name=proj["name"]).first()
            if not existing:
                session.add(Project(project_name=proj["name"], description=proj["desc"], active=proj["active"]))
                logger.info(f"Added project: {proj['name']}")
            else:
                logger.debug(f"Project already exists: {proj['name']}")

        # 3. Seed Assigned By
        assigned_by_data = [
            {"name": "Manager", "desg": "Project Manager"},
            {"name": "Team Lead", "desg": "Technical Lead"},
            {"name": "Client", "desg": "External Client Representative"},
            {"name": "Self", "desg": "Individual Developer/User"},
            {"name": "Other", "desg": "General Coordinator"}
        ]
        
        logger.info("Seeding assigned_by...")
        for pers in assigned_by_data:
            existing = session.query(AssignedBy).filter_by(person_name=pers["name"]).first()
            if not existing:
                session.add(AssignedBy(person_name=pers["name"], designation=pers["desg"]))
                logger.info(f"Added assigned_by: {pers['name']}")
            else:
                logger.debug(f"AssignedBy already exists: {pers['name']}")

        session.commit()
    logger.info("Seeding complete.")

if __name__ == "__main__":
    import sys
    # Add parent directory to path so script can run from root
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    seed_database()
