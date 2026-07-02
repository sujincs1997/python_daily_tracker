import os
import uuid
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.connection import get_db_session
from app.models.project import Project
from app.models.category import Category
from app.models.assigned_by import AssignedBy
from app.models.task import Task
from app.utils.logger import logger

# ReportLab Imports
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class ImportExportService:
    
    # ==========================================
    # IMPORT FUNCTIONALITY
    # ==========================================
    
    @staticmethod
    def import_projects_from_excel(filepath: str) -> int:
        """Imports projects from an Excel sheet.
        
        Expected columns: 'project_name', 'description', 'active'
        """
        if not os.path.exists(filepath):
            logger.error(f"Excel file not found for project import: {filepath}")
            return 0
        
        try:
            df = pd.read_excel(filepath)
            # Normalize column names
            df.columns = [col.strip().lower() for col in df.columns]
            
            required_cols = {"project_name"}
            if not required_cols.issubset(df.columns):
                logger.error(f"Excel file missing required columns: {required_cols - set(df.columns)}")
                return 0
            
            imported_count = 0
            with get_db_session() as session:
                for _, row in df.iterrows():
                    name = str(row["project_name"]).strip()
                    desc = str(row.get("description", "")).strip() if pd.notna(row.get("description", "")) else ""
                    active = bool(row.get("active", True)) if pd.notna(row.get("active", True)) else True
                    
                    if not name:
                        continue
                        
                    existing = session.query(Project).filter_by(project_name=name).first()
                    if not existing:
                        proj = Project(project_name=name, description=desc, active=active)
                        session.add(proj)
                        imported_count += 1
                session.commit()
            
            logger.info(f"Successfully imported {imported_count} projects.")
            return imported_count
        except Exception as e:
            logger.error(f"Error importing projects from Excel: {e}")
            return 0

    @staticmethod
    def import_categories_from_excel(filepath: str) -> int:
        """Imports categories from an Excel sheet.
        
        Expected columns: 'category_name'
        """
        if not os.path.exists(filepath):
            logger.error(f"Excel file not found for category import: {filepath}")
            return 0
            
        try:
            df = pd.read_excel(filepath)
            df.columns = [col.strip().lower() for col in df.columns]
            
            if "category_name" not in df.columns:
                logger.error("Excel file missing required column: 'category_name'")
                return 0
                
            imported_count = 0
            with get_db_session() as session:
                for _, row in df.iterrows():
                    name = str(row["category_name"]).strip()
                    if not name:
                        continue
                        
                    existing = session.query(Category).filter_by(category_name=name).first()
                    if not existing:
                        cat = Category(category_name=name)
                        session.add(cat)
                        imported_count += 1
                session.commit()
                
            logger.info(f"Successfully imported {imported_count} categories.")
            return imported_count
        except Exception as e:
            logger.error(f"Error importing categories from Excel: {e}")
            return 0

    @staticmethod
    def import_assigned_by_from_excel(filepath: str) -> int:
        """Imports 'Assigned By' list from an Excel sheet.
        
        Expected columns: 'person_name', 'designation'
        """
        if not os.path.exists(filepath):
            logger.error(f"Excel file not found for Assigned By import: {filepath}")
            return 0
            
        try:
            df = pd.read_excel(filepath)
            df.columns = [col.strip().lower() for col in df.columns]
            
            if "person_name" not in df.columns:
                logger.error("Excel file missing required column: 'person_name'")
                return 0
                
            imported_count = 0
            with get_db_session() as session:
                for _, row in df.iterrows():
                    name = str(row["person_name"]).strip()
                    desg = str(row.get("designation", "")).strip() if pd.notna(row.get("designation", "")) else ""
                    if not name:
                        continue
                        
                    existing = session.query(AssignedBy).filter(
                        AssignedBy.person_name == name,
                        AssignedBy.designation == desg
                    ).first()
                    
                    if not existing:
                        ab = AssignedBy(person_name=name, designation=desg)
                        session.add(ab)
                        imported_count += 1
                session.commit()
                
            logger.info(f"Successfully imported {imported_count} Assigned By entries.")
            return imported_count
        except Exception as e:
            logger.error(f"Error importing Assigned By from Excel: {e}")
            return 0

    @staticmethod
    def import_tasks_from_file(filepath: str) -> int:
        """Imports tasks from CSV or Excel file.
        
        Creates missing projects, categories, and assigned-by profiles on the fly if needed.
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found for task import: {filepath}")
            return 0

        # Load file
        try:
            if filepath.endswith((".xlsx", ".xls")):
                df = pd.read_excel(filepath)
            else:
                df = pd.read_csv(filepath)
            
            # Normalize column mapping
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
            
            # Identify essential fields
            # Check required base columns (task name/title, project, category, assigned_by)
            required = {"title", "project", "category", "assigned_by"}
            normalized_cols = set(df.columns)
            
            # Fallbacks for header naming variations
            column_mappings = {
                "task_name": "title",
                "task_title": "title",
                "project_name": "project",
                "category_name": "category",
                "person_name": "assigned_by",
            }
            
            for key, val in column_mappings.items():
                if key in normalized_cols and val not in normalized_cols:
                    df.rename(columns={key: val}, inplace=True)
            
            # Recheck
            if not {"title", "project", "category", "assigned_by"}.issubset(df.columns):
                logger.error(f"Import file missing required fields. Map titles: 'title', 'project', 'category', 'assigned_by'. Current: {list(df.columns)}")
                return 0

            imported_count = 0
            
            with get_db_session() as session:
                # Cache existing entities to minimize database lookups
                project_cache = {p.project_name.lower(): p.id for p in session.query(Project).all()}
                category_cache = {c.category_name.lower(): c.id for c in session.query(Category).all()}
                assigned_cache = {a.person_name.lower(): a.id for a in session.query(AssignedBy).all()}
                
                # Fetch maximum existing task counter for generating sequential task numbers
                all_tasks = session.query(Task).all()
                next_task_num = len(all_tasks) + 1

                for _, row in df.iterrows():
                    title = str(row["title"]).strip()
                    if not title or pd.isna(row["title"]):
                        continue
                    
                    # 1. Resolve Project
                    proj_name = str(row["project"]).strip()
                    if proj_name.lower() not in project_cache:
                        new_proj = Project(project_name=proj_name, description="Auto-created during task import", active=True)
                        session.add(new_proj)
                        session.flush()  # populate ID
                        project_cache[proj_name.lower()] = new_proj.id
                    proj_id = project_cache[proj_name.lower()]
                    
                    # 2. Resolve Category
                    cat_name = str(row["category"]).strip()
                    if cat_name.lower() not in category_cache:
                        new_cat = Category(category_name=cat_name)
                        session.add(new_cat)
                        session.flush()
                        category_cache[cat_name.lower()] = new_cat.id
                    cat_id = category_cache[cat_name.lower()]
                    
                    # 3. Resolve Assigned By
                    ab_name = str(row["assigned_by"]).strip()
                    if ab_name.lower() not in assigned_cache:
                        new_ab = AssignedBy(person_name=ab_name, designation="Auto-created")
                        session.add(new_ab)
                        session.flush()
                        assigned_cache[ab_name.lower()] = new_ab.id
                    ab_id = assigned_cache[ab_name.lower()]
                    
                    # Optional columns mappings
                    task_uuid = str(row.get("uuid", uuid.uuid4()))
                    task_num = str(row.get("task_number", f"TASK-{next_task_num:04d}"))
                    desc = str(row.get("description", "")) if pd.notna(row.get("description", "")) else ""
                    priority = str(row.get("priority", "Medium")).strip().capitalize()
                    status = str(row.get("status", "Not Started")).strip()
                    completion = int(row.get("completion", 0)) if pd.notna(row.get("completion", 0)) else 0
                    remarks = str(row.get("remarks", "")) if pd.notna(row.get("remarks", "")) else ""
                    
                    # Parse start_time, end_time, duration
                    duration = int(row.get("duration", 0)) if pd.notna(row.get("duration", 0)) else 0
                    
                    def parse_dt(val):
                        if pd.isna(val) or not str(val).strip():
                            return None
                        try:
                            return pd.to_datetime(val).to_pydatetime()
                        except Exception:
                            return None
                            
                    start_time = parse_dt(row.get("start_time"))
                    end_time = parse_dt(row.get("end_time"))
                    
                    # Check task uniqueness by UUID
                    existing_task = session.query(Task).filter((Task.uuid == task_uuid) | (Task.task_number == task_num)).first()
                    if existing_task:
                        # Skip or update. Let's update stats
                        existing_task.title = title
                        existing_task.description = desc
                        existing_task.project_id = proj_id
                        existing_task.category_id = cat_id
                        existing_task.assigned_by_id = ab_id
                        existing_task.priority = priority
                        existing_task.status = status
                        existing_task.completion = completion
                        existing_task.start_time = start_time
                        existing_task.end_time = end_time
                        existing_task.duration = duration
                        existing_task.remarks = remarks
                    else:
                        task = Task(
                            uuid=task_uuid,
                            task_number=task_num,
                            title=title,
                            description=desc,
                            project_id=proj_id,
                            category_id=cat_id,
                            assigned_by_id=ab_id,
                            priority=priority,
                            status=status,
                            completion=completion,
                            start_time=start_time,
                            end_time=end_time,
                            duration=duration,
                            remarks=remarks
                        )
                        session.add(task)
                        next_task_num += 1
                        imported_count += 1
                        
                session.commit()
            logger.info(f"Imported {imported_count} new tasks and synced updates.")
            return imported_count
        except Exception as e:
            logger.error(f"Error importing tasks from file: {e}")
            return 0


    # ==========================================
    # EXPORT FUNCTIONALITY
    # ==========================================

    @staticmethod
    def export_to_csv(df: pd.DataFrame, filepath: str) -> bool:
        """Exports a pandas DataFrame to a CSV file."""
        try:
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
            logger.info(f"CSV exported successfully to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return False

    @staticmethod
    def export_to_excel(df: pd.DataFrame, filepath: str, sheet_name: str = "Productivity Report") -> bool:
        """Exports a pandas DataFrame to an Excel spreadsheet."""
        try:
            # Using openpyxl as engine
            with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            logger.info(f"Excel exported successfully to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting Excel: {e}")
            return False

    @staticmethod
    def export_to_pdf(headers: list, data: list, title: str, subtitle: str, filepath: str) -> bool:
        """Exports report dataset to a structured PDF document.
        
        Using ReportLab Platypus tables for professional rendering.
        """
        try:
            # We will use landscape layout if columns list is wide (e.g. > 5 columns)
            use_landscape = len(headers) > 5
            pagesize = landscape(letter) if use_landscape else letter
            
            doc = SimpleDocTemplate(
                filepath, 
                pagesize=pagesize,
                rightMargin=36, leftMargin=36, topMargin=40, bottomMargin=40
            )
            
            styles = getSampleStyleSheet()
            
            # Custom stylesheet settings
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor('#1A365D'), # Navy accent
                alignment=TA_LEFT,
                spaceAfter=6
            )
            
            subtitle_style = ParagraphStyle(
                'ReportSubtitle',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#4A5568'), # Charcoal
                alignment=TA_LEFT,
                spaceAfter=15
            )
            
            cell_header_style = ParagraphStyle(
                'TableHeader',
                parent=styles['Normal'],
                fontSize=9,
                leading=11,
                fontName='Helvetica-Bold',
                textColor=colors.white,
                alignment=TA_LEFT
            )
            
            cell_body_style = ParagraphStyle(
                'TableBody',
                parent=styles['Normal'],
                fontSize=8,
                leading=10,
                textColor=colors.HexColor('#2D3748')
            )
            
            story = []
            
            # Add Title & Header Info
            story.append(Paragraph(title, title_style))
            story.append(Paragraph(f"{subtitle} | Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
            story.append(Spacer(1, 10))
            
            # Format Table Data: wrap headers and cells in Paragraphs to support auto-wrapping
            formatted_data = []
            
            # Add Headers row
            header_row = [Paragraph(str(h), cell_header_style) for h in headers]
            formatted_data.append(header_row)
            
            # Add data rows
            for row in data:
                formatted_row = [Paragraph(str(val) if val is not None else "", cell_body_style) for val in row]
                formatted_data.append(formatted_row)
            
            # Determine column widths automatically based on page size
            avail_width = doc.width
            col_width = avail_width / len(headers)
            col_widths = [col_width] * len(headers)
            
            # Construct ReportLab Table
            table = Table(formatted_data, colWidths=col_widths, repeatRows=1)
            
            # Apply Table Styling
            t_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B6CB0')), # Teal/Blue header background
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')), # Slate borders
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]), # Zebra striping
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ])
            table.setStyle(t_style)
            
            story.append(table)
            doc.build(story)
            logger.info(f"PDF exported successfully to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting PDF: {e}", exc_info=True)
            return False
