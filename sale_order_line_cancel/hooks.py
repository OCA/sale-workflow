# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tools.sql import column_exists


def pre_init_hook(env):
    if not column_exists(env.cr, "sale_order_line", "product_qty_remains_to_deliver"):
        env.cr.execute(
            "ALTER TABLE sale_order_line "
            "ADD COLUMN product_qty_remains_to_deliver NUMERIC"
        )
        env.cr.execute(
            """
            UPDATE
                sale_order_line
            SET
                product_qty_remains_to_deliver = product_uom_qty - qty_delivered
        """
        )
