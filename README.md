# Clear AI Backend

## Production Deployment

The backend is deployed on Render and can be accessed at:

```
https://clear-edi-backend.onrender.com/
```

API Documentation:

- Swagger UI (Recommended): https://clear-edi-backend.onrender.com/docs
- ReDoc: https://clear-edi-backend.onrender.com/redoc

## Local Development Guide

### Requirements

- Python 3.8 or higher
- MongoDB (for local development)

### Quick Start

1. Get the code:

   ```bash
   # Option 1: Clone the repository
   git clone https://github.com/PhoebeHuHu/clear-backend
   # OR
   # Option 2: Extract the downloaded zip file

   # Enter project directory
   cd clear-backend
   ```

2. Create and activate virtual environment:

   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   # Install all development dependencies
   pip install -r requirements-dev.txt
   ```

4. Configure environment variables:

   ```bash
   # Copy environment variables example file
   cp .env.example .env

   # Edit .env file and set necessary variables:
   # - MONGODB_URL: MongoDB connection string
   # - Other required configurations...
   ```

5. Start the server:
   ```bash
   # Start development server (with hot reload)
   uvicorn app.main:app --reload --port 8000
   ```

After starting the server, you can access:

- API Documentation: http://localhost:8000/docs
- API Service: http://localhost:8000

## Project Structure

```
clear-backend/
├── app/                    # Main application directory
│   ├── api/
│   │   └── v1/           # API routes and endpoints
│   ├── models/           # Data models definition
│   ├── services/        # Business logic layer
│   ├── db/             # Database related code
│   ├── utils/          # Utility functions
│   ├── constants/      # Constants definition
│   ├── config.py       # Application configuration
│   └── main.py         # Application entry point
├── requirements.txt     # Production dependencies
└── requirements-dev.txt # Development dependencies
```

### Core Files Description

- `app/main.py`: Application entry point containing FastAPI app instance and basic configuration
- `app/api/`: Contains all API endpoint definitions and route handlers
- `app/models/`: Defines data models and database schemas
- `app/services/`: Contains core business logic implementation
- `app/db/`: Database connection and operation related code
- `requirements.txt`: Dependencies required for production
- `.env`: Environment variables configuration file (needs to be created)

## Common Issues

If you encounter startup issues, please check:

1. MongoDB is running properly
2. Environment variables are correctly configured
3. All dependencies are properly installed

## API Documentation Guide

When developing locally, you can view the API documentation at:

- Swagger UI (Recommended): http://localhost:8000/docs
  - Provides interactive API testing interface
  - Test APIs directly in the browser
- ReDoc: http://localhost:8000/redoc
  - Provides clearer documentation reading experience
  - Includes detailed request/response examples

## Running Tests

To run the test suite:

```bash
# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest -v

# Run tests with coverage report
python -m pytest --cov=app

# Run a specific test file
python -m pytest app/tests/your_test_file.py

# Run tests matching specific pattern
python -m pytest -k "test_pattern"
```

Test files are located in the `app/tests/` directory. Each module has its corresponding test file.

### Test Configuration

The test configuration is defined in `pytest.ini` and uses a separate test database to avoid affecting your development database.
