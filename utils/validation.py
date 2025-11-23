"""
Input validation utilities for KiiT AI Agents
"""
import re
from typing import Optional, Tuple


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False

    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_roll_number(roll_no: str) -> bool:
    """
    Validate KIIT roll number format.
    Assumes format: 4-digit year + series number (e.g., 2012345, 2112345)

    Args:
        roll_no: Roll number to validate

    Returns:
        True if valid, False otherwise
    """
    if not roll_no:
        return False

    # Check if it's 7 digits and starts with 20 or 21
    pattern = r'^(20|21)\d{5}$'
    return bool(re.match(pattern, str(roll_no).strip()))


def validate_cgpa(cgpa: float) -> Tuple[bool, Optional[str]]:
    """
    Validate CGPA value.

    Args:
        cgpa: CGPA value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        cgpa_val = float(cgpa)
        if cgpa_val < 0.0 or cgpa_val > 10.0:
            return False, "CGPA must be between 0.0 and 10.0"
        return True, None
    except (ValueError, TypeError):
        return False, "CGPA must be a valid number"


def validate_attendance(attendance: float) -> Tuple[bool, Optional[str]]:
    """
    Validate attendance percentage.

    Args:
        attendance: Attendance percentage to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        attendance_val = float(attendance)
        if attendance_val < 0.0 or attendance_val > 100.0:
            return False, "Attendance must be between 0.0 and 100.0"
        return True, None
    except (ValueError, TypeError):
        return False, "Attendance must be a valid number"


def validate_student_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate student name.

    Args:
        name: Student name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Name cannot be empty"

    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"

    if len(name.strip()) > 100:
        return False, "Name cannot exceed 100 characters"

    # Allow letters, spaces, hyphens, and apostrophes
    pattern = r"^[a-zA-Z\s\-'\.]+$"
    if not re.match(pattern, name.strip()):
        return False, "Name contains invalid characters"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove any directory separators
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remove any potentially dangerous characters
    filename = re.sub(r'[^\w\s\-.]', '', filename)

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename.strip()


# Example usage:
# from utils.validation import validate_email, validate_cgpa
#
# if not validate_email(student_email):
#     raise ValueError("Invalid email address")
#
# is_valid, error = validate_cgpa(student_cgpa)
# if not is_valid:
#     logger.error(f"Invalid CGPA: {error}")
