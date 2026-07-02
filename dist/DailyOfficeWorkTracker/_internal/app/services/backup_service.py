import os
import shutil
from datetime import datetime
from app.database.connection import get_db_path, get_engine
from app.utils.logger import logger

class BackupService:
    @staticmethod
    def create_backup(dest_directory: str = None) -> str:
        """Copies the active database file to a backup destination.
        
        Returns the path of the backup file if successful, otherwise empty string.
        """
        db_file = get_db_path()
        if not os.path.exists(db_file):
            logger.warning(f"Database file does not exist to backup: {db_file}")
            return ""

        # Default to a "backups" directory in the project root if none provided
        if dest_directory is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            dest_directory = os.path.join(project_root, "backups")
        
        os.makedirs(dest_directory, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"tracker_backup_{timestamp}.db"
        dest_path = os.path.join(dest_directory, backup_filename)

        try:
            logger.info(f"Creating database backup at {dest_path}")
            # Safely copy database file
            shutil.copy2(db_file, dest_path)
            logger.info("Database backup created successfully.")
            return dest_path
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            return ""

    @staticmethod
    def restore_backup(backup_file_path: str) -> bool:
        """Restores the database from a backup file."""
        db_file = get_db_path()
        if not os.path.exists(backup_file_path):
            logger.error(f"Backup file does not exist: {backup_file_path}")
            return False

        try:
            logger.info(f"Restoring database from {backup_file_path}")
            
            # Dispose SQLAlchemy engine connections to release file locks
            engine = get_engine()
            engine.dispose()
            
            # Create a backup of the current database before overwriting, in case restore fails
            if os.path.exists(db_file):
                temp_backup = db_file + ".bak"
                shutil.copy2(db_file, temp_backup)
                logger.info(f"Temporary rollback backup created at {temp_backup}")
            else:
                temp_backup = None

            try:
                # Copy the backup file over the active DB
                shutil.copy2(backup_file_path, db_file)
                logger.info("Database restoration complete.")
                
                # If rollback file was created, delete it since restore succeeded
                if temp_backup and os.path.exists(temp_backup):
                    os.remove(temp_backup)
                return True
            except Exception as e:
                logger.error(f"Error copying backup file during restore: {e}")
                # Rollback if we saved a backup
                if temp_backup and os.path.exists(temp_backup):
                    logger.info("Restoration failed. Rolling back database file.")
                    shutil.move(temp_backup, db_file)
                return False

        except Exception as e:
            logger.error(f"Failed to restore database backup: {e}")
            return False
