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

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
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

### API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI (Interactive): http://localhost:8000/docs
- ReDoc (Alternative): http://localhost:8000/redoc

The documentation provides:

- Detailed API endpoints information
- Request/response schemas
- Interactive testing interface
- Example requests and responses
