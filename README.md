# Movie Rating System - Docker Setup

## Overview
A FastAPI-based Movie Rating System containerized with Docker and Docker Compose.

## Prerequisites
- Docker Engine
- Docker Compose
- Git

## Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/SahellSabetii/movie-rating-system
cd movie-rating-system

# Copy environment configuration
cp .env.example .env
```

### 2. Configure Environment
Edit the `.env` file to set your database credentials:
```env
POSTGRES_DB=movie_rating_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql://movie_user:your_password@db:5432/movie_rating_db
DEBUG=true
```

### 3. Start the Application
```bash
# Build and start all services
docker compose up --build

# Or run in background
docker compose up -d --build
```

### 4. Access the Application
- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc Documentation**: http://localhost:8000/api/redoc

## Available Services

### 1. Application (FastAPI)
- **Container**: `movie_rating_app`
- **Port**: 8000

### 2. Database (PostgreSQL)
- **Container**: `movie_rating_db`
- **Port**: 5432
- **Volume**: Persistent data storage
- **Health Check**: Automatic connection verification

## Development Commands

### Using Docker Compose
```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs
docker compose logs -f app      # Follow app logs
docker compose logs db         # View database logs

# Check service status
docker compose ps

# build images and run
docker compose up --build
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `movie_rating_db` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | (required) |
| `DATABASE_URL` | Full database connection URL | Constructed from above |
| `DEBUG` | Debug mode | `true` |

## Troubleshooting

### Common Issues

#### 1. "Database is unavailable" error
```bash
# Check if database is running
docker compose ps

# View database logs
docker compose logs db

# Wait for database to be ready, then restart app
docker compose restart app
```

#### 2. Port already in use
```bash
# Check what's using port 8000 or 5432
lsof -i :8000
lsof -i :5432

# Change ports in docker-compose.yml if needed
```

#### 3. Docker build failures
```bash
# Clear Docker cache
docker compose build --no-cache

# Remove unused Docker resources
docker system prune -f
```

#### 4. Alembic migration errors
```bash
# Check current migration state
docker compose exec app alembic current

# Downgrade and re-apply
docker compose exec app alembic downgrade -1
docker compose exec app alembic upgrade head
```

### Logs and Debugging
```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs app
docker compose logs db

# Follow logs in real-time
docker compose logs -f

# Check container health
docker compose exec db pg_isready -U postgres
```

## Contributing

### Setup Development Environment
1. Fork and clone the repository
2. Copy `.env.example` to `.env`
3. Update `.env` with your settings
4. Run `docker compose up --build`
5. Access the API at `http://localhost:8000/docs`

### Testing Changes
1. Make your changes
2. Test locally using the API documentation
3. Run migrations if database changes were made
4. Commit and push changes

---

Developer: Sahel Sabeti

