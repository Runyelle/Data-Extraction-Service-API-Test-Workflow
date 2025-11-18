# Data Extraction Service: API Test Workflow

This repository contains a comprehensive test suite for the Data Extraction Service API, implementing the testing workflows for validating API behavior, data extraction functionality, and error handling.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start Guide](#quick-start-guide)
3. [Understanding Key Concepts](#understanding-key-concepts)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running Tests](#running-tests)
7. [API Access Requirements](#api-access-requirements)
8. [Running the API Server](#running-the-api-server)
9. [Test Workflow Documentation](#test-workflow-documentation)
10. [Troubleshooting](#troubleshooting)
11. [Project Structure](#project-structure)
12. [Contributing](#contributing)

---

## Overview

The test suite includes three main categories of tests:

1. **Seeded Data Tests** - Fast, deterministic tests using pre-populated database data
2. **Real Extraction Tests** - End-to-end tests using actual API tokens
3. **Edge Case Tests** - Tests for error handling and boundary conditions

### Prerequisites

- Python 3.8 or higher
- Access to the Data Extraction Service API
- (Optional) Database access for seeded data tests
- (Optional) Valid service provided API token for real extraction tests

---

## Quick Start Guide

### Step 1: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

Or if you prefer using a virtual environment (recommended):

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate    # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your configuration
# At minimum, set API_BASE_URL
```

### Step 3: Run Tests

```bash
# Run all tests
pytest -v

# Run specific test suite (recommended to start with edge cases)
pytest tests/test_edge_cases.py -v
```

---

## Understanding Key Concepts

### What is API_BASE_URL?

**API_BASE_URL** is the base address/URL where your Data Extraction Service API is running. It tells the tests where to find the API server.

**Examples:**
- `http://localhost:8000` - API running on your local machine
- `https://staging-api.example.com` - API running on a remote staging server
- `https://api.example.com` - API running on a remote production server

**How It Works:**

When your test calls an endpoint, the test code constructs the full URL:
```
Full URL = API_BASE_URL + Endpoint Path
```

**Example:**
- **API_BASE_URL**: `http://localhost:8000`
- **Endpoint**: `/api/v1/scan/start`
- **Full URL**: `http://localhost:8000/api/v1/scan/start`

**Note**: The original documentation does NOT explicitly mention API_BASE_URL. It's a configuration detail needed to run the tests.

### What is the API Server?

**Important**: This repository contains **only the test suite** for the Data Extraction Service API. The actual API server code is in a **separate repository/project**.

#### Visual Explanation

```
┌─────────────────────────────────────┐
│   API SERVER (The Application)      │
│   - Receives requests               │
│   - Processes data extraction       │
│   - Returns responses               │
│   - Runs on http://localhost:8000   │
└─────────────────────────────────────┘
              ▲
              │ HTTP Requests
              │ (GET, POST, DELETE)
              │
┌─────────────────────────────────────┐
│   TEST SUITE (What You Have)        │
│   - Sends requests                  │
│   - Validates responses             │
│   - Checks for errors               │
│   - This repository!                │
└─────────────────────────────────────┘
```

#### What the API Server Contains

The API server codebase typically includes:
- Server application code (Python, Node.js, Java, etc.)
- API endpoints implementation (all the `/api/v1/*` endpoints)
- Business logic (data extraction, job management)
- Configuration files (`requirements.txt`, `package.json`, `docker-compose.yml`)

#### Where Might It Be?

1. **Separate Git Repository** - Different repository name
2. **Different Directory** - On your local machine
3. **Already Running Somewhere** - Remote server, Docker container
4. **You Need to Build It** - May need to clone or set up

See [Running the API Server](#running-the-api-server) section for more details.

---

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Data-Extraction-Service-API-Test-Workflow
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

---

## Configuration

Create a `.env` file in the root directory with the following variables:

### Required Configuration

- **`API_BASE_URL`** - Base URL of the Data Extraction Service API (e.g., `http://localhost:8000`)
  - This is the address where your API server is running
  - Can be local (`http://localhost:8000`) or remote (`https://api.example.com`)

### Optional Configuration

#### For Seeded Data Tests
- `DB_HOST` - Database hostname
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password

**Note**: If database credentials are not provided, seeded data tests will attempt to use API endpoints for data setup, or you may need to manually seed data.

#### For Real Extraction Tests
- `SERVICE_PROVIDED_API_TOKEN` - Valid API token for the third-party service

**Note**: Real extraction tests will be skipped if this token is not provided.

#### Test Configuration
- `API_TIMEOUT` - Request timeout in seconds (default: 30)
- `POLL_INTERVAL_SECONDS` - Interval between status polls (default: 5)
- `MAX_POLL_ATTEMPTS` - Maximum polling attempts (default: 120)
- `TEST_DATA_CLEANUP` - Automatically cleanup test data (default: true)

---

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Detailed Logging
```bash
pytest -v --log-cli-level=INFO
```

### Run Specific Test Suites

**Edge Case Tests (Recommended to start here - fastest):**
```bash
pytest tests/test_edge_cases.py -v
```

**Seeded Data Tests:**
```bash
pytest tests/test_seeded_data.py -v
```

**Real Extraction Tests:**
```bash
pytest tests/test_real_extraction.py -v
```

### Run a Specific Test
```bash
pytest tests/test_edge_cases.py::TestEdgeCases::test_health_check -v
```

### Common Commands

- **Stop on first failure**: `pytest -x`
- **Show print statements**: `pytest -s`
- **Run in parallel**: `pytest -n auto`
- **Test coverage**: `pytest --cov=. --cov-report=html`

### Understanding Test Output

- **PASSED** - Test completed successfully
- **FAILED** - Test encountered an error
- **SKIPPED** - Test was skipped (e.g., missing token/DB configuration)

---

## API Access Requirements

### 1. Data Extraction Service API

**Status**: ✅ Required for all tests

**Base URL**: Configure via `API_BASE_URL` in `.env`

**Endpoints Used**:
- `POST /api/v1/scan/start` - Start extraction jobs
- `GET /api/v1/scan/status/<job_id>` - Get job status
- `GET /api/v1/scan/result/<job_id>` - Get extraction results
- `POST /api/v1/scan/cancel/<job_id>` - Cancel jobs
- `DELETE /api/v1/scan/remove/<job_id>` - Remove job data
- `GET /api/v1/jobs/jobs` - List all jobs
- `GET /api/v1/jobs/statistics` - Get job statistics
- `GET /api/v1/health` - Health check

### 2. Database API (for Seeded Data Tests)

**Status**: ⚠️ Optional - Required only for seeded data tests

**Options**:

#### Option A: Direct Database Access (Recommended)
- **Type**: PostgreSQL database connection
- **Configuration**: Set database credentials in `.env`
- **Required Permissions**: INSERT, UPDATE, DELETE on `extraction_jobs` and `extraction_records` tables

#### Option B: API-Based Seeding
- Modify `utils/database_seeder.py` to use API endpoints for seeding
- Or manually seed data before running tests

### 3. Service Provided API Token (for Real Extraction Tests)

**Status**: ⚠️ Optional - Required only for real extraction tests

**Configuration**: Set `SERVICE_PROVIDED_API_TOKEN` in your `.env` file

**Token Requirements**:
- Valid API token for the third-party service
- Token must have necessary permissions to access and extract data
- Consider using a dedicated test account

### Test Suite Behavior by Configuration

| Configuration | Seeded Data Tests | Real Extraction Tests | Edge Case Tests |
|--------------|-------------------|----------------------|-----------------|
| API_BASE_URL only | ⚠️ May fail (no data) | ❌ Skipped | ✅ Works |
| API_BASE_URL + DB | ✅ Works | ❌ Skipped | ✅ Works |
| API_BASE_URL + Token | ⚠️ May fail (no data) | ✅ Works | ✅ Works |
| API_BASE_URL + DB + Token | ✅ Works | ✅ Works | ✅ Works |

---

## Running the API Server

### Important Note

This repository contains **only the test suite**. The actual API server code is in a **separate repository/project**.

### Finding Your API Server

The API server code is typically located in:
1. **Separate Repository** - Different Git repository
2. **Different Directory** - On your local machine
3. **Docker Container** - Running in Docker/Docker Compose
4. **Remote Server** - Already running on staging/production

### Common Ways to Run API Servers

#### Python/FastAPI/Flask Server

```bash
# Navigate to API server directory
cd /path/to/your/api/server

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
# OR
uvicorn main:app --host 0.0.0.0 --port 8000
# OR
flask run --port 8000
```

#### Node.js/Express Server

```bash
# Navigate to API server directory
cd /path/to/your/api/server

# Install dependencies
npm install

# Run the server
npm start
# OR
node server.js
```

#### Docker/Docker Compose

```bash
# Navigate to API server directory
cd /path/to/your/api/server

# Run with Docker Compose
docker-compose up
```

### Verifying the API is Running

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Should return something like:
# {"status": "ok"}
```

### Common Ports

- `8000` (default in your tests)
- `3000` (common for Node.js)
- `5000` (common for Flask)
- `8080` (common alternative)

If your API runs on a different port, update `.env`:
```bash
API_BASE_URL=http://localhost:YOUR_PORT
```

### Alternative: Use Remote API

If you have access to a remote/staging API, update `.env`:
```bash
API_BASE_URL=https://staging-api.example.com
```

---

## Test Workflow Documentation

### Test Types Overview

| Test Type | Description | Primary Use Case |
|-----------|-------------|------------------|
| Seeded Data Tests | Utilizes predefined data inserted directly into the test database for controlled, fast, and isolated tests. | Validating internal API logic, data processing, and business rules without external dependencies. |
| Real Extraction Tests | Employs actual API tokens for the service provided to trigger live data extractions, validating real-time integration. | Ensuring end-to-end integration, authentication, and data mapping with the external service provided API. |
| Edge Case Tests | Focuses on validating the API's behavior when confronted with invalid inputs, unexpected states, or boundary conditions. | Guaranteeing API robustness, proper error handling, and a predictable response to abnormal scenarios. |

### Workflow Steps for Seeded Data Tests

1. **Setup Environment and Data**: Initialize a clean test database and seed with pre-defined extraction job records
2. **Verify Job Status**: Query status endpoint for seeded jobs
3. **Fetch Extraction Results**: Retrieve results for completed jobs
4. **List All Jobs**: Verify all seeded jobs appear in the list
5. **Retrieve Job Statistics**: Verify statistics reflect seeded data
6. **Health Check**: Verify service reports healthy status
7. **Cancel a Pending Job**: Test job cancellation
8. **Remove Job Data**: Test data removal

### Workflow Steps for Real Extraction Tests

1. **Prepare Valid Credentials**: Ensure valid API token is available
2. **Start New Extraction**: Send POST request to start extraction
3. **Poll Job Status**: Poll until job completes or fails
4. **Retrieve Extracted Results**: Get results once job is completed
5. **Remove Extraction Data**: Clean up test data

### Common Assertions and Validations

- **HTTP Status Codes**: Validate expected status codes (200, 202, 400, 404, etc.)
- **Job Status Transitions**: Verify valid state transitions
- **Response Body Content**: Validate data structure, completeness, and correctness
- **Pagination**: Verify pagination works correctly
- **Error Messages**: Ensure meaningful error messages
- **Performance**: Basic response time assertions
- **Health Status**: Verify health endpoint returns valid status

### API Endpoints Tested

| Endpoint | HTTP Method | Tested In | Description |
|----------|-------------|-----------|-------------|
| `/api/v1/scan/start` | POST | Real Extraction Test, Edge Case Test | Initiates a new data extraction job |
| `/api/v1/scan/status/<job_id>` | GET | Both Tests, Edge Case Test | Retrieves job status and progress |
| `/api/v1/scan/result/<job_id>` | GET | Both Tests, Edge Case Test | Fetches extracted data for completed job |
| `/api/v1/scan/cancel/<job_id>` | POST | Seeded Data Test, Edge Case Test | Cancels a pending or in-progress job |
| `/api/v1/scan/remove/<job_id>` | DELETE | Both Tests, Edge Case Test | Deletes stored extraction data |
| `/api/v1/jobs/jobs` | GET | Seeded Data Test | Lists all extraction jobs |
| `/api/v1/jobs/statistics` | GET | Seeded Data Test | Provides aggregated statistics |
| `/api/v1/health` | GET | Both Tests | Checks operational status |

### Edge Cases Tested

- Invalid or missing API tokens
- Non-existent job IDs
- Accessing results for incomplete jobs
- Cancelling completed or failed jobs
- Concurrent requests for the same extraction
- Large data volumes / pagination stress
- Service provided API downtime/errors
- Malformed request bodies
- ID injection/manipulation attempts
- Rate limiting from the service provided

---

## Troubleshooting

### Connection Refused Error

**Error**: `ConnectionRefusedError: [Errno 61] Connection refused`

**Root Cause**: The Data Extraction Service API is not running or not accessible at the configured `API_BASE_URL`.

**Solutions**:
1. **Start the API server** (if running locally)
2. **Update API_BASE_URL** in `.env` if API is running elsewhere
3. **Verify connectivity**: `curl http://localhost:8000/api/v1/health`

### Database Connection Issues

If you encounter database connection errors for seeded data tests:

1. Verify your database credentials in `.env`
2. Ensure the database is accessible from your test environment
3. Check that the database schema matches the expected structure
4. Consider using API endpoints for data seeding instead

### Missing Service Provided Token

If real extraction tests are being skipped:

1. Ensure `SERVICE_PROVIDED_API_TOKEN` is set in `.env`
2. Verify the token is valid and has necessary permissions
3. Check that the token format matches what the API expects

### Test Timeouts

If tests are timing out:

1. Increase `API_TIMEOUT` in `.env`
2. Increase `MAX_POLL_ATTEMPTS` for long-running extractions
3. Adjust `POLL_INTERVAL_SECONDS` based on expected job duration

### Module Not Found Error

```bash
pip install -r requirements.txt
```

---

## Project Structure

```
.
├── config.py                 # Configuration management
├── conftest.py              # Pytest fixtures and configuration
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
├── .env.example            # Example environment variables
├── README.md               # This file
├── utils/
│   ├── __init__.py
│   ├── api_client.py       # API client for making requests
│   ├── assertions.py       # Common assertions and validations
│   └── database_seeder.py  # Database seeding utilities
└── tests/
    ├── __init__.py
    ├── test_seeded_data.py    # Seeded data test suite
    ├── test_real_extraction.py # Real extraction test suite
    └── test_edge_cases.py     # Edge case test suite
```

### Test Coverage

**Seeded Data Tests**:
- Health check validation
- Job status verification (pending, completed, cancelled)
- Extraction result retrieval
- Pagination testing
- Job listing and filtering
- Statistics retrieval
- Job cancellation
- Job data removal

**Real Extraction Tests**:
- Starting new extractions
- Polling job status until completion
- Retrieving extracted results
- Pagination for large result sets
- Job status transitions
- Data cleanup

**Edge Case Tests**:
- Invalid or missing API tokens
- Non-existent job IDs
- Accessing results for incomplete jobs
- Cancelling completed jobs
- Malformed request bodies
- SQL injection attempts
- Invalid pagination parameters
- Special character handling

### Database Schema Requirements

If you're using direct database access for seeded data tests, your database should have the following tables (adjust as needed based on your actual schema):

```sql
CREATE TABLE extraction_jobs (
    job_id VARCHAR PRIMARY KEY,
    connection_id VARCHAR,
    status VARCHAR NOT NULL,
    record_count INTEGER DEFAULT 0,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE extraction_records (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR REFERENCES extraction_jobs(job_id),
    email VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    id_from_service VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Note**: If your schema differs, you'll need to update `utils/database_seeder.py` accordingly.

---

## Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Use the provided utilities (`APIClient`, `APIAssertions`, etc.)
3. Ensure proper cleanup of test data
4. Update this README if adding new configuration options
5. Add appropriate docstrings and comments

---

## Security Notes

- **Never commit `.env` files** to version control
- Store API tokens securely
- Use test/dedicated accounts for testing, not production accounts
- Rotate tokens regularly
- Follow your organization's security policies for credential management

---

## Support

For questions or issues, please contact the development team or create an issue in the repository.

---

## License

[Add your license information here]
