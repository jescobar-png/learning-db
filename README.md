# Task Manager - Database Tutorial

A practical database learning project demonstrating a complete Python application connected to a MySQL database using Docker.

📖 **Available in other languages**: [Español (Spanish)](README_ES.md)

## Overview

This project teaches database fundamentals by building a simple task management system with:
- **Python backend** with clean database abstraction layer
- **Streamlit UI** for interactive task management
- **MySQL database** running in Docker for data persistence
- **Comprehensive tests** to ensure reliability

### Key Learning Concepts

- Database connection and configuration management
- CRUD operations (Create, Read, Update, Delete)
- Parameterized queries for SQL injection prevention
- Error handling and user-friendly error messages
- Type annotations and code documentation
- Testing database operations
- Docker for containerized databases

---

## Project Architecture

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # Streamlit UI application
│   └── db.py                # Database access layer
├── tests/
│   ├── __init__.py
│   ├── test_db.py           # Database unit tests
│   └── test_main.py         # Application tests
├── docker-compose.yml       # MySQL container configuration
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (local)
├── .env.example            # Environment template (for git)
├── .gitignore              # Git exclusions
└── README.md               # This file
```

### Three Agent Pattern

1. **App Agent** (`app/main.py`): Handles user interaction and display
2. **DB Agent** (`app/db.py`): Manages all database operations
3. **Infrastructure Agent** (`docker-compose.yml`): Manages MySQL container

---

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- pip (Python package manager)

---

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd db-tutorial

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

The project includes a `.env` file with default values:

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=testdb
MYSQL_USER=testuser
MYSQL_PASSWORD=testpass
```

To customize, edit `.env` with your desired values.

### 3. Start MySQL Container

```bash
# Start the MySQL container
docker-compose up -d

# Verify it's running
docker ps
```

### 4. Run the Application

```bash
# Start Streamlit app
streamlit run app/main.py

# App will open at http://localhost:8501
```

---

## Usage

### Creating a Task

1. Enter task title (required)
2. Add optional description
3. Select priority (low, medium, high)
4. Click "Add Task"

### Managing Tasks

- **Status Update**: Change task status from dropdown
- **Delete**: Remove task with delete button
- **Filter**: Use sidebar to filter by status and priority

### Viewing Statistics

See task summary in the sidebar:
- Total tasks count
- Pending tasks count
- Completed tasks count

---

## API Reference

### Database Module (`app/db.py`)

#### Connection

```python
from app.db import connect_db, init_db

# Initialize database (creates tables if needed)
init_db()

# Get connection
connection = connect_db()
```

#### Task Operations

```python
from app.db import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    get_tasks_by_status,
    update_task,
    update_task_status,
    delete_task,
    get_task_statistics,
)

# Create task
success, task_id, message = create_task(
    title="My Task",
    description="Task details",
    priority="high"
)

# Get all tasks
success, tasks, message = get_all_tasks()

# Get single task
success, task, message = get_task_by_id(task_id=1)

# Filter by status
success, tasks, message = get_tasks_by_status("pending")

# Update task
success, message = update_task(
    task_id=1,
    title="Updated Title",
    priority="medium"
)

# Update status only
success, message = update_task_status(task_id=1, status="completed")

# Delete task
success, message = delete_task(task_id=1)

# Get statistics
success, stats, message = get_task_statistics()
```

All functions return tuples with:
- `success`: Boolean indicating operation result
- `data`: Returned data (or message for operations without data)
- `message`: Human-readable status message

---

## Testing

### Run All Tests

```bash
# Install test dependencies (included in requirements.txt)
pip install pytest

# Run all tests
pytest

# Run specific test file
pytest tests/test_db.py

# Run specific test
pytest tests/test_db.py::TestTaskCreation::test_create_task_success

# Run with verbose output
pytest -v
```

### Test Coverage

Tests are organized by functionality:

- **Connection Tests**: Database connectivity
- **CRUD Tests**: Create, read, update, delete operations
- **Filter Tests**: Status-based filtering
- **Statistics Tests**: Data aggregation
- **Error Handling Tests**: Invalid inputs and edge cases

