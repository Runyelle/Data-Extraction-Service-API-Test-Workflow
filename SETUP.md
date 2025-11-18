# Setup Instructions

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start server:**
   ```bash
   python manage.py runserver
   ```

6. **Access API documentation:**
   - Swagger UI: http://localhost:8000/swagger/
   - ReDoc: http://localhost:8000/redoc/

## Database Setup

Make sure PostgreSQL is installed and running:

```bash
# Create database
createdb extraction_db

# Or using psql
psql -U postgres
CREATE DATABASE extraction_db;
```

## Running Tests

```bash
pytest -v
```

