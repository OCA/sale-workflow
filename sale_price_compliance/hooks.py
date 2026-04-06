# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import logging

from odoo.tools import sql

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Create table columns for computed fields to not get them computed by Odoo."""
    if not sql.column_exists(cr, "sale_order_line", "price_compliance_tier"):
        sql.create_column(
            cr,
            "sale_order_line",
            "price_compliance_tier",
            "VARCHAR",
            comment="Price Compliance Tier",
        )
    if not sql.column_exists(cr, "sale_order_line", "price_compliance_data"):
        sql.create_column(
            cr,
            "sale_order_line",
            "price_compliance_data",
            "JSONB",
            comment="Price Compliance Data",
        )
