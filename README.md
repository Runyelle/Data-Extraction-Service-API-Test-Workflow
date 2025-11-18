# Data Extraction Service: API Test Workflow

This repository contains a comprehensive test suite for the Data Extraction Service API, implementing the testing workflows for validating API behavior, data extraction functionality, and error handling.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start Guide](#quick-start-guide)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running Tests](#running-tests)
6. [Troubleshooting](#troubleshooting)

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

### What You Need

Before running the tests, you need to setup the following in your .env file:

1. **API_BASE_URL** — **REQUIRED**
   - This is the base URL where your Data Extraction Service API is running
   - Examples: 
     - `http://localhost:8000` (if running locally)
     - or (if running on a remote server)
   -You must set for tests to work

2. **SERVICE_PROVIDED_API_TOKEN** — **OPTIONAL** (but recommended)
   - This is the API token for the third-party service you're extracting data from
   - Only needed for real extraction tests
   - Tests will skip real extraction tests if not provided
   - Should be configured in `.env` file

---

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Data-Extraction-Service-API-Test-Workflow
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate    # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Configuration

1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` and configure the following:

### Required Configuration

- **`API_BASE_URL`** - **REQUIRED** - Base URL of the Data Extraction Service API
  - This tells the tests where to find your API server
  - Example: `http://localhost:8000` (if API runs locally)
  - Example: `https://staging-api.example.com` (if API runs on remote server)
  - **You must set this** - tests will fail without it
- **`SERVICE_PROVIDED_API_TOKEN` - API token for the third-party service
  - This is the token for the external service you're extracting data from
  - Only needed for real extraction tests
  - Real extraction tests will be skipped if not provided
  - Example: `pat-na2-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Database credentials** (for seeded data tests only):
  - `DB_HOST`
  - `DB_PORT` (default: 5432)
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`

---

## Running Tests

### Run All Tests
```bash
pytest -v
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

### Run with Detailed Logging
```bash
pytest -v --log-cli-level=INFO
```

### Run a Specific Test
```bash
pytest tests/test_edge_cases.py::TestEdgeCases::test_health_check -v
```

### Common Commands

- **Stop on first failure**: `pytest -x`
- **Show print statements**: `pytest -s`
- **Run in parallel**: `pytest -n auto`

---

## Troubleshooting

### Connection Refused Error

**Error**: `ConnectionRefusedError: [Errno 61] Connection refused`

**Solution**: The API server is not running or not accessible at the configured `API_BASE_URL`.

1. Verify your API is running: `curl http://localhost:8000/api/v1/health`
2. Update `API_BASE_URL` in `.env` if the API is running elsewhere
3. Start the API server if it should be running locally

### Missing Service Provided Token

If real extraction tests are being skipped:
- Ensure `SERVICE_PROVIDED_API_TOKEN` is set in `.env`
- Verify the token is valid and has necessary permissions

### Module Not Found Error

```bash
pip install -r requirements.txt
```

### Test Timeouts

If tests are timing out:
1. Increase `API_TIMEOUT` in `.env`
2. Increase `MAX_POLL_ATTEMPTS` for long-running extractions

---

## Summary

**What You Need:**
1. **API_BASE_URL** (REQUIRED) - The URL where your Data Extraction Service API is running
2. **SERVICE_PROVIDED_API_TOKEN** (OPTIONAL) - The API token for the third-party service

**Quick Setup:**
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `env.example` to `.env`: `cp env.example .env`
3. Edit `.env` and set:
   - `API_BASE_URL=http://your-api-url-here` (REQUIRED)
   - `SERVICE_PROVIDED_API_TOKEN=your-token-here` (OPTIONAL)
4. Run tests: `pytest -v`

That's it! Just plug in your API URL and (optionally) your token, and you're ready to run tests.
