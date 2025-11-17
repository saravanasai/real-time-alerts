# Real-Time Alerts API

FastAPI application with PostgreSQL support, fully containerized for local development.

## Quick Start - Local Development

### Prerequisites

- Docker & Docker Compose installed

### Running Locally with Docker

1. **Start the services:**

   ```bash
   docker-compose up
   ```

2. **Access the application:**
   - API: http://localhost:8000
   - API Docs (Swagger UI): http://localhost:8000/docs
   - Database: localhost:5432 (user: root, password: root)

### Hot-Reload

Any changes you make to your Python files will automatically reload the application. Just save your files and refresh the browser.

### Database

- PostgreSQL is running in a separate container
- Connection string: `postgresql://root:root@db:5432/alerts_db`
- Volume: `postgres_data` (persists between restarts)

### Environment Variables

Check `.env` for local development settings. Copy `.env.example` if needed:

```bash
cp .env.example .env
```

### Useful Docker Commands

**Stop containers:**

```bash
docker-compose down
```

**Stop and remove volumes (reset database):**

```bash
docker-compose down -v
```

**View logs:**

```bash
docker-compose logs -f web    # FastAPI logs
docker-compose logs -f db     # PostgreSQL logs
```

**Connect to PostgreSQL:**

```bash
docker-compose exec db psql -U root -d alerts_db
```

**Rebuild after dependency changes:**

```bash
docker-compose up --build
```

## Project Structure

```
├── main.py                 # Entry point
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Services orchestration
├── requirements.txt        # Python dependencies
├── .env                    # Local environment variables
└── app/
    ├── main.py            # FastAPI app instance
    ├── config.py          # Configuration
    ├── routes/            # API endpoints
    │   └── alerts.py
    ├── schemas/           # Pydantic models
    │   └── alerts_sehemas.py
    └── model/             # Database models
```

## Notes

- The `--reload` flag enables hot-reload on file changes
- PostgreSQL health check ensures DB is ready before API starts
- `PYTHONUNBUFFERED=1` ensures real-time log output to Docker
