"""Tests for JSON persistence and data relationships."""

import json
import pytest

from services.storage_service import StorageService


@pytest.fixture
def storage(tmp_path):
  """Create isolated storage for each test."""
  return StorageService(
    tmp_path / "test_data.json"
  )


def test_add_user(storage):
  user = storage.add_user(
    "Alex",
    "alex@example.com"
  )

  assert user.id == 1
  assert user.name == "Alex"
  assert len(storage.users) == 1


def test_duplicate_email(storage):
  storage.add_user(
    "Alex",
    "alex@example.com"
  )

  with pytest.raises(ValueError):
    storage.add_user(
      "Another Alex",
      "alex@example.com"
    )


def test_add_project(storage):
  user = storage.add_user(
    "Alex",
    "alex@example.com"
  )

  project = storage.add_project(
    user.id,
    "CLI Tool"
  )

  assert project.owner_id == user.id
  assert project.id in user.project_ids


def test_add_project_invalid_user(storage):
  with pytest.raises(ValueError):
    storage.add_project(
      999,
      "Invalid Project"
    )


def test_add_task(storage):
  user = storage.add_user(
    "Alex",
    "alex@example.com"
  )

  project = storage.add_project(
    user.id,
    "CLI Tool"
  )

  task = storage.add_task(
    project.id,
    "Write tests"
  )

  assert task.project_id == project.id
  assert task.id in project.task_ids


def test_assign_task(storage):
  user = storage.add_user(
    "Alex",
    "alex@example.com"
  )

  project = storage.add_project(
    user.id,
    "CLI Tool"
  )

  task = storage.add_task(
    project.id,
    "Write tests"
  )

  storage.assign_task(
    task.id,
    user.id
  )

  assert user.id in task.assigned_to
  assert task.id in user.task_ids


def test_complete_task(storage):
  user = storage.add_user(
    "Alex",
    "alex@example.com"
  )

  project = storage.add_project(
    user.id,
    "CLI Tool"
  )

  task = storage.add_task(
    project.id,
    "Write tests"
  )

  storage.complete_task(task.id)

  assert task.is_complete is True


def test_json_persistence(storage):
  storage.add_user(
    "Alex",
    "alex@example.com"
  )

  reloaded = StorageService(
    storage.file_path
  )

  assert len(reloaded.users) == 1
  assert reloaded.users[1].name == "Alex"


def test_json_file_structure(storage):
  storage.add_user(
    "Alex",
    "alex@example.com"
  )

  with storage.file_path.open(
    "r",
    encoding="utf-8"
  ) as file:
    data = json.load(file)

  assert "users" in data
  assert "projects" in data
  assert "tasks" in data


def test_missing_file_starts_empty(tmp_path):
  storage = StorageService(
    tmp_path / "missing.json"
  )

  assert storage.users == {}
  assert storage.projects == {}
  assert storage.tasks == {}


def test_malformed_json_raises_error(tmp_path):
  path = tmp_path / "broken.json"
  path.write_text("{not valid json")

  with pytest.raises(
    RuntimeError,
    match="Unable to load"
  ):
    StorageService(path)


def test_project_summary_data(storage):
  user = storage.add_user(
    "Alex",
    "alex@example.com"
  )

  project = storage.add_project(
    user.id,
    "CLI Tool"
  )

  task = storage.add_task(
    project.id,
    "Write tests"
  )

  storage.complete_task(task.id)

  summary = storage.project_summary_data(
    project.id
  )

  assert summary["project"] == "CLI Tool"
  assert summary["total_tasks"] == 1
  assert summary["completed_tasks"] == 1