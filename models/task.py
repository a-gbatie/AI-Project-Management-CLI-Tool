"""Task model and task status management."""

from dataclasses import dataclass, field


@dataclass
class Task:
  """A task belonging to a project."""

  id: int
  title: str
  project_id: int
  status: str = "pending"
  assigned_to: list[int] = field(default_factory=list)

  def __post_init__(self):
    self.title = self.title.strip()

    if not self.title:
      raise ValueError("Task title cannot be empty.")

    if self.status not in ("pending", "complete"):
      raise ValueError("Invalid task status.")

  @property
  def is_complete(self):
    """Check whether the task has been completed."""
    return self.status == "complete"

  def complete(self):
    """Mark the task as complete."""
    self.status = "complete"

  def assign_user(self, user_id):
    """Assign a contributor to this task."""
    if user_id not in self.assigned_to:
      self.assigned_to.append(user_id)

  def __str__(self):
    return (
      f"[{self.id}] {self.title} "
      f"- {self.status} "
      f"(Project {self.project_id})"
    )