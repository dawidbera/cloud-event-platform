"""Initial order tables

Revision ID: 001
Revises: 
Create Date: 2026-09-17 21:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('orders',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('customer_id', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('total_amount', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_customer_id'), 'orders', ['customer_id'], unique=False)
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_table('order_items',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_id', sa.String(), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_order_items_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_customer_id'), table_name='orders')
    op.drop_table('orders')
