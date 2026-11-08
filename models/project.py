"""Project model and project-task relationships."""

from dataclasses import dataclass, field


@dataclass
class Project:
  """A project owned by a user and containing tasks."""

  id: int
  title: str
  owner_id: int
  description: str = "" # optional description 
  due_date: str = "" # optional due date
  task_ids: list[int] = field(default_factory=list)

  def __post_init__(self):
    self.title = self.title.strip()
    self.description = self.description.strip()

    if not self.title:
      raise ValueError("Project title cannot be empty.")

  @property
  def task_count(self):
    """Return the number of tasks in this project."""
    return len(self.task_ids)

  def add_task(self, task_id):
    """Associate a task with this project."""
    if task_id not in self.task_ids:
      self.task_ids.append(task_id)

  def __str__(self):
    return (
      f"[{self.id}] {self.title} "
      f"- Owner ID: {self.owner_id} "
      f"- Tasks: {self.task_count}"
    )