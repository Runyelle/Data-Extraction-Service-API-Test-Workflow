# Data Extraction Service: Django REST API

A complete Django REST Framework API for extracting data from third-party services, featuring comprehensive test suite, Swagger UI documentation, and production-ready code following Django best practices.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Quick Start Guide](#quick-start-guide)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Server](#running-the-server)
7. [API Documentation](#api-documentation)
8. [Running Tests](#running-tests)
9. [Project Structure](#project-structure)

---

## Overview

This project provides a complete Django REST Framework implementation of a Data Extraction Service API. It includes:

- **Django REST API** - Full implementation of all endpoints
- **PostgreSQL Database** - For storing jobs and extracted records
- **Swagger UI Documentation** - Interactive API documentation
- **Comprehensive Test Suite** - Automated tests for all endpoints
- **Background Job Processing** - Asynchronous data extraction

## Features

- ✅ RESTful API endpoints for data extraction
- ✅ Job status tracking and management
- ✅ Pagination support
- ✅ Error handling and validation
- ✅ Swagger/OpenAPI documentation
- ✅ Comprehensive test coverage
- ✅ Database migrations
- ✅ Admin interface

---

## Quick Start Guide

### What You Need

Before running the project, you need to configure the following in your `.env` file:

1. **Database Configuration** — **REQUIRED**
   - PostgreSQL database credentials
   - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

2. **Django Settings** — **REQUIRED**
   - `SECRET_KEY` - Django secret key
   - `DEBUG` - Set to `True` for development

3. **SERVICE_PROVIDED_API_TOKEN** — **OPTIONAL** (for tests)
   - API token for the third-party service
   - Only needed for real extraction tests

---

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Data-Extraction-Service-API-Test-Workflow
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate    # On Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Database

1. Create a PostgreSQL database:
```bash
createdb extraction_db
```

2. Configure database credentials in `.env` file (see Configuration section)

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

---

## Configuration

1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` and configure the following:

### Required Configuration

- **`SECRET_KEY`** - Django secret key (generate a new one for production)
- **`DEBUG`** - Set to `True` for development, `False` for production
- **`ALLOWED_HOSTS`** - Comma-separated list of allowed hosts
- **`DB_HOST`** - Database hostname (default: `localhost`)
- **`DB_PORT`** - Database port (default: `5432`)
- **`DB_NAME`** - Database name (default: `extraction_db`)
- **`DB_USER`** - Database username (default: `postgres`)
- **`DB_PASSWORD`** - Database password

### Optional Configuration

- **`SERVICE_PROVIDED_API_TOKEN`** - API token for third-party service (for tests)
- **`API_BASE_URL`** - Base URL for API (default: `http://localhost:8000`)

---

## Running the Server

### Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn data_extraction_service.wsgi:application --bind 0.0.0.0:8000
```

---

## API Documentation

### Swagger UI Setup

This project includes **Swagger UI** for interactive API documentation. The Swagger UI is automatically configured and available once the server is running.

**Access the API Documentation:**

1. Start the Django server:
   ```bash
   python manage.py runserver
   ```

2. Open your browser and navigate to:
   - **Swagger UI**: http://localhost:8000/swagger/
   - **ReDoc**: http://localhost:8000/redoc/
   - **OpenAPI JSON Schema**: http://localhost:8000/swagger.json

**Features:**
- Interactive API testing directly from the browser
- Complete endpoint documentation with request/response schemas
- Try-it-out functionality for all endpoints
- Authentication examples
- Response examples and error codes

The Swagger UI is configured using `drf-yasg` and automatically documents all API endpoints defined in the `extraction` app.

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/scan/start` | POST | Start a new extraction job |
| `/api/v1/scan/status/<job_id>` | GET | Get job status |
| `/api/v1/scan/result/<job_id>` | GET | Get extraction results |
| `/api/v1/scan/cancel/<job_id>` | POST | Cancel a job |
| `/api/v1/scan/remove/<job_id>` | DELETE | Remove job data |
| `/api/v1/jobs/jobs` | GET | List all jobs |
| `/api/v1/jobs/statistics` | GET | Get job statistics |

### Example API Request

**Start Extraction:**
```bash
curl -X POST http://localhost:8000/api/v1/scan/start \
  -H "Content-Type: application/json" \
  -d '{"api_token": "your-token-here"}'
```

**Get Job Status:**
```bash
curl http://localhost:8000/api/v1/scan/status/<job_id>
```

---

## Running Tests

### Run All Tests
```bash
pytest -v
```

### Run Specific Test Suites

**Edge Case Tests:**
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

### Run with Detailed Logging
```bash
pytest -v --log-cli-level=INFO
```

---

## Project Structure

```
.
├── data_extraction_service/    # Django project settings
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── extraction/                 # Extraction app
│   ├── models.py              # Database models
│   ├── views.py               # API views
│   ├── serializers.py         # DRF serializers
│   ├── services.py            # Business logic
│   ├── urls.py                # App URLs
│   └── admin.py               # Admin configuration
├── tests/                      # Test suite
│   ├── test_edge_cases.py
│   ├── test_real_extraction.py
│   └── test_seeded_data.py
├── utils/                      # Utility modules
│   ├── api_client.py
│   ├── assertions.py
│   └── database_seeder.py
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
└── README.md                   # This file
```

---

## Database Models

### ExtractionJob
- `job_id` (UUID, Primary Key)
- `connection_id` (UUID)
- `status` (pending, in_progress, completed, failed, cancelled)
- `record_count` (Integer)
- `start_time`, `end_time` (DateTime)
- `error_message` (Text, optional)

### ExtractionRecord
- `id` (AutoField, Primary Key)
- `job` (ForeignKey to ExtractionJob)
- `email`, `first_name`, `last_name` (CharField)
- `id_from_service` (CharField)
- `created_at` (DateTime)

---

## Admin Interface

Access the Django admin interface at: `http://localhost:8000/admin/`

Login with the superuser credentials created during setup.

---

## Troubleshooting

### Database Connection Error

If you encounter database connection errors:

1. Verify PostgreSQL is running: `pg_isready`
2. Check database credentials in `.env`
3. Ensure database exists: `createdb extraction_db`

### Migration Errors

If migrations fail:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Port Already in Use

If port 8000 is already in use:

```bash
python manage.py runserver 8001
```

---

## Summary

**Quick Setup:**
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `env.example` to `.env`: `cp env.example .env`
3. Configure database credentials in `.env`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`
6. Access API documentation: http://localhost:8000/swagger/

**What's Included:**
- ✅ Complete Django REST Framework API
- ✅ PostgreSQL database integration
- ✅ Swagger UI API documentation (configured and ready)
- ✅ Comprehensive test suite
- ✅ Environment configuration template (`.env.example`)
- ✅ Admin interface
- ✅ Background job processing

That's it! Your Django API is ready to use. All endpoints are documented in Swagger UI.
