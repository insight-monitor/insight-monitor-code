# Development Setup

## Prerequisites

```bash
python3 --version   # >= 3.11
node --version      # >= 20
npm --version       # >= 9
```

## Install dependencies

```bash
# Python backend
cd backend
export PATH="$HOME/.local/bin:$PATH"
poetry install
cd ..

# Dashboard
cd frontend
npm install
cd ..

# Root (for concurrently)
npm install
```

## Run everything

```bash
npm run dev
```

| Service | URL | Notes |
|---|---|---|
| Backend API | `http://localhost:8002` | FastAPI with auto-reload |
| Swagger Docs | `http://localhost:8002/docs` | Interactive API documentation |
| Dashboard | `http://localhost:5173` | React dev server, proxies `/api` to backend |

## Load test data

```bash
npm run seed        # Creates 2 sample sessions in SQLite
npm run simulate    # Sends simulated Riwi/BPO events to the API
```

## Scripts reference

| Command | Description |
|---|---|
| `npm run dev` | Start backend + frontend in one terminal |
| `npm run backend` | Start backend only |
| `npm run frontend:dev` | Start frontend only |
| `npm run seed` | Load test sessions into SQLite |
| `npm run simulate` | Simulate Riwi/BPO activity events |
| `npm run frontend:build` | Production build of frontend |
