"""Tests for User, Project, and Task models."""

import pytest

from models import User, Project, Task


def test_user_creation():
  user = User(
    id=1,
    name="Alex",
    email="alex@example.com"
  )

  assert user.name == "Alex"
  assert user.email == "alex@example.com"
  assert user.project_count == 0


def test_user_inheritance():
  from models import Person

  user = User(
    id=1,
    name="Alex",
    email="alex@example.com"
  )

  assert isinstance(user, Person)


def test_user_rejects_empty_name():
  with pytest.raises(ValueError):
    User(
      id=1,
      name=" ",
      email="alex@example.com"
    )


def test_user_rejects_invalid_email():
  with pytest.raises(ValueError):
    User(
      id=1,
      name="Alex",
      email="invalid-email"
    )


def test_user_project_relationship():
  user = User(
    id=1,
    name="Alex",
    email="alex@example.com"
  )

  user.add_project(10)
  user.add_project(10)

  assert user.project_ids == [10]
  assert user.project_count == 1


def test_project_creation():
  project = Project(
    id=1,
    title="CLI Tool",
    owner_id=1
  )

  assert project.title == "CLI Tool"
  assert project.owner_id == 1
  assert project.task_count == 0


def test_project_task_relationship():
  project = Project(
    id=1,
    title="CLI Tool",
    owner_id=1
  )

  project.add_task(5)
  project.add_task(5)

  assert project.task_ids == [5]
  assert project.task_count == 1


def test_task_creation():
  task = Task(
    id=1,
    title="Write tests",
    project_id=1
  )

  assert task.status == "pending"
  assert task.is_complete is False


def test_complete_task():
  task = Task(
    id=1,
    title="Write tests",
    project_id=1
  )

  task.complete()

  assert task.status == "complete"
  assert task.is_complete is True


def test_task_multiple_contributors():
  task = Task(
    id=1,
    title="Write tests",
    project_id=1
  )

  task.assign_user(1)
  task.assign_user(2)
  task.assign_user(1)

  assert task.assigned_to == [1, 2]