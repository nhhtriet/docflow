# DocFlow

Monorepo containing a FastAPI backend and React frontend for a simple document management flow.

## Development

### Requirements
- Docker & Docker Compose

### Setup

1. Copy `.env.example` to `.env` and adjust values if needed.
2. Build and start services:
   ```bash
   docker compose up --build
   ```
3. The API will be available at `http://localhost:8000` and the frontend at `http://localhost:5173`.

## Testing

Backend tests use `pytest`:
```bash
cd backend
pytest -q
```

## Endpoints

- `POST /auth/login` – Dummy login endpoint.
- `GET /documents` – List documents.
- `POST /documents` – Create document (in-memory).
