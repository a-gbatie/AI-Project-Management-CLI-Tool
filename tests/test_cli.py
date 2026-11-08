"""Tests for CLI commands and AI integration."""

import pytest

from cli.commands import build_parser, ProjectCLI
from services.storage_service import StorageService
from services.ai_client import ProjectAIClient


class FakeAIClient:
  """Fake AI client for tests without Ollama."""

  def __init__(self):
    self.received_data = None

  def summarize_project(self, project_data):
    self.received_data = project_data
    return (
      "Project Summary: Progress is good.\n"
      "Risk Notes: No major risks.\n"
      "Recommended Next Steps: Continue testing."
    )


@pytest.fixture
def app(tmp_path):
  storage = StorageService(
    tmp_path / "test_data.json"
  )

  return ProjectCLI(
    storage=storage,
    ai_client=FakeAIClient()
  )


def execute(app, arguments):
  """Parse and execute a CLI command."""
  parser = build_parser()
  args = parser.parse_args(arguments)
  return app.handle_command(args)


def test_add_user_command(app):
  result = execute(
    app,
    [
        "add-user",
        "--name", "Alex",
        "--email", "alex@example.com"
    ]
  )

  assert "User created" in result
  assert "Alex" in result


def test_list_users_command(app):
  execute(
    app,
    [
      "add-user",
      "--name", "Alex",
      "--email", "alex@example.com"
    ]
  )

  result = execute(
    app,
    ["list-users"]
  )

  assert "Alex" in result


def test_add_project_command(app):
  execute(
    app,
    [
      "add-user",
      "--name", "Alex",
      "--email", "alex@example.com"
    ]
  )

  result = execute(
    app,
    [
      "add-project",
      "--user", "Alex",
      "--title", "CLI Tool"
    ]
  )

  assert "Project created" in result
  assert "CLI Tool" in result


def test_add_task_command(app):
  execute(
    app,
    [
      "add-user",
      "--name", "Alex",
      "--email", "alex@example.com"
    ]
  )

  execute(
    app,
    [
      "add-project",
      "--user", "Alex",
      "--title", "CLI Tool"
    ]
  )

  result = execute(
    app,
    [
      "add-task",
      "--project", "CLI Tool",
      "--title", "Write tests"
    ]
  )

  assert "Task created" in result
  assert "Write tests" in result


def test_complete_task_command(app):
  user = app.storage.add_user(
    "Alex",
    "alex@example.com"
  )

  project = app.storage.add_project(
    user.id,
    "CLI Tool"
  )

  task = app.storage.add_task(
    project.id,
    "Write tests"
  )

  result = execute(
    app,
    [
      "complete-task",
      "--project", "CLI Tool",
      "--task", "Write tests"
    ]
  )

  assert "Task completed" in result
  assert task.is_complete is True


def test_assign_task_command(app):
  user = app.storage.add_user(
    "Alex",
    "alex@example.com"
  )

  project = app.storage.add_project(
    user.id,
    "CLI Tool"
  )

  task = app.storage.add_task(
    project.id,
    "Write tests"
  )

  result = execute(
      app,
      [
        "assign-task",
        "--project", "CLI Tool",
        "--task", "Write tests",
        "--user", "Alex"
      ]
  )

  assert "assigned" in result
  assert user.id in task.assigned_to


def test_summarize_project_command(app):
    user = app.storage.add_user(
      "Alex",
      "alex@example.com"
    )

    app.storage.add_project(
      user.id,
      "CLI Tool"
    )

    result = execute(
      app,
      [
        "summarize-project",
        "--project", "CLI Tool"
      ]
    )

    assert "AI Project Summary" in result
    assert "Risk Notes" in result
    assert app.ai_client.received_data["project"] == "CLI Tool"


def test_unknown_command_rejected():
  parser = build_parser()

  with pytest.raises(SystemExit):
    parser.parse_args(["unknown-command"])


def test_missing_required_argument():
  parser = build_parser()

  with pytest.raises(SystemExit):
    parser.parse_args(["add-user", "--name", "Alex"])


def test_ai_client_success(monkeypatch):
  class FakeResponse:
    message = {
      "content": "Project summary generated."
    }

  def fake_chat(model, messages):
    return FakeResponse()

  monkeypatch.setattr(
    "services.ai_client.ollama.chat",
    fake_chat
  )

  client = ProjectAIClient()

  result = client.summarize_project(
    {"project": "CLI Tool"}
  )

  assert result == "Project summary generated."


def test_ai_client_service_error(monkeypatch):
  def fake_chat(model, messages):
    raise ConnectionError("Ollama unavailable")

  monkeypatch.setattr(
    "services.ai_client.ollama.chat",
    fake_chat
  )

  client = ProjectAIClient()

  with pytest.raises(
    RuntimeError,
    match="AI service request failed"
  ):
    client.summarize_project(
      {"project": "CLI Tool"}
    )