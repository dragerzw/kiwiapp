# Database Migrations

This project includes Alembic migration scripts in `migrations/versions/`, but the full Alembic configuration (e.g., `alembic.ini` and `env.py`) is not currently tracked in the repository.

## Applying Migrations

To apply existing migrations (like the schema change made to `Transaction.portfolio_id`):

1. Install alembic if it is not already in your environment:
   ```bash
   pip install alembic
   ```

2. Initialize your local Alembic setup:
   ```bash
   alembic init migrations
   ```
   *(Note: Do not overwrite the existing `migrations/versions/` directory if prompted).*

3. Configure `migrations/env.py` and `alembic.ini` to connect to your local database instance (e.g., your local `dev.db`).

4. Run the upgrade command to apply the pending migrations:
   ```bash
   alembic upgrade head
   ```

## Creating New Migrations

When you modify your SQLAlchemy models, you should create a new migration script:

1. Generate an automatic revision:
   ```bash
   alembic revision --autogenerate -m "Description of your change"
   ```

2. **Always inspect** the generated migration script in `migrations/versions/` to ensure it correctly captured your schema changes. Sometimes `autogenerate` misses things like constraint changes or renaming columns.

3. Apply your new migration:
   ```bash
   alembic upgrade head
   ```

**Notes:**
- Remember to back up your database before applying schema changes in a production environment.
