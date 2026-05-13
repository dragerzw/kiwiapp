"""Make transaction.portfolio_id nullable and set FK ON DELETE SET NULL

Revision ID: 0001_make_transaction_portfolio_nullable
Revises: 
Create Date: 2026-05-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_make_transaction_portfolio_nullable'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing FK (name may vary per DB); replace with the correct constraint name if necessary.
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    fks = inspector.get_foreign_keys('transaction')
    for fk in fks:
        if fk['referred_table'] == 'portfolio' and 'portfolio_id' in fk['constrained_columns']:
            op.drop_constraint(fk['name'], 'transaction', type_='foreignkey')
    # Alter column to be nullable
    op.alter_column('transaction', 'portfolio_id', existing_type=sa.INTEGER(), nullable=True)
    # Create new FK with ON DELETE SET NULL
    op.create_foreign_key(
        'fk_transaction_portfolio_id',
        'transaction',
        'portfolio',
        ['portfolio_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade():
    # Revert: drop new FK, alter column to NOT NULL, recreate original FK without ON DELETE
    op.drop_constraint('fk_transaction_portfolio_id', 'transaction', type_='foreignkey')
    op.alter_column('transaction', 'portfolio_id', existing_type=sa.INTEGER(), nullable=False)
    op.create_foreign_key('fk_transaction_portfolio_id_old', 'transaction', 'portfolio', ['portfolio_id'], ['id'])
