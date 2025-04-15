# Clear AI Backend

## Production Deployment

The backend is deployed on Render and can be accessed at:

```
https://clear-edi-backend.onrender.com/
```

API documentation is available at:

- Swagger UI: https://clear-edi-backend.onrender.com/docs
- ReDoc: https://clear-edi-backend.onrender.com/redoc

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB (for local development)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/PhoebeHuHu/clear-backend
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

3. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

For production environments, use:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```

5. Set up pre-commit hooks:

```bash
pre-commit install
```

This will automatically run tests and linting checks before each commit.

### Development Workflow

#### Managing Dependencies

The project uses `pip-tools` for dependency management:

- `requirements.in`: Contains direct production dependencies
- `requirements-dev.in`: Contains development dependencies
- `requirements.txt` and `requirements-dev.txt`: Generated files with pinned versions

To add new dependencies:

1. Add them to the appropriate `.in` file
2. Compile new requirements:
   ```bash
   pip-compile requirements.in
   pip-compile requirements-dev.in
   ```
3. Install updated dependencies:
   ```bash
   pip-sync requirements-dev.txt
   ```

#### Code Quality

The project uses several tools to maintain code quality:

- **Ruff**: For linting and formatting
- **pre-commit**: Runs checks before each commit
- **pytest**: For testing

These checks run automatically on commit, but you can also run them manually:

```bash
# Format and lint code
ruff check .
ruff format .

# Run tests
pytest
```

### Running Locally

1. Make sure your MongoDB instance is running

2. Start the FastAPI server:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

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
- `requirements.in`: Direct production dependencies
- `requirements-dev.in`: Development dependencies
- `requirements.txt`: Generated production dependencies with versions
- `requirements-dev.txt`: Generated development dependencies with versions
- `.env`: Environment variables (not in version control)
- `.env.example`: Example environment variables
- `.pre-commit-config.yaml`: Pre-commit hook configuration
- `pytest.ini`: Pytest configuration

### Running Tests

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest app/tests/test_specific_file.py

# Run tests with coverage report
pytest --cov=app
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
