"""Database layer for task management application."""

import os
from typing import Any, Dict, List, Optional, Tuple

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error


def load_db_config() -> Dict[str, Any]:
    """
    Load database configuration from environment variables.

    Returns:
        Dictionary containing database connection configuration

    Raises:
        ValueError: If required environment variables are missing
    """
    load_dotenv()

    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "database": os.getenv("MYSQL_DB"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
    }

    # Validate required fields
    required_fields = ["database", "user", "password"]
    missing_fields = [field for field in required_fields if not config[field]]

    if missing_fields:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_fields)}"
        )

    return config


def connect_db() -> Optional[mysql.connector.MySQLConnection]:
    """
    Establish a connection to the MySQL database.

    Returns:
        MySQL connection object if successful, None otherwise

    Raises:
        Error: MySQL connection error with details
    """
    try:
        config = load_db_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Error as err:
        if err.errno == 2003:
            raise Error(
                "Cannot connect to MySQL server. Is the database running?"
            )
        else:
            raise Error(f"Database connection failed: {err}")
    except ValueError as err:
        raise Error(f"Configuration error: {err}")


def init_db() -> bool:
    """
    Initialize the database by creating the tasks table if it doesn't exist.

    Returns:
        True if initialization successful, False otherwise
    """
    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status ENUM('pending', 'in_progress', 'completed')
                DEFAULT 'pending',
            priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """

        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        return True

    except Error as err:
        return False, [], f"Failed to retrieve tasks: {err}"
    finally:
        if connection and connection.is_connected():
            connection.close()


def get_task_statistics() -> Tuple[bool, Dict[str, Any], str]:
    """
    Retrieve statistics about all tasks.

    Returns:
        Tuple of (success: bool, stats: Dict, message: str)
    """
    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)

        # Total tasks
        cursor.execute("SELECT COUNT(*) as total FROM tasks")
        total = cursor.fetchone()["total"]

        # Tasks by status
        cursor.execute(
            """
            SELECT status, COUNT(*) as count
            FROM tasks
            GROUP BY status
            """
        )
        status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

        # Tasks by priority
        cursor.execute(
            """
            SELECT priority, COUNT(*) as count
            FROM tasks
            GROUP BY priority
            """
        )
        priority_counts = {
            row["priority"]: row["count"] for row in cursor.fetchall()
        }

        stats = {
            "total": total,
            "by_status": status_counts,
            "by_priority": priority_counts,
        }

        cursor.close()
        return True, stats, "Statistics retrieved"

    except Error as err:
        return False, {}, f"Failed to retrieve statistics: {err}"
    finally:
        if connection and connection.is_connected():
            connection.close()


def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
) -> Tuple[bool, Optional[int], str]:
    """
    Create a new task in the database.

    Args:
        title: Task title (required)
        description: Task description (optional)
        priority: Task priority - 'low', 'medium', 'high' (default: 'medium')

    Returns:
        Tuple of (success: bool, task_id: Optional[int], message: str)
    """
    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()

        insert_query = """
        INSERT INTO tasks (title, description, priority, status)
        VALUES (%s, %s, %s, 'pending')
        """

        cursor.execute(insert_query, (title, description, priority))
        connection.commit()

        task_id = cursor.lastrowid
        cursor.close()

        return True, task_id, f"Task '{title}' created successfully"

    except Error as err:
        return False, None, f"Failed to create task: {err}"
    finally:
        if connection and connection.is_connected():
            connection.close()


def get_all_tasks() -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Retrieve all tasks from the database.

    Returns:
        Tuple of (success: bool, tasks: List[Dict], message: str)
    """
    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)

        select_query = """
        SELECT id, title, description, status, priority, created_at, updated_at
        FROM tasks
        ORDER BY created_at DESC
        """

        cursor.execute(select_query)
        tasks = cursor.fetchall()
        cursor.close()

        return True, tasks, f"Retrieved {len(tasks)} tasks"

    except Error as err:
        return False, [], f"Failed to retrieve tasks: {err}"
    finally:
        if connection and connection.is_connected():
            connection.close()


