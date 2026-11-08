"""JSON persistence and project data management."""

import json
from pathlib import Path
from dataclasses import asdict

from models import User, Project, Task


class StorageService:
  """Manage application data and persist it to JSON."""

  def __init__(self, file_path="data/project_data.json"):
    self.file_path = Path(file_path)

    self.users = {}
    self.projects = {}
    self.tasks = {}

    self.load()

  def load(self):
    """Load saved data, or start empty if no file exists."""
    if not self.file_path.exists():
      self.users = {}
      self.projects = {}
      self.tasks = {}
      return

    try:
      with self.file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

      if not isinstance(data, dict):
        raise ValueError("Saved data must be a JSON object.")

      users = {
        int(item["id"]): User(**item)
        for item in data.get("users", [])
      }

      projects = {
        int(item["id"]): Project(**item)
        for item in data.get("projects", [])
      }

      tasks = {
        int(item["id"]): Task(**item)
        for item in data.get("tasks", [])
      }

      self.users = users
      self.projects = projects
      self.tasks = tasks

    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
      raise RuntimeError(
        f"Unable to load project data: {error}"
      ) from error

  def save(self):
    """Save all users, projects, and tasks to JSON."""
    data = {
      "users": [
        asdict(user)
        for user in self.users.values()
      ],
      "projects": [
        asdict(project)
        for project in self.projects.values()
      ],
      "tasks": [
        asdict(task)
        for task in self.tasks.values()
      ],
    }

    try:
      self.file_path.parent.mkdir(
        parents=True,
        exist_ok=True
      )

      with self.file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    except OSError as error:
      raise RuntimeError(
        f"Unable to save project data: {error}"
      ) from error

  @staticmethod
  def next_id(collection):
    """Generate the next available numeric ID."""
    return max(collection.keys(), default=0) + 1

  def add_user(self, name, email):
    """Create and save a new user."""
    if any(
      user.email.lower() == email.strip().lower()
      for user in self.users.values()
    ):
      raise ValueError("A user with that email already exists.")

    user = User(
      id=self.next_id(self.users),
      name=name,
      email=email
    )

    self.users[user.id] = user
    self.save()

    return user

  def add_project(self, owner_id, title, description="", due_date=""):
    """Create a project owned by an existing user."""
    if owner_id not in self.users:
      raise ValueError("User not found.")

    project = Project(
      id=self.next_id(self.projects),
      title=title,
      owner_id=owner_id,
      description=description,
      due_date=due_date
    )

    self.projects[project.id] = project
    self.users[owner_id].add_project(project.id)

    self.save()
    return project

  def add_task(self, project_id, title):
    """Create a task in an existing project."""
    if project_id not in self.projects:
      raise ValueError("Project not found.")

    task = Task(
      id=self.next_id(self.tasks),
      title=title,
      project_id=project_id
    )

    self.tasks[task.id] = task
    self.projects[project_id].add_task(task.id)

    self.save()
    return task

  def assign_task(self, task_id, user_id):
    """Assign an existing user to an existing task."""
    if task_id not in self.tasks:
      raise ValueError("Task not found.")

    if user_id not in self.users:
      raise ValueError("User not found.")

    task = self.tasks[task_id]

    task.assign_user(user_id)
    self.users[user_id].add_task(task_id)

    self.save()
    return task

  def complete_task(self, task_id):
      """Mark a task complete and save the change."""
      if task_id not in self.tasks:
        raise ValueError("Task not found.")

      task = self.tasks[task_id]
      task.complete()

      self.save()
      return task

  def get_user_by_name(self, name):
    """Find a user by name, ignoring capitalization."""
    for user in self.users.values():
      if user.name.lower() == name.strip().lower():
        return user

    raise ValueError(f"User not found: {name}")

  def get_project_by_title(self, title):
    """Find a project by title, ignoring capitalization."""
    for project in self.projects.values():
      if project.title.lower() == title.strip().lower():
        return project

    raise ValueError(f"Project not found: {title}")

  def get_task_by_title(self, project_id, title):
    """Find a task by its project and title."""
    for task in self.tasks.values():
      if (
        task.project_id == project_id
        and task.title.lower() == title.strip().lower()
      ):
        return task

    raise ValueError(f"Task not found: {title}")

  def get_project_tasks(self, project_id):
    """Return all tasks associated with a project."""
    if project_id not in self.projects:
      raise ValueError("Project not found.")

    return [
      task
      for task in self.tasks.values()
      if task.project_id == project_id
    ]

  def get_user_projects(self, user_id):
    """Return all projects owned by a user."""
    if user_id not in self.users:
      raise ValueError("User not found.")

    return [
      project
      for project in self.projects.values()
      if project.owner_id == user_id
    ]

  def project_summary_data(self, project_id):
    """Build structured project information for the AI client."""
    if project_id not in self.projects:
      raise ValueError("Project not found.")

    project = self.projects[project_id]
    owner = self.users[project.owner_id]
    tasks = self.get_project_tasks(project_id)

    return {
      "project": project.title,
      "description": project.description,
      "due_date": project.due_date,
      "owner": owner.name,
      "total_tasks": len(tasks),
      "completed_tasks": sum(
          task.is_complete for task in tasks
      ),
      "tasks": [
        {
          "title": task.title,
          "status": task.status,
          "contributors": [
              self.users[user_id].name
              for user_id in task.assigned_to
              if user_id in self.users
          ]
        }
          for task in tasks
      ]
    }