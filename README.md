# HTTP Metadata Inventory (Django REST + MongoDB)

Implements the hiring challenge requirements with Django REST Framework instead of FastAPI while preserving all specified behaviors:

- `POST /api/metadata/` collects headers, cookies, and page source for a URL and stores it in MongoDB.
- `GET /api/metadata/?url=...` returns stored metadata immediately when present.
- On cache miss, `GET` returns `202 Accepted` immediately and triggers internal asynchronous background collection.

## Tech Stack

- Python 3.11+
- Django 5 + Django REST Framework
- MongoDB (PyMongo)
- Docker Compose
- Pytest

## Run With Docker Compose

```bash
docker-compose up --build
```

Services:

- API: `http://localhost:8000`
- MongoDB: `mongodb://localhost:27017`

## API Usage

### POST metadata collection

```bash
curl -X POST http://localhost:8000/api/metadata/ \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

### GET metadata by URL

```bash
curl "http://localhost:8000/api/metadata/?url=https://example.com"
```

Possible outcomes:

- `200 OK` with full metadata when found in inventory.
- `202 Accepted` when missing; background collection has been queued.

## Local Development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings
python manage.py runserver 0.0.0.0:8000
```

Set `MONGO_URI` to a reachable MongoDB instance before running locally.

## Tests

```bash
pytest -q
```

The test suite validates:

- URL normalization and validation logic
- POST behavior (collect and persist)
- GET behavior for hit and miss
- Async scheduling trigger on GET miss
- Error handling for invalid URL input

## Architecture Notes

- `metadata_service/views.py`: transport layer (HTTP, status codes)
- `metadata_service/services.py`: business orchestration and validation
- `metadata_service/repository.py`: Mongo access and indexing
- `metadata_service/schemas.py`: URL/document contract and Mongo field definitions
- `metadata_service/collector.py`: outbound HTTP metadata collection
- `metadata_service/background.py`: in-process async worker scheduling

The background inventory update is handled internally via a `ThreadPoolExecutor`, with de-duplication of in-flight URL tasks and no self-referential HTTP calls.
