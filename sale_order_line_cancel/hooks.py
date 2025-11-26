# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tools.sql import column_exists


def pre_init_hook(cr):
    if not column_exists(cr, "sale_order_line", "product_qty_remains_to_deliver"):
        cr.execute(
            "ALTER TABLE sale_order_line ADD COLUMN product_qty_remains_to_deliver NUMERIC"
        )
        cr.execute(
            """
            UPDATE
                sale_order_line
            SET
                product_qty_remains_to_deliver = product_uom_qty - qty_delivered
        """
        )
