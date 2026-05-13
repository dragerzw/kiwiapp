"""Make transaction.portfolio_id nullable for local/dev DBs (handles SQLite dev.db).

This script is intended to be run locally in the project venv. It will:
- detect the SQLALCHEMY_DATABASE_URI from DevelopmentConfig
- if SQLite: create a new `transaction_new` table with `portfolio_id` nullable, copy data, drop old table, rename new
- if other dialect: attempt a safe ALTER (may require manual adjustment)

Run: python scripts/migrate_transaction_portfolio_nullable.py
"""
import sys
from sqlalchemy import create_engine, text
from app.config import DevelopmentConfig

URI = DevelopmentConfig.SQLALCHEMY_DATABASE_URI
print('Using DB URI:', URI)
engine = create_engine(URI)

def migrate_sqlite(conn):
    print('Detected SQLite — running copy/rename migration')
    conn.execute(text('PRAGMA foreign_keys=OFF'))
    try:
        # Check table exists
        r = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='transaction'"))
        if r.fetchone() is None:
            print('transaction table not found — aborting')
            return

        # Create new table with portfolio_id nullable
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS transaction_new (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(30) NOT NULL,
                portfolio_id INTEGER NULL,
                ticker VARCHAR(30) NOT NULL,
                transaction_type VARCHAR(10) NOT NULL,
                quantity INTEGER NOT NULL,
                price FLOAT NOT NULL,
                date_time DATETIME NOT NULL
            );
        '''))

        # Copy data
        conn.execute(text('''
            INSERT INTO transaction_new (transaction_id, username, portfolio_id, ticker, transaction_type, quantity, price, date_time)
            SELECT transaction_id, username, portfolio_id, ticker, transaction_type, quantity, price, date_time FROM transaction;
        '''))

        # Drop old table and rename
        conn.execute(text('DROP TABLE transaction;'))
        conn.execute(text('ALTER TABLE transaction_new RENAME TO transaction;'))

        # (Re)create simple FK if desired — SQLite supports FK syntax but enforcement depends on PRAGMA
        # We'll create a foreign key constraint referencing portfolio(id) with ON DELETE SET NULL
        # SQLite requires rebuilding the table for FK; skipping explicit FK creation here.

        print('Migration completed — portfolio_id is now nullable in the new transaction table')
    finally:
        conn.execute(text('PRAGMA foreign_keys=ON'))


def migrate_other(conn):
    print('Non-SQLite DB detected — attempting ALTER statements. Verify manually after running.')
    try:
        conn.execute(text('ALTER TABLE transaction ALTER COLUMN portfolio_id DROP NOT NULL'))
        conn.execute(text("ALTER TABLE transaction DROP CONSTRAINT IF EXISTS fk_transaction_portfolio_id;"))
        conn.execute(text("ALTER TABLE transaction ADD CONSTRAINT fk_transaction_portfolio_id FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE SET NULL;"))
        print('Attempted ALTER statements — please inspect DB to ensure correctness')
    except Exception as e:
        print('ALTER approach failed:', e)


def main():
    with engine.begin() as conn:
        dialect = engine.dialect.name
        if dialect == 'sqlite':
            migrate_sqlite(conn)
        else:
            migrate_other(conn)

if __name__ == '__main__':
    main()
