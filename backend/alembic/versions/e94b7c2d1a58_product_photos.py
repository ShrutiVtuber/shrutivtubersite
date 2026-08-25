"""A product gets as many photographs as it needs

One column held one picture, which is right for a print and wrong for a jumper
that wants a front, a back and a detail. "How many" is not a question with an
answer, so it becomes rows.

`product.media_id` stays and keeps meaning the first photograph — nothing that
already reads it has to change, and a product with one picture works exactly as
it did.

Revision ID: e94b7c2d1a58
Revises: d82f5a1c9e46
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e94b7c2d1a58"
down_revision: Union[str, None] = "d82f5a1c9e46"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_photo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("product.id"), nullable=False),
        sa.Column("media_id", sa.Integer(), sa.ForeignKey("media.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_product_photo_product_id", "product_photo", ["product_id"])
    op.create_index("ix_product_photo_media_id", "product_photo", ["media_id"])

    # Anything that already had a picture keeps it, as its first one.
    op.execute(
        "INSERT INTO product_photo (product_id, media_id, position, created_at, updated_at) "
        "SELECT id, media_id, 0, now(), now() FROM product WHERE media_id IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_table("product_photo")
