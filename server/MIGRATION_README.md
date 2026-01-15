# Database Migration System

This project now includes a robust database migration system to handle schema mismatches between cloud and local environments.

## Features

1. **Automatic Schema Detection**: Detects when the database schema doesn't match the Python models
2. **Data Preservation**: Backs up existing data before schema changes
3. **Smart Merging**: Merges data from old tables to new tables based on common columns
4. **Professional Migrations**: Uses Alembic for advanced migration scenarios

## How It Works

When connecting to the database, the system:
1. Checks if tables exist and match expected schema
2. Detects any missing or extra columns
3. Automatically backs up existing tables if changes are needed
4. Applies schema updates while preserving existing data
5. Logs all migration activities for troubleshooting

## Usage

The migration happens automatically when you call `get_session()` or start the application. For manual control:

```bash
# To create new migrations when changing models:
cd server && python -m alembic revision --autogenerate -m "Description of changes"

# To apply migrations:
cd server && python -m alembic upgrade head
```

## Files Added/Modified

- `server/db.py`: Enhanced with migration logic
- `server/requirements.txt`: Added alembic dependency
- `server/alembic.ini`: Alembic configuration
- `server/migrations/`: Alembic migration directory
- `server/migrations/env.py`: Connects Alembic to our models
- `server/migrations/versions/`: Contains migration scripts
