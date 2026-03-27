"""Task management Streamlit application."""

import streamlit as st
from datetime import datetime
from typing import Optional

from db import (
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

# Page configuration
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_status = st.sidebar.selectbox(
    "Filter by Status",
    options=["All", "pending", "in_progress", "completed"],
    help="Select a status to filter tasks",
)
selected_priority = st.sidebar.selectbox(
    "Filter by Priority",
    options=["All", "low", "medium", "high"],
    help="Select a priority to filter tasks",
)

# Page title and description
st.title("✅ Task Manager")
st.markdown(
    """
    A simple task management system to learn database operations with Python and MySQL.
    Create, read, update, and delete tasks easily!
    """
)

# Database initialization and connection check
try:
    init_db()
    db_connected = True
except Exception as e:
    st.error(f"Failed to initialize database: {e}")
    db_connected = False

if not db_connected:
    st.warning("Unable to connect to database. Please check your configuration.")
    st.stop()

# Main content
st.divider()

# Add Task Section
st.header("Add New Task")
with st.form("add_task_form"):
    title = st.text_input("Task Title", placeholder="Enter task title")
    description = st.text_area(
        "Description (Optional)", placeholder="Enter task description"
    )
    priority = st.selectbox("Priority", options=["low", "medium", "high"])

    submitted = st.form_submit_button("Add Task", use_container_width=True)

    if submitted:
        if not title:
            st.error("Task title is required")
        else:
            success, task_id, message = create_task(
                title=title, description=description, priority=priority
            )
            if success:
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")

st.divider()

# Task List Display Section
st.header("Your Tasks")

# Get tasks based on filter
if selected_status == "All":
    success, tasks, message = get_all_tasks()
else:
    success, tasks, message = get_tasks_by_status(selected_status)

if not success:
    st.error(f"❌ Failed to load tasks: {message}")
elif not tasks:
    st.info("📭 No tasks yet. Create one to get started!")
else:
    # Apply priority filter
    if selected_priority != "All":
        tasks = [t for t in tasks if t["priority"] == selected_priority]

    if not tasks:
        st.info("📭 No tasks match your filters.")
    else:  # noqa: E117
         # Display tasks in a table-like format
         for task in tasks:
             with st.container(border=True):
                 col1, col2, col3 = st.columns([2, 1, 1])

                 with col1:
                     status_emoji = {
                         "pending": "⏳",
                         "in_progress": "🔄",
                         "completed": "✅",
                     }
                     st.subheader(
                         f"{status_emoji.get(task['status'], '•')} {task['title']}"
                     )
                     if task["description"]:
                         st.write(task["description"])
                     st.caption(
                         f"Priority: {task['priority']} | Created: {task['created_at']}"
                     )

                 with col2:
                     new_status = st.selectbox(
                         "Status",
                         options=["pending", "in_progress", "completed"],
                         index=["pending", "in_progress", "completed"].index(
                             task["status"]
                         ),
                         key=f"status_{task['id']}",
                         label_visibility="collapsed",
                     )

                     if new_status != task["status"]:
                         success, msg = update_task_status(task["id"], new_status)
                         if success:
                             st.success("Updated!", icon="✅")
                             st.rerun()
                         else:
                             st.error(f"Failed: {msg}")

                 with col3:
                     if st.button(
                         "🗑️ Delete",
                         key=f"delete_{task['id']}",
                         use_container_width=True,
                     ):
                         success, msg = delete_task(task["id"])
                         if success:
                             st.success("Deleted!", icon="✅")
                             st.rerun()
                         else:
                             st.error(f"Failed: {msg}")

st.divider()

# Statistics Section
st.sidebar.header("📊 Statistics")
success, stats, msg = get_task_statistics()

if success:
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        st.metric("Total", stats.get("total", 0))
    with col2:
        pending = stats.get("by_status", {}).get("pending", 0)
        st.metric("Pending", pending)
    with col3:
        completed = stats.get("by_status", {}).get("completed", 0)
        st.metric("Done", completed)
