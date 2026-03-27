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
    Establece una conexión a la base de datos MySQL.
    
    Esta función es fundamental para el tutorial - todas las operaciones 
    de base de datos la utilizan. Demuestra cómo manejar configuración,
    conexiones y diferentes tipos de errores apropiadamente.

    Returns:
        Objeto de conexión MySQL si es exitoso, None en caso contrario

    Raises:
        Error: Error de conexión MySQL con detalles específicos
    """
    try:
        # Cargar configuración desde variables de entorno
        config = load_db_config()
        
        # Establecer conexión usando desempaquetado de diccionario
        # **config equivale a: mysql.connector.connect(host=..., port=..., etc.)
        connection = mysql.connector.connect(**config)
        return connection
        
    except Error as err:
        # Manejo específico de errores comunes de MySQL
        if err.errno == 2003:  # Error: no puede conectar al servidor
            raise Error(
                "Cannot connect to MySQL server. Is the database running?"
            )
        else:
            raise Error(f"Database connection failed: {err}")
            
    except ValueError as err:
        # Error de configuración (variables de entorno faltantes)
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
    [EJERCICIO] Actualizar el estado de una tarea existente.
    
    Esta función debe cambiar el estado de una tarea específica a un nuevo valor.
    Primero debe validar que el estado sea válido, luego conectarse a la base de 
    datos y ejecutar la actualización.

    Instrucciones:
    1. Validar que el status esté en la lista de estados válidos
    2. Si no es válido, retornar False con mensaje de error
    3. Conectarse a la base de datos usando connect_db()
    4. Crear cursor y ejecutar consulta UPDATE
    5. Verificar que se actualizó al menos un registro (cursor.rowcount)
    6. Manejar el caso donde la tarea no existe
    7. Cerrar recursos y manejar errores apropiadamente

    Pistas:
    - Estados válidos: ["pending", "in_progress", "completed"]
    - Consulta SQL: "UPDATE tasks SET status = %s WHERE id = %s"
    - Parámetros en orden: (status, task_id)
    - Si cursor.rowcount == 0, la tarea no existe
    - Usar try/except/finally para manejo seguro de recursos
    - Observar create_task() para ver el patrón de conexión y manejo de errores

    Args:
        task_id: ID de la tarea a actualizar
        status: Nuevo estado - 'pending', 'in_progress', o 'completed'

    Returns:
        Tupla de (éxito: bool, mensaje: str)
        - True, "Mensaje de éxito" si se actualizó correctamente
        - False, "Mensaje de error" si hubo problemas, estado inválido, o tarea no encontrada
    """
    # TODO: Implementar esta función siguiendo las instrucciones
    # Recuerda validar el estado antes de conectar a la base de datos
    # Usa las otras funciones como referencia para el manejo de conexiones
    pass


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
    [EJERCICIO] Eliminar una tarea de la base de datos.
    
    Esta función debe conectarse a la base de datos y eliminar la tarea 
    especificada por su ID. Es importante manejar casos donde la tarea 
    no existe y gestionar errores de conexión apropiadamente.

    Instrucciones:
    1. Obtener una conexión a la base de datos usando connect_db()
    2. Crear un cursor para ejecutar la consulta
    3. Ejecutar una consulta DELETE con el ID de la tarea
    4. Verificar si realmente se eliminó algún registro (usar cursor.rowcount)
    5. Manejar el caso donde la tarea no existe
    6. Cerrar recursos y manejar errores con try/except/finally

    Pistas:
    - Consulta SQL: "DELETE FROM tasks WHERE id = %s"
    - Si cursor.rowcount == 0, significa que no se encontró la tarea
    - Usar parámetros para evitar SQL injection: cursor.execute(query, (task_id,))
    - No olvides hacer commit() para confirmar los cambios
    - Revisar las otras funciones como referencia para el manejo de conexiones

    Args:
        task_id: ID de la tarea a eliminar

    Returns:
        Tupla de (éxito: bool, mensaje: str)
        - True, "Mensaje de éxito" si la tarea se eliminó
        - False, "Mensaje de error" si hubo problemas o no se encontró
    """
    # TODO: Implementar esta función siguiendo las instrucciones
    # Puedes usar create_task() y update_task_status() como referencia
    pass


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
