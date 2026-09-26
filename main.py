from datetime import date, timedelta
from enum import StrEnum


class TaskStatus(StrEnum):
    planned = "planned"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


def is_overdue(due_date: date | None, status: TaskStatus) -> bool:
    if due_date is None:
        return False
    if status == TaskStatus.done:
        return False
    return due_date < date.today()


def next_status(current: TaskStatus) -> TaskStatus:
    match current:
        case TaskStatus.planned:
            return TaskStatus.in_progress
        case TaskStatus.in_progress:
            return TaskStatus.done
        case TaskStatus.done | TaskStatus.blocked:
            return current


if __name__ == "__main__":
    yesterday = date.today() - timedelta(days=1)

    print(is_overdue(None, TaskStatus.planned))  # False
    print(is_overdue(yesterday, TaskStatus.done))  # False
    print(is_overdue(yesterday, TaskStatus.in_progress))  # True

    print(next_status(TaskStatus.planned))  # TaskStatus.in_progress
    print(next_status(TaskStatus.in_progress))  # TaskStatus.done
    print(next_status(TaskStatus.done))  # TaskStatus.done
    print(next_status(TaskStatus.blocked))  # TaskStatus.blocked
