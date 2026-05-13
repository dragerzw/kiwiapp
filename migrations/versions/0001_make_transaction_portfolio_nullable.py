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
    # Alter column and recreate FK safely using batch_alter_table
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        # We try to drop the constraint, but if we don't know the name we rely on recreate behavior
        # Get constraint name if available
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        fks = inspector.get_foreign_keys('transaction')
        for fk in fks:
            if fk['referred_table'] == 'portfolio' and 'portfolio_id' in fk['constrained_columns']:
                if fk['name']:
                    batch_op.drop_constraint(fk['name'], type_='foreignkey')
                break
        
        batch_op.alter_column('portfolio_id', existing_type=sa.INTEGER(), nullable=True)
        batch_op.create_foreign_key(
            'fk_transaction_portfolio_id',
            'portfolio',
            ['portfolio_id'],
            ['id'],
            ondelete='SET NULL'
        )

def downgrade():
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_constraint('fk_transaction_portfolio_id', type_='foreignkey')
        batch_op.alter_column('portfolio_id', existing_type=sa.INTEGER(), nullable=False)
        batch_op.create_foreign_key('fk_transaction_portfolio_id_old', 'portfolio', ['portfolio_id'], ['id'])
