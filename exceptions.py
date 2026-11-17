class TaskManagerError(Exception):
    """Base class for all Task Manager errors."""


class ValidationError(TaskManagerError):
    """Raised when user data is invalid."""
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field


    def __str__(self):
        if self.field:
            return f"[{self.field}] {super().__str__()}"
        return super().__str__()


class TaskNotFoundError(TaskManagerError):
    """Raised when no task has the given id."""

    def __init__(self, task_id):
        super().__init__(f"Task with id {task_id} not found")
        self.task_id = task_id


class StorageError(TaskManagerError):
    """Raised when reading or writing the data file fails."""
    def __init__(self,message, path=None):
        super().__init__(message)
        self.path = path


    def __str__(self):
        if self.path:
            return f"{super().__str__()} (file: {self.__str__})"
        return super().__str__()



if __name__ == "__main__":
    
    try:
        raise TaskNotFoundError(5)
    except TaskManagerError as err:       
        print("Caught:", err)
        print("id:", err.task_id)

    print(issubclass(ValidationError, TaskManagerError))
    print(isinstance(TaskNotFoundError(1), Exception))

    for error_class in (ValidationError, StorageError):
        try:
            raise error_class("something went wrong")
        except TaskManagerError as err:
            print(type(err).__name__, "->", err)

    
    try:
        raise TaskNotFoundError(7)
    except TaskNotFoundError as err:
        print("specific:", err)
    except TaskManagerError as err:
        print("general:", err)

    
    try:
        raise ValidationError("Title cannot be empty", field="title")
    except TaskManagerError as err:
        print(err)            
        print(err.field)       

    try:
        raise StorageError("Cannot read data file", path="data/tasks.json")
    except TaskManagerError as err:
        print(err)   