---

## Database Schema

### Tasks Table

```sql
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columns:**
- `id`: Unique task identifier
- `title`: Task title (required)
- `description`: Detailed task description (optional)
- `status`: Current task state
- `priority`: Task urgency level
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp

---

## Code Quality

### Standards

Following best practices:
- **Type Hints**: All functions annotated with types
- **Error Handling**: Try-catch blocks with user-friendly messages
- **Documentation**: Docstrings for all functions
- **SQL Security**: Parameterized queries prevent SQL injection
- **Naming**: snake_case for functions/variables, PascalCase for classes

### Formatting

Code follows these standards:
- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Imports**: Organized per PEP 8
- **Trailing Commas**: Used in multi-line constructs

### Tools

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Check code style
flake8 app/ tests/

# Type checking
mypy app/
```

---

## Troubleshooting

### Database Connection Failed

**Problem**: "Cannot connect to MySQL server"

**Solutions**:
1. Verify Docker container is running: `docker ps`
2. Check `.env` file has correct MySQL credentials
3. Wait 10-15 seconds after starting container for MySQL to initialize
4. Verify port 3306 isn't in use: `lsof -i :3306`

### Module Not Found

**Problem**: "ModuleNotFoundError: No module named 'streamlit'"

**Solution**:
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Problem**: "Error: port 3306 is already allocated"

**Solutions**:
1. Stop existing container: `docker-compose down`
2. Or use different port in `docker-compose.yml`:
   ```yaml
   ports:
     - "3307:3306"  # Change host port
   ```

### Permission Denied on .env

**Problem**: Cannot read environment variables

**Solution**:
```bash
chmod 600 .env
```

---

## Development Workflow

### Adding a New Feature

1. **Plan**: Add function to `app/db.py` for database operation
2. **Implement**: Write database function with type hints and error handling
3. **Test**: Add tests to `tests/test_db.py`
4. **UI**: Add UI component to `app/main.py` if needed
5. **Verify**: Run all tests and manual testing
6. **Commit**: Add to git with descriptive message

### Example: Add Task Due Date

```python
# 1. Add to db.py
def update_task_due_date(task_id: int, due_date: str) -> Tuple[bool, str]:
    """Update task due date."""
    # Implementation...

# 2. Add to tests/test_db.py
def test_update_task_due_date():
    """Test setting task due date."""
    # Test implementation...

# 3. Add to main.py UI
due_date = st.date_input("Due Date")
if st.button("Set Due Date"):
    success, msg = update_task_due_date(task_id, str(due_date))
```

---

## Git Workflow

### Initial Setup

```bash
git add .
git commit -m "Initial project setup with database and UI"
```

### Making Changes

```bash
# Make code changes...

# Stage changes
git add app/ tests/

# Commit with descriptive message
git commit -m "Add task priority filtering"

# Push to remote (if configured)
git push origin main
```

### Ignore Sensitive Files

The `.gitignore` file excludes:
- Virtual environments (`venv/`, `myenv/`)
- Environment files (`.env`)
- Python caches (`__pycache__/`)
- IDE settings (`.vscode/`, `.idea/`)

---

## Performance Tips

1. **Connection Pooling**: Current version creates new connection per operation. For production, use `mysql-connector-python` with connection pooling.

2. **Query Optimization**: Add database indexes for frequently searched columns.

3. **Caching**: Use Streamlit's `@st.cache_data` decorator for expensive queries.

4. **Pagination**: For large task lists, implement pagination instead of loading all at once.

---

## Resources

- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python mysql-connector-python](https://dev.mysql.com/doc/connector-python/en/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## License

Educational project - Free to use and modify for learning purposes.

---

## Definition of Done

A feature is complete when:
- ✅ Code follows style guidelines
- ✅ Type hints on all functions
- ✅ Error handling implemented
- ✅ Tests written and passing
- ✅ Manual testing performed
- ✅ Database operations verified
- ✅ UI displays data correctly
- ✅ No console errors or warnings
