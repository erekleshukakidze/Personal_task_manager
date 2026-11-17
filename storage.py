import json
import os
from abc import ABC, abstractmethod

from decorators import retry
from exceptions import StorageError, ValidationError
from models import Task


class BaseStorage(ABC):
    """Contract for every storage backend."""

    @abstractmethod
    def load(self):
        """Return a tuple (list of Task, next_id)."""

    @abstractmethod
    def save(self, tasks, next_id):
        """Store the tasks and the next free id."""


class JsonStorage(BaseStorage):
    """Keeps tasks in a JSON file."""

    def __init__(self, path="data/tasks.json"):
        self.path = path

    @retry(times=3, delay=0.5)
    def _write(self, text):
        """Write text to the data file safely (temp file, then replace)."""
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        temp_path = self.path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(temp_path, self.path)

    def save(self, tasks, next_id):
        """Write all tasks to the JSON file."""
        data = {
            "next_id": next_id,
            "tasks": [task.to_dict() for task in tasks],
        }
        text = json.dumps(data, indent=2, ensure_ascii=False)
        try:
            self._write(text)
        except OSError as err:
            raise StorageError(f"Cannot save data: {err}", path=self.path)

    @retry(times=3, delay=0.5)
    def _read(self):
        """Return the file content as text."""
        with open(self.path, encoding="utf-8") as f:
            return f.read()

    def load(self):
        """Return (tasks, next_id). A missing file means a fresh start."""
        if not os.path.exists(self.path):
            return [], 1

        try:
            text = self._read()
        except OSError as err:
            raise StorageError(f"Cannot read data: {err}", path=self.path)

        try:
            data = json.loads(text)
            tasks = [Task.from_dict(item) for item in data["tasks"]]
            next_id = data["next_id"]
            if not isinstance(next_id, int) or next_id < 1:
                raise ValueError("next_id must be a positive integer")
        except (ValueError, KeyError, TypeError, ValidationError):
            backup = self.path + ".corrupt"
            os.replace(self.path, backup)
            raise StorageError(f"Data file is damaged; a copy was kept as {backup}",
                               path=self.path)

        return tasks, next_id