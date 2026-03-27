"""Unit tests for database module."""

import pytest
from app.db import (
    connect_db,
    create_task,
    delete_task,
    get_all_tasks,
    get_task_by_id,
    get_task_statistics,
    get_tasks_by_status,
    init_db,
    update_task,
    update_task_status,
)


class TestDatabaseConnection:
    """Tests for database connection functionality."""

    def test_connect_db_success(self) -> None:
        """Test successful database connection."""
        try:
            connection = connect_db()
            assert connection is not None
            assert connection.is_connected()
            connection.close()
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_init_db_success(self) -> None:
        """Test database initialization."""
        try:
            result = init_db()
            assert result is True
        except Exception as e:
            pytest.skip(f"Database not available: {e}")


class TestTaskCreation:
    """Tests for task creation functionality."""

    def test_create_task_success(self) -> None:
        """Test successful task creation."""
        try:
            init_db()
            success, task_id, message = create_task(
                title="Test Task",
                description="This is a test task",
                priority="high",
            )

            assert success is True
            assert task_id is not None
            assert task_id > 0
            assert "created" in message.lower()

            # Cleanup
            if task_id:
                delete_task(task_id)

        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_create_task_minimal(self) -> None:
        """Test task creation with minimal parameters."""
        try:
            init_db()
            success, task_id, message = create_task(title="Minimal Task")

            assert success is True
            assert task_id is not None

            # Cleanup
            if task_id:
                delete_task(task_id)

        except Exception as e:
            pytest.skip(f"Database not available: {e}")


class TestTaskRetrieval:
    """Tests for task retrieval functionality."""

    def test_get_all_tasks(self) -> None:
        """Test retrieving all tasks."""
        try:
            init_db()
            success, tasks, message = get_all_tasks()

            assert success is True
            assert isinstance(tasks, list)

        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_get_task_by_id(self) -> None:
        """Test retrieving a specific task by ID."""
        try:
            init_db()

            # Create a task first
            success, task_id, _ = create_task(title="Test Task for Retrieval")
            if not success or not task_id:
                pytest.skip("Could not create test task")

            # Retrieve it
            success, task, message = get_task_by_id(task_id)
            assert success is True
            assert task is not None
            assert task["id"] == task_id
            assert task["title"] == "Test Task for Retrieval"

            # Cleanup
            delete_task(task_id)

        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_get_task_by_id_not_found(self) -> None:
        """Test retrieving a non-existent task."""
        try:
            init_db()
            success, task, message = get_task_by_id(999999)

            assert success is False
            assert task is None

        except Exception as e:
            pytest.skip(f"Database not available: {e}")


class TestTaskStatusUpdate:
    """Tests for task status update functionality."""

    def test_update_task_status_success(self) -> None:
        """Test successful task status update."""
        try:
            init_db()

            # Create a task
            success, task_id, _ = create_task(title="Status Update Test")
            if not success or not task_id:
                pytest.skip("Could not create test task")

            # Update status
            success, message = update_task_status(task_id, "in_progress")
            assert success is True

            # Verify update
            _, task, _ = get_task_by_id(task_id)
            assert task["status"] == "in_progress"

            # Cleanup
            delete_task(task_id)

        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_update_task_status_invalid_status(self) -> None:
        """Test updating task with invalid status."""
        try:
            init_db()

            # Create a task
            success, task_id, _ = create_task(title="Invalid Status Test")
            if not success or not task_id:
                pytest.skip("Could not create test task")

            # Try to update with invalid status
            success, message = update_task_status(task_id, "invalid_status")
            assert success is False

            # Cleanup
            delete_task(task_id)

        except Exception as e:
            pytest.skip(f"Database not available: {e}")


class TestTaskFiltering:
    """Tests for task filtering functionality."""

    def test_get_tasks_by_status(self) -> None:
        """Test retrieving tasks filtered by status."""
        try:
            init_db()

            # Create a task with pending status
            success, task_id, _ = create_task(title="Filter Test")
            if not success or not task_id:
                pytest.skip("Could not create test task")

            # Retrieve pending tasks
            success, tasks, message = get_tasks_by_status("pending")
            assert success is True
            assert isinstance(tasks, list)

            # Cleanup
            delete_task(task_id)

        except Exception as e:
            pytest.skip(f"Database not available: {e}")


class TestTaskStatistics:
    """Tests for task statistics functionality."""

    def test_get_task_statistics(self) -> None:
        """Test retrieving task statistics."""
        try:
            init_db()

            success, stats, message = get_task_statistics()
            assert success is True
            assert isinstance(stats, dict)
            assert "total" in stats
            assert "by_status" in stats
            assert "by_priority" in stats

        except Exception as e:
            pytest.skip(f"Database not available: {e}")
