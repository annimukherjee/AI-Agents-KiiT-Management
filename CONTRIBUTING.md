# Contributing to KiiT AI Agents

Thank you for your interest in contributing to the KiiT AI Agents project! This document provides guidelines and best practices for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the project and community

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Follow the [SETUP.md](SETUP.md) guide to set up your development environment
4. Create a new branch for your feature: `git checkout -b feature/your-feature-name`

## Development Guidelines

### Code Style

#### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep functions focused and small (< 50 lines when possible)
- Use meaningful variable and function names

Example:
```python
def validate_student_data(name: str, roll_no: str) -> Tuple[bool, Optional[str]]:
    """
    Validate student data before processing.

    Args:
        name: Student name
        roll_no: Student roll number

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Implementation
```

#### JavaScript/React

- Use ES6+ features (arrow functions, destructuring, etc.)
- Use functional components with hooks
- Keep components small and focused
- Use meaningful component and variable names
- Follow consistent formatting (use Prettier if available)

Example:
```javascript
const StudentCard = ({ name, rollNo, cgpa }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="student-card">
      {/* Component JSX */}
    </div>
  );
};
```

### Security Best Practices

1. **Never commit sensitive data**:
   - No API keys in code
   - No passwords in code
   - Use `.env` files (already in `.gitignore`)

2. **Input Validation**:
   - Always validate user input
   - Use the utilities in `utils/validation.py`
   - Sanitize file paths and names

3. **SQL Safety**:
   - Always use parameterized queries
   - Never use string concatenation for SQL
   - Use the database utilities in `utils/database.py`

4. **API Security**:
   - Validate all API inputs
   - Use proper HTTP methods (GET for reading, POST for writing)
   - Return appropriate status codes

### Using Utility Modules

Always use the provided utility modules instead of duplicating code:

```python
# ✅ Good - Use utilities
from utils.logger import setup_logger
from utils.validation import validate_email, validate_cgpa
from utils.database import get_db_connection, get_student_info

logger = setup_logger(__name__, "bonafide")

if not validate_email(email):
    logger.error(f"Invalid email: {email}")
    return

student = get_student_info(roll_no)
```

```python
# ❌ Bad - Don't duplicate
import sqlite3
conn = sqlite3.connect('students.db')
# Manual validation without using utilities
```

### Configuration Management

Always use the centralized `config.py`:

```python
# ✅ Good
from config import API_KEYS, EMAIL_CONFIG, DATABASE_CONFIG

genai.configure(api_key=API_KEYS["google"])
```

```python
# ❌ Bad
import os
api_key = os.getenv("GOOGLE_API_KEY")
```

### Error Handling

Always handle errors gracefully:

```python
from utils.logger import setup_logger

logger = setup_logger(__name__)

try:
    # Your code
    result = process_data(data)
except ValueError as e:
    logger.error(f"Validation error: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Adding New Features

### Backend (FastAPI)

1. Create endpoint in appropriate backend file (`noc_backend.py`, etc.)
2. Use proper HTTP methods and status codes
3. Add request/response models using Pydantic
4. Add error handling and logging
5. Test the endpoint manually

Example:
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.logger import setup_logger
from utils.validation import validate_roll_number

router = APIRouter(prefix="/feature", tags=["feature"])
logger = setup_logger(__name__, "feature")

class FeatureRequest(BaseModel):
    roll_no: str
    data: str

@router.post("/process")
async def process_feature(request: FeatureRequest):
    try:
        if not validate_roll_number(request.roll_no):
            raise HTTPException(status_code=400, detail="Invalid roll number")

        # Process request
        logger.info(f"Processing feature for {request.roll_no}")
        result = process_data(request.data)

        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error processing feature: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### Frontend (React)

1. Add endpoint to `src/config.js`
2. Create component in `src/elements/`
3. Add route in `App.jsx`
4. Use consistent styling with existing components

Example `config.js`:
```javascript
export const API_ENDPOINTS = {
  // ... existing endpoints
  newFeature: `${API_BASE_URL}/feature/process`,
};
```

Example component:
```javascript
import { useState } from 'react';
import API_ENDPOINTS from '../config';

function NewFeature() {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.newFeature, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: 'example' })
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const result = await response.json();
      setMessage({ text: result.message, isError: false });
    } catch (err) {
      setMessage({ text: err.message, isError: true });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="material-card">
      {/* Component JSX */}
    </div>
  );
}

export default NewFeature;
```

## Testing

Before submitting a pull request:

1. Test your changes locally
2. Ensure no console errors in browser
3. Test error cases (invalid input, network errors, etc.)
4. Verify changes work with actual email/API integration
5. Check that existing features still work

## Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body (optional)>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: Add scholarship eligibility validation

Added validation utilities for CGPA and attendance.
Updated scholarship backend to use new validation.
```

```
fix: Resolve CORS issue in main backend

Updated CORS configuration to use centralized config
instead of allowing all origins.
```

```
docs: Add comprehensive setup guide

Created SETUP.md with installation, configuration,
and troubleshooting sections.
```

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Update documentation if needed
3. Test your changes thoroughly
4. Create a pull request with:
   - Clear title describing the change
   - Description of what changed and why
   - Screenshots (if UI changes)
   - Related issue numbers (if applicable)

5. Be responsive to code review feedback
6. Ensure all checks pass

## Questions?

If you have questions:
- Check existing documentation (README.md, SETUP.md)
- Review existing code for patterns
- Open an issue for clarification

Thank you for contributing! 🎉
