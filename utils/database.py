"""
Database utilities for KiiT AI Agents
"""
import sqlite3
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

# Import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DATABASE_CONFIG


@contextmanager
def get_db_connection(db_path: Optional[str] = None):
    """
    Context manager for database connections.
    Ensures proper connection handling and automatic cleanup.

    Args:
        db_path: Optional custom database path. Uses default if not provided.

    Yields:
        Database connection object

    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            results = cursor.fetchall()
    """
    conn = None
    try:
        db_path = db_path or DATABASE_CONFIG["path"]
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def execute_query(
    query: str,
    params: tuple = (),
    db_path: Optional[str] = None,
    fetch_one: bool = False
) -> Optional[List[Dict[str, Any]]]:
    """
    Execute a SQL query with proper error handling.

    Args:
        query: SQL query to execute
        params: Query parameters (for parameterized queries)
        db_path: Optional custom database path
        fetch_one: If True, return only one result

    Returns:
        List of results as dictionaries, or single result if fetch_one=True

    Example:
        results = execute_query(
            "SELECT * FROM students WHERE roll_no = ?",
            (roll_number,)
        )
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)

        if query.strip().upper().startswith("SELECT"):
            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
            else:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        else:
            return None


def student_exists(roll_no: str, db_path: Optional[str] = None) -> bool:
    """
    Check if a student exists in the database.

    Args:
        roll_no: Student roll number
        db_path: Optional custom database path

    Returns:
        True if student exists, False otherwise
    """
    result = execute_query(
        "SELECT 1 FROM students WHERE roll_no = ? LIMIT 1",
        (roll_no,),
        db_path,
        fetch_one=True
    )
    return result is not None


def get_student_info(roll_no: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get student information from database.

    Args:
        roll_no: Student roll number
        db_path: Optional custom database path

    Returns:
        Dictionary with student information or None if not found
    """
    return execute_query(
        "SELECT * FROM students WHERE roll_no = ? LIMIT 1",
        (roll_no,),
        db_path,
        fetch_one=True
    )


def update_student_field(
    roll_no: str,
    field: str,
    value: Any,
    db_path: Optional[str] = None
) -> bool:
    """
    Update a specific field for a student.

    Args:
        roll_no: Student roll number
        field: Field name to update
        value: New value
        db_path: Optional custom database path

    Returns:
        True if update successful, False otherwise

    Note:
        This function validates field names against a whitelist to prevent SQL injection
    """
    # Whitelist of allowed fields to prevent SQL injection
    allowed_fields = {
        'name', 'cgpa', 'attendance', 'email', 'department',
        'bonafide_sent', 'noc_sent', 'rank_generation', 'scholarship_sent'
    }

    if field not in allowed_fields:
        raise ValueError(f"Invalid field name: {field}")

    try:
        query = f"UPDATE students SET {field} = ? WHERE roll_no = ?"
        execute_query(query, (value, roll_no), db_path)
        return True
    except Exception:
        return False


# Example usage:
# from utils.database import get_db_connection, get_student_info
#
# # Using context manager
# with get_db_connection() as conn:
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM students WHERE cgpa > 8.0")
#     high_performers = cursor.fetchall()
#
# # Using helper functions
# student = get_student_info("2012345")
# if student:
#     print(f"Student: {student['name']}, CGPA: {student['cgpa']}")
