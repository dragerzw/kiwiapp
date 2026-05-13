This project does not yet include Alembic migrations in the repository.

Suggested workflow to apply the schema change made to `Transaction.portfolio_id`:

1. Install alembic (if not already):

   ```bash
   pip install alembic
   ```

2. Initialize alembic in the project root (only if you don't already have a migrations setup):

   ```bash
   alembic init migrations
   ```

3. Configure `migrations/env.py` to use your Flask SQLAlchemy `db` URL or connect string. Adjust `target_metadata` to point at your models metadata: e.g., `from app.db import db; target_metadata = db.metadata`.

4. Generate a revision (autogenerate may detect the change):

   ```bash
   alembic revision --autogenerate -m "Make transaction.portfolio_id nullable and set FK ON DELETE SET NULL"
   ```

5. Inspect the generated migration and ensure it contains commands to ALTER COLUMN to nullable and to modify the FK to ON DELETE SET NULL. If autogenerate couldn't detect FK changes, edit the migration to:

   - ALTER TABLE transaction ALTER COLUMN portfolio_id DROP NOT NULL;
   - Drop existing FK constraint and create a new one with ON DELETE SET NULL.

6. Apply the migration:

   ```bash
   alembic upgrade head
   ```

Notes:
- If you prefer not to use Alembic, you can run raw SQL ALTER statements against your DB to change the FK and nullability.
- Remember to backup your DB before applying schema changes in production.
