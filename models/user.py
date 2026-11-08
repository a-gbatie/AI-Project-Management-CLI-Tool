"""User models for the project management application."""

from dataclasses import dataclass, field # @dataclass automatically creates methods like __init__() - field() gives each object its own empty list


@dataclass
class Person:
  """Base class representing a person."""

  # type annotations - name and email should be strings
  name: str
  email: str

  def __post_init__(self): # run automatically after the dataclass
    self.name = self.name.strip() # removes extra spaces
    self.email = self.email.strip() # '' '' ''

    if not self.name:
      raise ValueError("Name cannot be empty.") # stops creation if name is empty

    if not self.email or "@" not in self.email:
      raise ValueError("A valid email is required.") # stops creation if empty or missing @ symbol

  def __str__(self):
    return f"{self.name} <{self.email}>"


@dataclass
class User(Person): # User inherits from Person - User automatically receives name & email 
  """A user who owns projects and can contribute to tasks."""

  id: int # each user has unique id
  project_ids: list[int] = field(default_factory=list) # creates empty list for each user 
  task_ids: list[int] = field(default_factory=list) # stores the ids of tasks assigned to particular user

  @property
  def project_count(self):
    """Return the number of projects owned by this user."""
    return len(self.project_ids) # returns number of tasks in the list

  def add_project(self, project_id):
    """Associate a project with this user."""
    if project_id not in self.project_ids: # checks if project id is already in list
      self.project_ids.append(project_id) # adds only if project id isn't already in list

  def add_task(self, task_id):
    """Associate a task with this user."""
    if task_id not in self.task_ids: # check is task is already in list
      self.task_ids.append(task_id) # add task id to user's tasks list

  def __str__(self): # override the __str__() from Person
    return (
      f"[{self.id}] {self.name} ({self.email}) " # returns string with user's ID, name, email, and number of projects
      f"- {self.project_count} project(s)"
    )