# Clear AI Backend

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

1. Clone the repository:

```bash
git clone [your-repository-url]
cd clear-backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up the test database:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - The `.env` file already contains a test MongoDB connection string that you can use directly

### Project Structure

```
app/
├── api/                    # API endpoints
│   └── v1/                # API version 1
├── constants/             # Constants and enums
├── db/                    # Database related code
├── models/                # Database models
├── schemas/               # Pydantic schemas for request/response
├── services/              # Business logic
├── tests/                 # Test files
└── utils/                 # Utility functions
```

Key files:

- `main.py`: Application entry point and FastAPI app configuration
- `config.py`: Application configuration
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (not in version control)
- `.env.example`: Example environment variables
- `pytest.ini`: Pytest configuration

### Running Tests

Run the test suite:

```bash
# On Windows
python -m pytest
# Or use pytest directly if it's in your PATH
pytest

# On macOS/Linux
python -m pytest
# Or use pytest directly if it's in your PATH
pytest

# To run with verbose output
python -m pytest -v

# To run a specific test file
python -m pytest app/tests/test_specific_file.py

# To run tests with coverage report
python -m pytest --cov=app
```

### Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

### API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI (Interactive): http://localhost:8000/docs
- ReDoc (Alternative): http://localhost:8000/redoc

The documentation provides:

- Detailed API endpoints information
- Request/response schemas
- Interactive testing interface
- Example requests and responses
