# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tools import sql


def pre_init_hook(env):
    """Create table columns for computed fields to not get them computed by Odoo."""
    if not sql.column_exists(env.cr, "sale_order_line", "price_compliance_tier"):
        sql.create_column(
            env.cr,
            "sale_order_line",
            "price_compliance_tier",
            "VARCHAR",
            comment="Price Compliance Tier",
        )
    if not sql.column_exists(env.cr, "sale_order_line", "price_compliance_data"):
        sql.create_column(
            env.cr,
            "sale_order_line",
            "price_compliance_data",
            "JSONB",
            comment="Price Compliance Data",
        )
