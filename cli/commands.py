"""Command-line argument parsing and command execution."""

import argparse

from services.storage_service import StorageService
from services.ai_client import ProjectAIClient


def build_parser():
  """Build the command-line argument parser."""
  parser = argparse.ArgumentParser(
    description="Python Project Management CLI Tool"
  )

  subparsers = parser.add_subparsers(
    dest="command",
    required=True
  )

  # Add user
  add_user = subparsers.add_parser(
    "add-user",
    help="Create a new user"
  )
  add_user.add_argument("--name", required=True)
  add_user.add_argument("--email", required=True)

  # List users
  subparsers.add_parser(
    "list-users",
    help="Display all users"
  )

  # Add project
  add_project = subparsers.add_parser(
    "add-project",
    help="Create a project"
  )
  add_project.add_argument("--user", required=True)
  add_project.add_argument("--title", required=True)
  add_project.add_argument("--description", default="")
  add_project.add_argument("--due-date", default="")

  # List projects
  list_projects = subparsers.add_parser(
    "list-projects",
    help="Display projects"
  )
  list_projects.add_argument("--user")

  # Add task
  add_task = subparsers.add_parser(
    "add-task",
    help="Create a task"
  )
  add_task.add_argument("--project", required=True)
  add_task.add_argument("--title", required=True)

  # List tasks
  list_tasks = subparsers.add_parser(
    "list-tasks",
    help="Display tasks"
  )
  list_tasks.add_argument("--project")

  # Assign task
  assign_task = subparsers.add_parser(
    "assign-task",
    help="Assign a user to a task"
  )
  assign_task.add_argument("--project", required=True)
  assign_task.add_argument("--task", required=True)
  assign_task.add_argument("--user", required=True)

  # Complete task
  complete_task = subparsers.add_parser(
    "complete-task",
    help="Mark a task complete"
  )
  complete_task.add_argument("--project", required=True)
  complete_task.add_argument("--task", required=True)

  # Summarize project
  summarize = subparsers.add_parser(
    "summarize-project",
    help="Generate an AI project summary"
  )
  summarize.add_argument("--project", required=True)

  return parser


class ProjectCLI:
  """Execute project management commands."""

  def __init__(self, storage=None, ai_client=None):
    self.storage = (
      storage if storage is not None
      else StorageService()
    )
    self.ai_client = (
      ai_client if ai_client is not None
      else ProjectAIClient()
    )

  def handle_command(self, args):
    """Execute a parsed CLI command and return a result."""
    command = args.command

    if command == "add-user":
      user = self.storage.add_user(
        args.name,
        args.email
      )
      return f"User created: {user}"

    elif command == "list-users":
      users = list(self.storage.users.values())

      if not users:
        return "No users found."

      return "\n".join(str(user) for user in users)

    elif command == "add-project":
      user = self.storage.get_user_by_name(
        args.user
      )

      project = self.storage.add_project(
        owner_id=user.id,
        title=args.title,
        description=args.description,
        due_date=args.due_date
      )

      return f"Project created: {project}"

    elif command == "list-projects":
      if args.user:
          user = self.storage.get_user_by_name(
              args.user
          )
          projects = self.storage.get_user_projects(
              user.id
          )
      else:
        projects = list(
            self.storage.projects.values()
        )

      if not projects:
        return "No projects found."

      return "\n".join(
        str(project) for project in projects
      )

    elif command == "add-task":
      project = self.storage.get_project_by_title(
        args.project
      )

      task = self.storage.add_task(
        project_id=project.id,
        title=args.title
      )

      return f"Task created: {task}"

    elif command == "list-tasks":
      if args.project:
        project = self.storage.get_project_by_title(
          args.project
        )
        tasks = self.storage.get_project_tasks(
          project.id
        )
      else:
        tasks = list(
          self.storage.tasks.values()
        )

      if not tasks:
        return "No tasks found."

      return "\n".join(
        str(task) for task in tasks
      )

    elif command == "assign-task":
      project = self.storage.get_project_by_title(
        args.project
      )

      task = self.storage.get_task_by_title(
        project.id,
        args.task
      )

      user = self.storage.get_user_by_name(
        args.user
      )

      self.storage.assign_task(
        task.id,
        user.id
      )

      return (
        f"Task '{task.title}' assigned "
        f"to {user.name}."
      )

    elif command == "complete-task":
      project = self.storage.get_project_by_title(
          args.project
      )

      task = self.storage.get_task_by_title(
          project.id,
          args.task
      )

      self.storage.complete_task(task.id)

      return f"Task completed: {task.title}"

    elif command == "summarize-project":
      project = self.storage.get_project_by_title(
        args.project
      )

      project_data = (
        self.storage.project_summary_data(
          project.id
        )
      )

      summary = self.ai_client.summarize_project(
        project_data
      )

      return (
        f"\nAI Project Summary: {project.title}\n\n"
        f"{summary}"
      )

    raise ValueError(
      f"Unknown command: {command}"
    )