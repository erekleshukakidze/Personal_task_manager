from datetime import date

from exceptions import TaskNotFoundError, ValidationError
from models import Task


class TaskManager:
    """Business logic: create, find, edit, delete and group tasks."""

    EDITABLE_FIELDS = ("title", "description", "project", "deadline", "priority", "status")

    def __init__(self, storage):
        """Create a manager that works with the given storage."""
        self._storage = storage
        self._tasks = {}
        self._next_id = 1

    def load(self):
        """Load all tasks from the storage."""
        tasks, next_id = self._storage.load()
        self._tasks = {task.task_id: task for task in tasks}
        self._next_id = next_id

    def save(self):
        """Save all the tasks to the storage."""
        self._storage.save(list(self._tasks.values()), self._next_id)

    def add_task(self, title, description="", project="General",
                 deadline=None, priority="medium"):
        """Create a new task. A deadline in the past is rejected."""
        task = Task(self._next_id, title, description, project, deadline, priority)
        if task.deadline is not None and task.deadline < date.today():
            raise ValidationError("Deadline cannot be in the past", field="deadline")
        self._tasks[task.task_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id):
        """Return the task or raise TaskNotFoundError."""
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def delete_task(self, task_id):
        """Delete a task and return it."""
        task = self.get_task(task_id)
        del self._tasks[task_id]
        return task

    def update_task(self, task_id, **changes):
        """Change fields of a task. If one value is invalid, nothing is changed."""
        task = self.get_task(task_id)

        # Check the field names first and remember the old values
        old_values = {}
        for field in changes:
            if field not in TaskManager.EDITABLE_FIELDS:
                raise ValidationError(f"Field '{field}' cannot be edited", field=field)
            old_values[field] = getattr(task, field)

        try:
            for field, value in changes.items():
                setattr(task, field, value)
        except ValidationError:
            # Put the old values back, so the task is not half changed
            for field, value in old_values.items():
                setattr(task, field, value)
            raise
        return task

    def set_status(self, task_id, status):
        """Change the status of a task."""
        task = self.get_task(task_id)
        task.status = status
        return task

    def search(self, text):
        """Find tasks whose title or description contains the text."""
        needle = text.strip().lower()
        if not needle:
            raise ValidationError("Search text cannot be empty", field="search")
        return [task for task in self._tasks.values()
                if needle in task.title.lower() or needle in task.description.lower()]

    def group_by_project(self):
        """Return a dict: project name -> list of tasks."""
        groups = {}
        for task in self._tasks.values():
            if task.project not in groups:
                groups[task.project] = []
            groups[task.project].append(task)
        return groups

    def overdue_tasks(self):
        """Return tasks whose deadline has passed."""
        return [task for task in self._tasks.values() if task.is_overdue]

    def __len__(self):
        """Return the number of tasks."""
        return len(self._tasks)

    def __iter__(self):
        """Iterate over all tasks."""
        return iter(self._tasks.values())