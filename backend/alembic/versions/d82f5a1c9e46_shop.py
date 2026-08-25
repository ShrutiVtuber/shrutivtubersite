"""Products, the files they deliver, and the orders for them

Two kinds of thing in one table. A physical product needs an address and has a
finite number of it; a digital one needs delivering and does not. Everything
else about them is the same, and two tables would mean writing the shop, the
admin and the checkout twice to say it.

Product files are not media rows on purpose. Media is images, served straight
off a public path by Caddy, which is exactly what a paid file must not be.

Orders are written from the webhook rather than from the browser coming back:
a buyer who closes the tab has still bought the thing, and one who reloads the
thank-you page has not bought it twice.

Revision ID: d82f5a1c9e46
Revises: c71e2b8d94a3
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d82f5a1c9e46"
down_revision: Union[str, None] = "c71e2b8d94a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TS = sa.DateTime(timezone=True)


def _stamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", TS, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", TS, nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.create_table(
        "product_file",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("stored_name", sa.String(), nullable=False, unique=True),
        sa.Column("original_name", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False, server_default=""),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("storage_backend", sa.String(), nullable=False, server_default="local"),
        *_stamps(),
    )
    op.create_index("ix_product_file_stored_name", "product_file", ["stored_name"])

    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False, server_default="digital"),
        sa.Column("tagline", sa.String(), nullable=False, server_default=""),
        sa.Column("body_md", sa.String(), nullable=False, server_default=""),
        sa.Column("price_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(), nullable=False, server_default="eur"),
        sa.Column("media_id", sa.Integer(), sa.ForeignKey("media.id"), nullable=True),
        sa.Column("file_id", sa.Integer(), sa.ForeignKey("product_file.id"), nullable=True),
        sa.Column("stock", sa.Integer(), nullable=True),
        sa.Column("tax_code", sa.String(), nullable=False, server_default="txcd_10000000"),
        sa.Column("stripe_product_id", sa.String(), nullable=False, server_default=""),
        sa.Column("stripe_price_id", sa.String(), nullable=False, server_default=""),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        *_stamps(),
    )
    op.create_index("ix_product_slug", "product", ["slug"])
    op.create_index("ix_product_kind", "product", ["kind"])

    op.create_table(
        "product_order",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("checkout_session_id", sa.String(), nullable=False, unique=True),
        sa.Column("payment_intent_id", sa.String(), nullable=False, server_default=""),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("product.id"), nullable=True),
        sa.Column("product_name", sa.String(), nullable=False, server_default=""),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("amount_total_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(), nullable=False, server_default="eur"),
        sa.Column("fulfilment", sa.String(), nullable=False, server_default="none"),
        sa.Column("shipping_json", sa.String(), nullable=False, server_default=""),
        sa.Column("download_token", sa.String(), nullable=False, server_default=""),
        sa.Column("downloads", sa.Integer(), nullable=False, server_default="0"),
        *_stamps(),
    )
    op.create_index("ix_product_order_checkout_session_id", "product_order",
                    ["checkout_session_id"])
    op.create_index("ix_product_order_email", "product_order", ["email"])
    op.create_index("ix_product_order_fulfilment", "product_order", ["fulfilment"])
    op.create_index("ix_product_order_download_token", "product_order", ["download_token"])


def downgrade() -> None:
    op.drop_table("product_order")
    op.drop_table("product")
    op.drop_table("product_file")
