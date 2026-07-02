import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import or_, and_, func
from app.database.connection import get_db_session
from app.models.task import Task
from app.models.project import Project
from app.models.category import Category
from app.models.assigned_by import AssignedBy
from app.utils.config import config_manager
from app.utils.logger import logger

class TaskController:
    def __init__(self):
        pass

    def get_next_task_number(self) -> str:
        """Generates the next task number sequentially (e.g., TASK-0001)."""
        try:
            with get_db_session() as session:
                # Count total tasks in DB
                count = session.query(Task).count()
                return f"TASK-{count + 1:04d}"
        except Exception as e:
            logger.error(f"Error generating task number: {e}")
            return "TASK-0001"

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves details of a single task by ID."""
        try:
            with get_db_session() as session:
                task = session.query(Task).get(task_id)
                if not task:
                    return None
                return self._serialize_task(task)
        except Exception as e:
            logger.error(f"Error fetching task details: {e}")
            return None

    def get_task_by_uuid(self, task_uuid: str) -> Optional[Dict[str, Any]]:
        """Retrieves details of a single task by UUID."""
        try:
            with get_db_session() as session:
                task = session.query(Task).filter_by(uuid=task_uuid).first()
                if not task:
                    return None
                return self._serialize_task(task)
        except Exception as e:
            logger.error(f"Error fetching task details by UUID: {e}")
            return None

    def create_task(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Creates and saves a new task in the database."""
        try:
            with get_db_session() as session:
                new_uuid = data.get("uuid") or str(uuid.uuid4())
                new_number = data.get("task_number") or self.get_next_task_number()
                
                # Check duplicate UUID or task number
                existing = session.query(Task).filter(
                    (Task.uuid == new_uuid) | (Task.task_number == new_number)
                ).first()
                if existing:
                    logger.warning(f"Task already exists with UUID {new_uuid} or Number {new_number}.")
                    return None

                task = Task(
                    uuid=new_uuid,
                    task_number=new_number,
                    title=data["title"],
                    description=data.get("description", ""),
                    project_id=data["project_id"],
                    category_id=data["category_id"],
                    assigned_by_id=data["assigned_by_id"],
                    priority=data.get("priority", "Medium"),
                    status=data.get("status", "Not Started"),
                    completion=data.get("completion", 0),
                    start_time=data.get("start_time"),
                    end_time=data.get("end_time"),
                    duration=data.get("duration", 0),
                    remarks=data.get("remarks", "")
                )
                session.add(task)
                session.commit()
                # Refresh task to serialize relations properly
                session.refresh(task)
                logger.info(f"Task '{task.title}' created successfully as {task.task_number}.")
                return self._serialize_task(task)
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None

    def update_task(self, task_id: int, data: Dict[str, Any]) -> bool:
        """Updates fields of an existing task."""
        try:
            with get_db_session() as session:
                task = session.query(Task).get(task_id)
                if not task:
                    logger.error(f"Task with ID {task_id} not found.")
                    return False

                # Update fields
                if "title" in data: task.title = data["title"]
                if "description" in data: task.description = data["description"]
                if "project_id" in data: task.project_id = data["project_id"]
                if "category_id" in data: task.category_id = data["category_id"]
                if "assigned_by_id" in data: task.assigned_by_id = data["assigned_by_id"]
                if "priority" in data: task.priority = data["priority"]
                if "status" in data: task.status = data["status"]
                if "completion" in data: task.completion = data["completion"]
                if "start_time" in data: task.start_time = data["start_time"]
                if "end_time" in data: task.end_time = data["end_time"]
                if "duration" in data: task.duration = data["duration"]
                if "remarks" in data: task.remarks = data["remarks"]
                
                task.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Task ID {task_id} updated successfully.")
                return True
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False

    def delete_task(self, task_id: int) -> bool:
        """Deletes a task from the database."""
        try:
            with get_db_session() as session:
                task = session.query(Task).get(task_id)
                if not task:
                    return False
                session.delete(task)
                session.commit()
                logger.info(f"Task ID {task_id} deleted successfully.")
                
                # Clean up favorites config
                favs = config_manager.get("favorite_task_ids", [])
                if task_id in favs:
                    favs.remove(task_id)
                    config_manager.set("favorite_task_ids", favs)
                    
                return True
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False

    def duplicate_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Duplicates a task, auto-generating a new UUID and Task Number."""
        try:
            with get_db_session() as session:
                original = session.query(Task).get(task_id)
                if not original:
                    logger.error(f"Original task {task_id} not found for duplication.")
                    return None
                
                new_data = {
                    "uuid": str(uuid.uuid4()),
                    "task_number": self.get_next_task_number(),
                    "title": f"Copy of {original.title}",
                    "description": original.description,
                    "project_id": original.project_id,
                    "category_id": original.category_id,
                    "assigned_by_id": original.assigned_by_id,
                    "priority": original.priority,
                    "status": "Not Started",
                    "completion": 0,
                    "duration": 0,
                    "remarks": original.remarks
                }
                return self.create_task(new_data)
        except Exception as e:
            logger.error(f"Error duplicating task: {e}")
            return None

    # ==========================================
    # FAVORITES MANAGEMENT
    # ==========================================

    def toggle_favorite(self, task_id: int) -> bool:
        """Toggles the favorite state of a task in the configurations file."""
        favs = config_manager.get("favorite_task_ids", [])
        if task_id in favs:
            favs.remove(task_id)
            status = False
        else:
            favs.append(task_id)
            status = True
        config_manager.set("favorite_task_ids", favs)
        return status

    def is_favorite(self, task_id: int) -> bool:
        """Checks if a task is favorited."""
        return task_id in config_manager.get("favorite_task_ids", [])

    def get_favorite_tasks(self) -> List[Dict[str, Any]]:
        """Retrieves list of all favorited tasks."""
        fav_ids = config_manager.get("favorite_task_ids", [])
        if not fav_ids:
            return []
            
        try:
            with get_db_session() as session:
                tasks = session.query(Task).filter(Task.id.in_(fav_ids)).all()
                return [self._serialize_task(t) for t in tasks]
        except Exception as e:
            logger.error(f"Error fetching favorite tasks: {e}")
            return []

    # ==========================================
    # QUERIES, SEARCH & FILTERS
    # ==========================================

    def get_recent_tasks(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves tasks sorted by updated_at time descending."""
        try:
            with get_db_session() as session:
                tasks = session.query(Task).order_by(Task.updated_at.desc()).limit(limit).all()
                return [self._serialize_task(t) for t in tasks]
        except Exception as e:
            logger.error(f"Error fetching recent tasks: {e}")
            return []

    def search_and_filter_tasks(self, filters: Dict[str, Any], search_query: str = "") -> List[Dict[str, Any]]:
        """Retrieves tasks using search query matching and dropdown/date filters."""
        try:
            with get_db_session() as session:
                query = session.query(Task).join(Project).join(Category).join(AssignedBy)
                
                # 1. Apply Search Query (checks UUID, Title, Project, Category, Assigned By, Remarks)
                if search_query:
                    q = f"%{search_query}%"
                    query = query.filter(
                        or_(
                            Task.uuid.like(q),
                            Task.task_number.like(q),
                            Task.title.like(q),
                            Task.remarks.like(q),
                            Project.project_name.like(q),
                            Category.category_name.like(q),
                            AssignedBy.person_name.like(q)
                        )
                    )
                
                # 2. Dropdown Filters
                if filters.get("project_id"):
                    query = query.filter(Task.project_id == filters["project_id"])
                if filters.get("category_id"):
                    query = query.filter(Task.category_id == filters["category_id"])
                if filters.get("assigned_by_id"):
                    query = query.filter(Task.assigned_by_id == filters["assigned_by_id"])
                if filters.get("priority"):
                    query = query.filter(Task.priority == filters["priority"])
                if filters.get("status"):
                    query = query.filter(Task.status == filters["status"])

                # 3. Date Filters
                date_filter = filters.get("date_filter") # Today, Yesterday, Last 7 Days, Current Month, Custom
                now = datetime.now()
                today_start = datetime.combine(now.date(), datetime.min.time())
                
                if date_filter == "Today":
                    query = query.filter(Task.created_at >= today_start)
                elif date_filter == "Yesterday":
                    yesterday_start = today_start - timedelta(days=1)
                    query = query.filter(
                        and_(
                            Task.created_at >= yesterday_start,
                            Task.created_at < today_start
                        )
                    )
                elif date_filter == "Last 7 Days":
                    seven_days_ago = today_start - timedelta(days=7)
                    query = query.filter(Task.created_at >= seven_days_ago)
                elif date_filter == "Current Month":
                    month_start = datetime(now.year, now.month, 1)
                    query = query.filter(Task.created_at >= month_start)
                
                tasks = query.order_by(Task.created_at.desc()).all()
                return [self._serialize_task(t) for t in tasks]
        except Exception as e:
            logger.error(f"Error filtering tasks: {e}")
            return []

    # ==========================================
    # STATISTICS & DASHBOARD COMPUTATION
    # ==========================================

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Calculates and compiles aggregated statistics for the dashboard view."""
        stats = {
            "today_hours": 0.0,
            "today_tasks": 0,
            "current_task": "None",
            "current_task_uuid": "",
            "current_task_duration": 0,
            "current_task_id": None,
            "avg_duration": "00:00:00",
            "longest_task": "None",
            "longest_task_time": "00:00:00",
            "shortest_task": "None",
            "shortest_task_time": "00:00:00",
            "most_used_category": "None",
            "most_used_project": "None",
            "weekly_hours": 0.0,
            "monthly_hours": 0.0,
            "total_tasks_today": 0,
            "completed_tasks_today": 0,
            "pending_tasks_today": 0,
            "completion_percentage": 0.0
        }
        
        now = datetime.now()
        today_start = datetime.combine(now.date(), datetime.min.time())
        week_start = today_start - timedelta(days=now.weekday()) # Monday start
        month_start = datetime(now.year, now.month, 1)

        try:
            with get_db_session() as session:
                # 1. Current Task (In Progress)
                current = session.query(Task).filter_by(status="In Progress").order_by(Task.updated_at.desc()).first()
                if current:
                    stats["current_task"] = current.title
                    stats["current_task_uuid"] = current.uuid
                    stats["current_task_id"] = current.id
                    stats["current_task_duration"] = current.duration

                # 2. Today's metrics
                today_tasks_query = session.query(Task).filter(Task.created_at >= today_start)
                stats["total_tasks_today"] = today_tasks_query.count()
                stats["today_tasks"] = stats["total_tasks_today"]
                stats["completed_tasks_today"] = today_tasks_query.filter_by(status="Completed").count()
                stats["pending_tasks_today"] = today_tasks_query.filter(
                    Task.status.in_(["Not Started", "In Progress", "Paused"])
                ).count()
                
                # Daily completion percentage
                if stats["total_tasks_today"] > 0:
                    completions = [t.completion for t in today_tasks_query.all()]
                    stats["completion_percentage"] = sum(completions) / stats["total_tasks_today"]
                else:
                    stats["completion_percentage"] = 0.0

                # Today's hours: Sum durations of tasks touched today (in seconds)
                today_seconds = session.query(func.sum(Task.duration)).filter(Task.created_at >= today_start).scalar() or 0
                stats["today_hours"] = round(today_seconds / 3600.0, 2)

                # Weekly and Monthly hours (Monday-based)
                weekly_seconds = session.query(func.sum(Task.duration)).filter(Task.created_at >= week_start).scalar() or 0
                stats["weekly_hours"] = round(weekly_seconds / 3600.0, 2)

                monthly_seconds = session.query(func.sum(Task.duration)).filter(Task.created_at >= month_start).scalar() or 0
                stats["monthly_hours"] = round(monthly_seconds / 3600.0, 2)

                # Average task duration (all tasks with duration > 0)
                all_valid_durations = session.query(Task.duration).filter(Task.duration > 0).all()
                if all_valid_durations:
                    avg_secs = int(sum([d[0] for d in all_valid_durations]) / len(all_valid_durations))
                    stats["avg_duration"] = self._format_duration(avg_secs)
                
                # Longest task (all time)
                longest = session.query(Task).filter(Task.duration > 0).order_by(Task.duration.desc()).first()
                if longest:
                    stats["longest_task"] = longest.title
                    stats["longest_task_time"] = self._format_duration(longest.duration)
                
                # Shortest task (all time, with duration > 0)
                shortest = session.query(Task).filter(Task.duration > 0).order_by(Task.duration.asc()).first()
                if shortest:
                    stats["shortest_task"] = shortest.title
                    stats["shortest_task_time"] = self._format_duration(shortest.duration)
                
                # Most Used Category
                cat_usage = session.query(Task.category_id, func.count(Task.id)).group_by(Task.category_id).order_by(func.count(Task.id).desc()).first()
                if cat_usage:
                    cat = session.query(Category).get(cat_usage[0])
                    if cat:
                        stats["most_used_category"] = cat.category_name

                # Most Used Project
                proj_usage = session.query(Task.project_id, func.count(Task.id)).group_by(Task.project_id).order_by(func.count(Task.id).desc()).first()
                if proj_usage:
                    proj = session.query(Project).get(proj_usage[0])
                    if proj:
                        stats["most_used_project"] = proj.project_name

        except Exception as e:
            logger.error(f"Error calculating dashboard stats: {e}")
            
        return stats

    def get_weekly_productivity_data(self) -> Dict[str, float]:
        """Returns work hours logged per day for the last 7 calendar days (ending today)."""
        data = {}
        now = datetime.now()
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_name = day.strftime("%a")  # e.g., Mon, Tue
            day_start = datetime.combine(day.date(), datetime.min.time())
            day_end = datetime.combine(day.date(), datetime.max.time())
            
            try:
                with get_db_session() as session:
                    seconds = session.query(func.sum(Task.duration)).filter(
                        and_(Task.created_at >= day_start, Task.created_at <= day_end)
                    ).scalar() or 0
                    data[day_name] = round(seconds / 3600.0, 2)
            except Exception as e:
                logger.error(f"Error fetching productivity for {day_name}: {e}")
                data[day_name] = 0.0
        return data

    def get_category_distribution_data(self) -> Dict[str, float]:
        """Returns category distribution based on total time spent (in hours)."""
        data = {}
        try:
            with get_db_session() as session:
                results = session.query(
                    Category.category_name, 
                    func.sum(Task.duration)
                ).join(Task).group_by(Category.category_name).all()
                
                for cat_name, duration_secs in results:
                    if duration_secs and duration_secs > 0:
                        data[cat_name] = round(duration_secs / 3600.0, 2)
        except Exception as e:
            logger.error(f"Error fetching category distribution: {e}")
        return data

    def get_project_hours_data(self) -> Dict[str, float]:
        """Returns total hours spent per project."""
        data = {}
        try:
            with get_db_session() as session:
                results = session.query(
                    Project.project_name, 
                    func.sum(Task.duration)
                ).join(Task).group_by(Project.project_name).all()
                
                for proj_name, duration_secs in results:
                    if duration_secs and duration_secs > 0:
                        data[proj_name] = round(duration_secs / 3600.0, 2)
        except Exception as e:
            logger.error(f"Error fetching project hours: {e}")
        return data

    # ==========================================
    # HELPER SERIALIZERS
    # ==========================================

    def _serialize_task(self, task: Task) -> Dict[str, Any]:
        """Translates SQLAlchemy Task objects into dictionary outputs."""
        return {
            "id": task.id,
            "uuid": task.uuid,
            "task_number": task.task_number,
            "title": task.title,
            "description": task.description,
            "project_id": task.project_id,
            "project_name": task.project.project_name if task.project else "Unknown",
            "category_id": task.category_id,
            "category_name": task.category.category_name if task.category else "Unknown",
            "assigned_by_id": task.assigned_by_id,
            "assigned_by_name": task.assigned_by.person_name if task.assigned_by else "Unknown",
            "priority": task.priority,
            "status": task.status,
            "completion": task.completion,
            "start_time": task.start_time.strftime("%Y-%m-%d %H:%M:%S") if task.start_time else "",
            "end_time": task.end_time.strftime("%Y-%m-%d %H:%M:%S") if task.end_time else "",
            "duration": task.duration,
            "duration_formatted": self._format_duration(task.duration),
            "remarks": task.remarks,
            "created_date": task.created_at.strftime("%Y-%m-%d"),
            "created_time": task.created_at.strftime("%H:%M:%S"),
            "updated_at": task.updated_at
        }

    def _format_duration(self, seconds: int) -> str:
        """Helper to format duration in seconds to 00:00:00 format."""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
