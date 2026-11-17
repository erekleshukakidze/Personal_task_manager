from decorators import handle_errors, log_action
from exceptions import StorageError, ValidationError
from manager import TaskManager
from storage import JsonStorage


class TaskApp:
    """The console application: shows the menu and does what the user chooses."""

    def __init__(self, path="data/tasks.json"):
        """Create the app with a manager that saves tasks to a JSON file."""
        self.manager = TaskManager(JsonStorage(path))

    # ---------- Helpers ----------

    def read_task_id(self):
        """Ask for a task id and return it as a number."""
        text = input("Task id: ").strip()
        try:
            return int(text)
        except ValueError:
            raise ValidationError("Task id must be a whole number", field="id")

    def print_task(self, task):
        """Print one task (and its description if it has one)."""
        line = str(task)
        if task.is_overdue:
            line += "  <-- OVERDUE"
        print(line)
        if task.description:
            print(f"      {task.description}")

    def print_tasks(self, tasks, title, empty_text):
        """Print a title and the tasks. If the list is empty, print empty_text."""
        if len(tasks) == 0:
            print(empty_text)
            return
        print(f"\n{title} ({len(tasks)}):")
        for task in tasks:
            self.print_task(task)

    def print_menu(self):
        """Show the menu."""
        print("\n--- Personal Task Manager ---")
        print("1. Add task")
        print("2. Show all tasks")
        print("3. Search tasks")
        print("4. Edit task")
        print("5. Change task status")
        print("6. Delete task")
        print("7. Show tasks by project")
        print("8. Show overdue tasks")
        print("0. Save and exit")

    # ---------- Menu actions ----------
    # @handle_errors prints a friendly message if something goes wrong,
    # so the program does not crash.

    @handle_errors
    def add_task(self):
        """Ask for the task data and create the task."""
        title = input("Title: ")
        description = input("Description (optional): ")
        project = input("Project (Enter = General): ")
        deadline = input("Deadline YYYY-MM-DD (Enter = none): ").strip()
        priority = input("Priority low/medium/high (Enter = medium): ").strip()

        if deadline == "":
            deadline = None
        if priority == "":
            priority = "medium"

        task = self.manager.add_task(title, description, project, deadline, priority)
        print("Task added:")
        self.print_task(task)

    @handle_errors
    def show_all(self):
        """Print all tasks."""
        self.print_tasks(list(self.manager), "All tasks", "No tasks yet.")

    @handle_errors
    def search_tasks(self):
        """Find tasks by a word in the title or description."""
        text = input("Search text: ")
        results = self.manager.search(text)
        self.print_tasks(results, "Search results", "No tasks found.")

    @handle_errors
    def edit_task(self):
        """Change some fields of a task. Press Enter to keep a value."""
        task_id = self.read_task_id()
        task = self.manager.get_task(task_id)

        print("Current task:")
        self.print_task(task)
        print("Press Enter to keep the current value.")

        questions = [
            ("title", "New title: "),
            ("description", "New description: "),
            ("project", "New project: "),
            ("deadline", "New deadline (YYYY-MM-DD): "),
            ("priority", "New priority (low/medium/high): "),
        ]

        changes = {}
        for field, question in questions:
            value = input(question).strip()
            if value != "":
                changes[field] = value

        if len(changes) == 0:
            print("Nothing changed.")
            return

        self.manager.update_task(task_id, **changes)
        print("Task updated:")
        self.print_task(task)

    @handle_errors
    def change_status(self):
        """Change the status of a task."""
        task_id = self.read_task_id()
        status = input("New status (pending / in-progress / completed): ")
        task = self.manager.set_status(task_id, status)
        print("Status changed:")
        self.print_task(task)

    @handle_errors
    def delete_task(self):
        """Delete a task after the user confirms."""
        task_id = self.read_task_id()
        task = self.manager.get_task(task_id)  # raises an error if it does not exist

        self.print_task(task)
        answer = input("Delete this task? (y/n): ").strip().lower()
        if answer == "y":
            self.manager.delete_task(task_id)
            print("Task deleted.")
        else:
            print("Cancelled.")

    @handle_errors
    def show_by_project(self):
        """Print the tasks grouped by project."""
        groups = self.manager.group_by_project()
        if len(groups) == 0:
            print("No tasks yet.")
            return

        for project in sorted(groups):
            tasks = groups[project]
            print(f"\n== {project} ({len(tasks)}) ==")
            for task in tasks:
                self.print_task(task)

    @handle_errors
    def show_overdue(self):
        """Print the tasks whose deadline has passed."""
        tasks = self.manager.overdue_tasks()
        self.print_tasks(tasks, "Overdue tasks", "No overdue tasks.")

    # ---------- Loading and saving ----------

    @log_action
    def load_data(self):
        """Load the tasks from the JSON file (when the program starts)."""
        self.manager.load()

    @handle_errors
    @log_action
    def save_data(self):
        """Save the tasks to the JSON file (when the program closes)."""
        self.manager.save()
        print("Tasks saved.")

    # ---------- Main loop ----------

    def menu_loop(self):
        """Show the menu again and again until the user chooses 0."""
        while True:
            self.print_menu()
            choice = input("Choose: ").strip()

            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.show_all()
            elif choice == "3":
                self.search_tasks()
            elif choice == "4":
                self.edit_task()
            elif choice == "5":
                self.change_status()
            elif choice == "6":
                self.delete_task()
            elif choice == "7":
                self.show_by_project()
            elif choice == "8":
                self.show_overdue()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

    def run(self):
        """Start the program: load, show the menu, save when the program closes."""
        try:
            self.load_data()
        except StorageError as err:
            # We stop here, so we never overwrite the old file with an empty one
            print(f"Error: {err}")
            print("Fix the problem and start the program again.")
            return

        try:
            self.menu_loop()
        except (KeyboardInterrupt, EOFError):
            print("\nProgram interrupted.")
        finally:
            self.save_data()  # runs always, so the data is not lost
            print("Goodbye!")


if __name__ == "__main__":
    app = TaskApp()
    app.run()