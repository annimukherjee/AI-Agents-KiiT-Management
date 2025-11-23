# KiiT AI Agents - Setup Guide

This guide will help you set up the KiiT AI Agents system on your local machine.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher**
- **Node.js 16 or higher** (for React frontend)
- **npm or yarn** (comes with Node.js)
- **Git**
- **Gmail account** with App Password enabled
- **API Keys**:
  - Google Generative AI (Gemini) API Key
  - Groq API Key (optional, for some features)
  - OpenAI API Key (optional, for some features)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Agents-KiiT-Management
```

### 2. Set Up Python Backend

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up React Frontend

```bash
cd react-frontend/my-app
npm install
cd ../..
```

## Configuration

### 1. Create Environment File

Copy the example environment file and fill in your actual values:

```bash
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your credentials:

```env
# Email Configuration
EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password

# SMTP/IMAP Configuration (Optional - defaults to Gmail)
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# API Keys (Required)
GOOGLE_API_KEY=your-google-api-key-here
GROQ_API_KEY=your-groq-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# AI Model Configuration (Optional)
GEMINI_MODEL=gemini-1.5-flash
GROQ_MODEL=deepseek-r1-distill-llama-70b

# Database Configuration (Optional)
DATABASE_PATH=students.db

# CORS Configuration - Add your frontend URLs
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Logging (Optional)
LOG_LEVEL=INFO

# Scholarship Criteria (Optional)
SCHOLARSHIP_MIN_CGPA=7.5
SCHOLARSHIP_MIN_ATTENDANCE=75.0

# NOC Criteria (Optional)
NOC_MIN_CGPA=6.0
NOC_MIN_ATTENDANCE=70.0
```

### 3. Obtain API Keys

#### Google Generative AI (Gemini)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to `GOOGLE_API_KEY` in `.env`

#### Gmail App Password

1. Go to your [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification if not already enabled
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a new app password for "Mail"
5. Copy the 16-character password to `EMAIL_PASSWORD` in `.env`

#### Groq API (Optional)

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up and create an API key
3. Copy to `GROQ_API_KEY` in `.env`

## Database Setup

### 1. Create the Database

Run the database creation script:

```bash
cd react-frontend/my-app/backend
python create_db.py
```

This will create a `students.db` file with the required schema.

### 2. Add Sample Data (Optional)

You can manually add student data or import from CSV:

```python
import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO students (name, roll_no, cgpa, attendance, email, department)
    VALUES (?, ?, ?, ?, ?, ?)
""", ("John Doe", "2012345", 8.5, 85.0, "john@example.com", "CSE"))

conn.commit()
conn.close()
```

## Running the Application

### 1. Start the Backend

```bash
cd react-frontend/my-app/backend
uvicorn main_backend:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

### 2. Start the Frontend

In a new terminal:

```bash
cd react-frontend/my-app
npm start
```

The frontend will be available at `http://localhost:3000`

### 3. Access the Application

Open your browser and navigate to `http://localhost:3000`

## Development

### Project Structure

```
AI-Agents-KiiT-Management/
├── config.py                 # Centralized configuration
├── requirements.txt          # Python dependencies
├── utils/                    # Utility modules
│   ├── logger.py            # Logging utilities
│   ├── validation.py        # Input validation
│   └── database.py          # Database utilities
├── -compliance-agents/       # Compliance certificate agents
├── -academic-activities/     # Academic activity agents
├── -placement-agent/         # Placement queries agent
├── -tutor-mentor/           # Tutor-mentor features
└── react-frontend/my-app/   # React frontend
    ├── src/
    │   ├── config.js        # Frontend configuration
    │   ├── elements/        # React components
    │   └── App.jsx          # Main app component
    └── backend/             # FastAPI backend
        ├── main_backend.py  # Main API server
        ├── noc_backend.py   # NOC endpoints
        ├── rank_backend.py  # Rank endpoints
        └── scholarship_backend.py
```

### Adding New Features

1. Create new endpoint in appropriate backend file
2. Add route to frontend config.js
3. Create React component in `src/elements/`
4. Add route in `App.jsx`

### Code Style

- Python: Follow PEP 8
- JavaScript/React: Use ES6+ features
- Use the provided utility modules for common operations

## Troubleshooting

### Backend Issues

#### "Module not found" errors

Make sure you activated the virtual environment:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

#### "GOOGLE_API_KEY is missing"

Check that your `.env` file is in the root directory and contains the correct API key.

#### Database errors

Delete `students.db` and run `create_db.py` again:
```bash
rm students.db
python create_db.py
```

### Frontend Issues

#### "Cannot connect to server"

1. Ensure backend is running on port 8000
2. Check CORS configuration in `.env`
3. Verify `REACT_APP_API_URL` in frontend (if set)

#### Port 3000 already in use

Start on a different port:
```bash
PORT=3001 npm start
```

Don't forget to add `http://localhost:3001` to `ALLOWED_ORIGINS` in `.env`

### Email Issues

#### "Authentication failed"

1. Verify you're using an App Password, not your regular password
2. Ensure 2-Step Verification is enabled on your Google account
3. Check that IMAP is enabled in Gmail settings

#### "No emails found"

1. Check that emails have the correct subject line (e.g., `[BONAFIDE]`)
2. Verify emails are unread
3. Check the correct email account is configured

## Next Steps

- Review the [README.md](README.md) for feature documentation
- Check individual agent files for specific functionality
- Explore the API documentation at `http://localhost:8000/docs` (when backend is running)

## Support

For issues and questions:
- Check existing issues on GitHub
- Review the codebase documentation
- Contact the development team

---

Happy coding! 🚀
