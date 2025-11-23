"""
Centralized Configuration Management for KiiT AI Agents
This module manages all configuration settings for the application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Email Configuration
EMAIL_CONFIG = {
    "address": os.getenv("EMAIL", ""),
    "password": os.getenv("EMAIL_PASSWORD", ""),
    "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
}

# API Keys
API_KEYS = {
    "google": os.getenv("GOOGLE_API_KEY", ""),
    "groq": os.getenv("GROQ_API_KEY", ""),
    "openai": os.getenv("OPENAI_API_KEY", ""),
}

# AI Model Configuration
AI_MODELS = {
    "gemini": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
    "groq": os.getenv("GROQ_MODEL", "deepseek-r1-distill-llama-70b"),
}

# Database Configuration
DATABASE_CONFIG = {
    "path": os.getenv("DATABASE_PATH", str(BASE_DIR / "students.db")),
}

# File Paths
FILE_PATHS = {
    "academic_calendar": BASE_DIR / "-academic-activities" / "calender.pdf",
    "exam_schedule": BASE_DIR / "-academic-activities" / "exam_schedule.pdf",
    "holidays": BASE_DIR / "-academic-activities" / "holidays.pdf",
    "placement_docs": BASE_DIR / "-placement-agent" / "documents",
}

# CORS Configuration
CORS_CONFIG = {
    "allowed_origins": os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001"
    ).split(","),
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["*"],
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_dir": BASE_DIR / "logs",
}

# Scholarship Eligibility Criteria
SCHOLARSHIP_CRITERIA = {
    "min_cgpa": float(os.getenv("SCHOLARSHIP_MIN_CGPA", "7.5")),
    "min_attendance": float(os.getenv("SCHOLARSHIP_MIN_ATTENDANCE", "75.0")),
}

# NOC Eligibility Criteria
NOC_CRITERIA = {
    "min_cgpa": float(os.getenv("NOC_MIN_CGPA", "6.0")),
    "min_attendance": float(os.getenv("NOC_MIN_ATTENDANCE", "70.0")),
}

def validate_config():
    """Validate that required configuration is present."""
    errors = []

    if not EMAIL_CONFIG["address"]:
        errors.append("EMAIL is not set in .env file")
    if not EMAIL_CONFIG["password"]:
        errors.append("EMAIL_PASSWORD is not set in .env file")
    if not API_KEYS["google"]:
        errors.append("GOOGLE_API_KEY is not set in .env file")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    # Create necessary directories
    LOGGING_CONFIG["log_dir"].mkdir(exist_ok=True)
    FILE_PATHS["placement_docs"].mkdir(parents=True, exist_ok=True)

    return True

# Validate configuration on import
if __name__ != "__main__":
    try:
        validate_config()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"⚠️  Configuration validation warning: {e}")
