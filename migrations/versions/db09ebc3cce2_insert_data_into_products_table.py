"""Insert data into products table

Revision ID: db09ebc3cce2
Revises: 289ef43a0672
Create Date: 2026-11-19 10:07:05.528172

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = 'db09ebc3cce2'
down_revision = '289ef43a0672'
branch_labels = None
depends_on = None


def upgrade():
    categories_table = table(
        "categories",
        column("id", sa.Integer),
        column("name", sa.String),
    )
    products_table = table(
        "products",
        column("name", sa.String),
        column("price", sa.Float),
        column("active", sa.Boolean),
        column("category_id", sa.Integer),
    )

    op.bulk_insert(categories_table, [
        {"name": "Electronics"},
        {"name": "Books"},
        {"name": "Clothing"},
    ])

    conn = op.get_bind()
    rows = conn.execute(sa.select(categories_table.c.id, categories_table.c.name))
    ids = {row.name: row.id for row in rows}

    op.bulk_insert(products_table, [
        {"name": "Laptop", "price": 1200.0, "active": True, "category_id": ids["Electronics"]},
        {"name": "Smartphone", "price": 800.0, "active": True, "category_id": ids["Electronics"]},
        {"name": "Novel", "price": 20.0, "active": True, "category_id": ids["Books"]},
        {"name": "T-Shirt", "price": 25.0, "active": False, "category_id": ids["Clothing"]},
    ])


def downgrade():
    op.execute("DELETE FROM products WHERE name IN ('Laptop', 'Smartphone', 'Novel', 'T-Shirt')")
    op.execute("DELETE FROM categories WHERE name IN ('Electronics', 'Books', 'Clothing')")
    