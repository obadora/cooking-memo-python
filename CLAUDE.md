# CLAUDE.md
必ず日本語で回答してください。
This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Start all services (FastAPI + MySQL) with Docker Compose
docker-compose up

# The FastAPI server runs on http://localhost:8000
# MySQL runs on port 33306 (mapped from container port 3306)
```

### Database Management
```bash
# Run database migrations
docker-compose exec workspace poetry run python src/migrate_db.py

# Access MySQL CLI
docker-compose exec db mysql -u root -p
```

### Dependency Management
```bash
# Install dependencies (inside container)
docker-compose exec workspace poetry install

# Add new dependency
docker-compose exec workspace poetry add <package_name>
```

## Architecture Overview

This is a FastAPI-based recipe scraping and management application with the following structure:

### Core Architecture
- **FastAPI** web framework with async support
- **SQLAlchemy** ORM with async MySQL driver (aiomysql)
- **Docker Compose** for container orchestration
- **Poetry** for Python dependency management

### Directory Structure
```
src/
├── main.py           # FastAPI app entry point
├── db.py            # Database connection and session management
├── migrate_db.py    # Database migration script
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response schemas
├── cruds/           # Database CRUD operations
├── routers/         # FastAPI route handlers
└── services/        # Business logic (scraping, etc.)
```

### Key Components

**Database Layer** (`src/db.py`):
- Async SQLAlchemy engine with aiomysql driver
- Session management with dependency injection
- Environment-based configuration for database connection

**API Layer** (`src/routers/recipe.py`):
- Recipe CRUD endpoints: GET, POST, DELETE
- Recipe scraping endpoint that either creates new recipe or returns existing
- Cooking record management

**Data Models** (`src/models/recipe.py`):
- Recipe entity with ingredients, steps, and cooking records
- Relationships between recipes and cooking history

**Scraping Service** (`src/services/scrape.py`):
- Web scraping functionality for recipe data extraction
- Integration with recipe creation workflow

### Environment Setup
- Uses `.env` file for database credentials
- Environment variables: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_ROOT_PASSWORD`
- CORS configured for React frontend on `http://localhost:5173`

### Database Schema
- MySQL 8.0 with initial schema in `docker-entrypoint-initdb.d/01_create_tables.sql`
- Test data setup in `docker-entrypoint-initdb.d/02_test_user.sql`

## Development Notes

- Application runs in development mode with `--reload` flag
- Database uses MySQL native password authentication
- All database operations are async using SQLAlchemy's async session
- Recipe scraping checks for existing recipes by source URL to avoid duplicates