def get_task_by_id(task_id: int) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Retrieve a specific task by ID.

    Args:
        task_id: The task ID to retrieve

    Returns:
        Tuple of (success: bool, task: Optional[Dict], message: str)
    """
    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)

        select_query = """
        SELECT id, title, description, status, priority, created_at, updated_at
        FROM tasks
        WHERE id = %s
        """

        cursor.execute(select_query, (task_id,))
        task = cursor.fetchone()
        cursor.close()

        if task:
            return True, task, f"Task {task_id} retrieved"
        else:
            return False, None, f"Task {task_id} not found"

    except Error as err:
        return False, None, f"Failed to retrieve task: {err}"
    finally:
        if connection and connection.is_connected():
            connection.close()


def update_task_status(task_id: int, status: str) -> Tuple[bool, str]:
    """
    Update the status of a task.

    Args:
        task_id: The task ID to update
        status: New status - 'pending', 'in_progress', or 'completed'

    Returns:
        Tuple of (success: bool, message: str)
    """
    valid_statuses = ["pending", "in_progress", "completed"]
    if status not in valid_statuses:
        return (
            False,
            f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()

        update_query = "UPDATE tasks SET status = %s WHERE id = %s"
        cursor.execute(update_query, (status, task_id))
        connection.commit()

        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Task {task_id} not found"

        cursor.close()
        return True, f"Task {task_id} status updated to '{status}'"

    except Error as err:
        return False, f"Failed to update task status: {err}"
    finally:
        if connection and connection.is_connected():
            connection.close()


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Update task details.

    Args:
        task_id: The task ID to update
        title: New task title (optional)
        description: New task description (optional)
        priority: New task priority (optional)

    Returns:
        Tuple of (success: bool, message: str)
    """
    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Build dynamic query
        updates = []
        values = []

        if title is not None:
            updates.append("title = %s")
            values.append(title)
        if description is not None:
            updates.append("description = %s")
            values.append(description)
        if priority is not None:
            updates.append("priority = %s")
            values.append(priority)

        if not updates:
            return False, "No fields to update"

        values.append(task_id)
        update_query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s"

        cursor.execute(update_query, values)
        connection.commit()

        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Task {task_id} not found"

        cursor.close()
        return True, f"Task {task_id} updated successfully"

    except Error as err:
        return False, f"Failed to update task: {err}"
    finally:
        if connection and connection.is_connected():
            connection.close()


def delete_task(task_id: int) -> Tuple[bool, str]:
    """
    Delete a task from the database.

    Args:
        task_id: The task ID to delete

    Returns:
        Tuple of (success: bool, message: str)
    """
    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()

        delete_query = "DELETE FROM tasks WHERE id = %s"
        cursor.execute(delete_query, (task_id,))
        connection.commit()

        if cursor.rowcount == 0:
            cursor.close()
            return False, f"Task {task_id} not found"

        cursor.close()
        return True, f"Task {task_id} deleted successfully"

    except Error as err:
        return False, f"Failed to delete task: {err}"
    finally:
        if connection and connection.is_connected():
            connection.close()


def get_tasks_by_status(status: str) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Retrieve tasks filtered by status.

    Args:
        status: Task status to filter by - 'pending', 'in_progress', 'completed'

    Returns:
        Tuple of (success: bool, tasks: List[Dict], message: str)
    """
    valid_statuses = ["pending", "in_progress", "completed"]
    if status not in valid_statuses:
        return (
            False,
            [],
            f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)

        select_query = """
        SELECT id, title, description, status, priority, created_at, updated_at
        FROM tasks
        WHERE status = %s
        ORDER BY created_at DESC
        """

        cursor.execute(select_query, (status,))
        tasks = cursor.fetchall()
        cursor.close()

        return True, tasks, f"Retrieved {len(tasks)} tasks with status '{status}'"

    except Error as err:
        return False, [], f"Failed to retrieve tasks: {err}"
    finally:
        if connection and connection.is_connected():
            connection.close()
