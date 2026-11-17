from datetime import date
from enum import Enum
from exceptions import ValidationError


class Priority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(Enum):
    """Task progress states."""
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


class Task:
    """A single task with validated data."""

    def __init__(self, task_id, title, description="", project="General",
                 deadline=None, priority=Priority.MEDIUM, status=Status.PENDING):
        """Create a task. Invalid data raises ValidationError."""
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValidationError("Task id must be a positive integer", field="id")
        self.__task_id = task_id
        self.title = title
        self.description = description
        self.project = project
        self.deadline = deadline
        self.priority = priority
        self.status = status

    @property
    def task_id(self):
        """Return the task id (read-only)."""
        return self.__task_id

    @property
    def title(self):
        """Return the title."""
        return self.__title

    @title.setter
    def title(self, value):
        """Set the title; it must be non-empty text."""
        if not isinstance(value, str):
            raise ValidationError("Title must be text", field="title")
        value = value.strip()
        if not value:
            raise ValidationError("Title cannot be empty", field="title")
        self.__title = value

    @property
    def description(self):
        """Return the description."""
        return self.__description

    @description.setter
    def description(self, value):
        """Set the description; it may be empty."""
        if not isinstance(value, str):
            raise ValidationError("Description must be text", field="description")
        self.__description = value.strip()

    @property
    def project(self):
        """Return the project name."""
        return self.__project

    @project.setter
    def project(self, value):
        """Set the project; an empty value becomes 'General'."""
        if not isinstance(value, str):
            raise ValidationError("Project must be text", field="project")
        value = value.strip()
        if not value:
            value = "General"
        self.__project = value

    @property
    def deadline(self):
        """Return the deadline or None."""
        return self.__deadline

    @deadline.setter
    def deadline(self, value):
        """Accept None, a date, or 'YYYY-MM-DD' text."""
        if value is None or isinstance(value, date):
            self.__deadline = value
        elif isinstance(value, str):
            try:
                self.__deadline = date.fromisoformat(value.strip())
            except ValueError:
                raise ValidationError("Deadline must be in YYYY-MM-DD format", field="deadline")
        else:
            raise ValidationError("Deadline must be in YYYY-MM-DD format", field="deadline")

    @property
    def priority(self):
        """Return the priority (a Priority member)."""
        return self.__priority

    @priority.setter
    def priority(self, value):
        """Accept a Priority or its text ('low', 'medium', 'high')."""
        if isinstance(value, str):
            value = value.strip().lower()
        try:
            self.__priority = Priority(value)  # Priority(Priority.LOW) also works
        except ValueError:
            raise ValidationError("Priority must be low, medium or high", field="priority")

    @property
    def status(self):
        """Return the status (a Status member)."""
        return self.__status

    @status.setter
    def status(self, value):
        """Accept a Status or its text ('pending', 'in-progress', 'completed')."""
        if isinstance(value, str):
            value = value.strip().lower()
        try:
            self.__status = Status(value)
        except ValueError:
            raise ValidationError("Status must be pending, in-progress or completed", field="status")

    @property
    def is_overdue(self):
        """True if the deadline has passed and the task is not completed."""
        if self.deadline is None:
            return False
        if self.status == Status.COMPLETED:
            return False
        return self.deadline < date.today()

    def to_dict(self):
        """Return a JSON-friendly dictionary."""
        if self.deadline is None:
            deadline_text = None
        else:
            deadline_text = self.deadline.isoformat()

        return {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "project": self.project,
            "deadline": deadline_text,
            "priority": self.priority.value,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Task from a dictionary made by to_dict."""
        if not isinstance(data, dict):
            raise ValidationError("Saved task must be an object")
        if "id" not in data or "title" not in data:
            raise ValidationError("Saved task must have an id and a title")

        return cls(
            data["id"],
            data["title"],
            description=data.get("description", ""),
            project=data.get("project", "General"),
            deadline=data.get("deadline"),
            priority=data.get("priority", "medium"),
            status=data.get("status", "pending"),
        )

    def __str__(self):
        """Human-readable description."""
        if self.deadline is None:
            due = "-"
        else:
            due = self.deadline.isoformat()
        return f"#{self.task_id} {self.title} [{self.project}] | {self.priority.value} | {self.status.value} | due {due}"

    def __repr__(self):
        """Developer-friendly description."""
        return f"Task({self.task_id}, {self.title!r})"