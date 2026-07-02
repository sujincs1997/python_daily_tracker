from typing import List, Dict, Any
from app.database.connection import get_db_session
from app.models.project import Project
from app.models.category import Category
from app.models.assigned_by import AssignedBy
from app.utils.config import config_manager
from app.services.backup_service import BackupService
from app.utils.logger import logger

class SettingsController:
    def __init__(self):
        pass

    # ==========================================
    # PROJECT CRUD
    # ==========================================
    
    def get_all_projects(self, include_archived: bool = True) -> List[Dict[str, Any]]:
        """Retrieves list of projects."""
        try:
            with get_db_session() as session:
                query = session.query(Project)
                if not include_archived:
                    query = query.filter(Project.active == True)
                projects = query.all()
                return [
                    {
                        "id": p.id,
                        "project_name": p.project_name,
                        "description": p.description,
                        "active": p.active
                    }
                    for p in projects
                ]
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return []

    def add_project(self, name: str, description: str = "") -> bool:
        """Adds a new project."""
        name = name.strip()
        if not name:
            return False
            
        try:
            with get_db_session() as session:
                # Check duplication
                existing = session.query(Project).filter_by(project_name=name).first()
                if existing:
                    logger.warning(f"Project '{name}' already exists.")
                    return False
                
                project = Project(project_name=name, description=description, active=True)
                session.add(project)
                session.commit()
                logger.info(f"Project '{name}' added successfully.")
                return True
        except Exception as e:
            logger.error(f"Error adding project: {e}")
            return False

    def update_project(self, project_id: int, name: str, description: str, active: bool) -> bool:
        """Updates an existing project's parameters."""
        name = name.strip()
        if not name:
            return False
            
        try:
            with get_db_session() as session:
                project = session.query(Project).get(project_id)
                if not project:
                    logger.error(f"Project with ID {project_id} not found.")
                    return False
                
                # Check duplicate name if renamed
                if project.project_name != name:
                    duplicate = session.query(Project).filter_by(project_name=name).first()
                    if duplicate:
                        logger.warning(f"Cannot rename; project '{name}' already exists.")
                        return False
                
                project.project_name = name
                project.description = description
                project.active = active
                session.commit()
                logger.info(f"Project ID {project_id} updated successfully.")
                return True
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return False

    def delete_project(self, project_id: int) -> bool:
        """Deletes a project. If it has associated tasks, it will raise an error or fail to protect integrity."""
        try:
            with get_db_session() as session:
                project = session.query(Project).get(project_id)
                if not project:
                    return False
                
                session.delete(project)
                session.commit()
                logger.info(f"Project ID {project_id} deleted successfully.")
                return True
        except Exception as e:
            logger.error(f"Error deleting project: {e}. Project may be referenced in tasks.")
            return False

    # ==========================================
    # CATEGORY CRUD
    # ==========================================

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Retrieves list of categories."""
        try:
            with get_db_session() as session:
                categories = session.query(Category).all()
                return [{"id": c.id, "category_name": c.category_name} for c in categories]
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    def add_category(self, name: str) -> bool:
        """Adds a new category."""
        name = name.strip()
        if not name:
            return False
            
        try:
            with get_db_session() as session:
                existing = session.query(Category).filter_by(category_name=name).first()
                if existing:
                    logger.warning(f"Category '{name}' already exists.")
                    return False
                
                cat = Category(category_name=name)
                session.add(cat)
                session.commit()
                logger.info(f"Category '{name}' added successfully.")
                return True
        except Exception as e:
            logger.error(f"Error adding category: {e}")
            return False

    def delete_category(self, category_id: int) -> bool:
        """Deletes a category."""
        try:
            with get_db_session() as session:
                cat = session.query(Category).get(category_id)
                if not cat:
                    return False
                session.delete(cat)
                session.commit()
                logger.info(f"Category ID {category_id} deleted successfully.")
                return True
        except Exception as e:
            logger.error(f"Error deleting category: {e}. Category might be referenced in tasks.")
            return False

    # ==========================================
    # ASSIGNED BY CRUD
    # ==========================================

    def get_all_assigned_by(self) -> List[Dict[str, Any]]:
        """Retrieves list of assignees."""
        try:
            with get_db_session() as session:
                list_ab = session.query(AssignedBy).all()
                return [{"id": a.id, "person_name": a.person_name, "designation": a.designation} for a in list_ab]
        except Exception as e:
            logger.error(f"Error fetching Assigned By list: {e}")
            return []

    def add_assigned_by(self, name: str, designation: str = "") -> bool:
        """Adds a new assignee profile."""
        name = name.strip()
        if not name:
            return False
            
        try:
            with get_db_session() as session:
                existing = session.query(AssignedBy).filter(
                    AssignedBy.person_name == name,
                    AssignedBy.designation == designation
                ).first()
                if existing:
                    logger.warning(f"Assignee '{name}' with designation '{designation}' already exists.")
                    return False
                
                ab = AssignedBy(person_name=name, designation=designation)
                session.add(ab)
                session.commit()
                logger.info(f"Assigned By '{name}' added successfully.")
                return True
        except Exception as e:
            logger.error(f"Error adding Assigned By: {e}")
            return False

    def delete_assigned_by(self, id_ab: int) -> bool:
        """Deletes an assignee profile."""
        try:
            with get_db_session() as session:
                ab = session.query(AssignedBy).get(id_ab)
                if not ab:
                    return False
                session.delete(ab)
                session.commit()
                logger.info(f"Assigned By ID {id_ab} deleted successfully.")
                return True
        except Exception as e:
            logger.error(f"Error deleting Assigned By: {e}. It might be referenced in tasks.")
            return False

    # ==========================================
    # CONFIG MANAGEMENT
    # ==========================================

    def get_config_setting(self, key: str, default: Any = None) -> Any:
        return config_manager.get(key, default)

    def update_config_setting(self, key: str, value: Any) -> bool:
        return config_manager.set(key, value)

    # ==========================================
    # DATABASE BACKUP & RESTORE
    # ==========================================

    def backup_database(self, dest_directory: str = None) -> str:
        return BackupService.create_backup(dest_directory)

    def restore_database(self, backup_filepath: str) -> bool:
        return BackupService.restore_backup(backup_filepath)
