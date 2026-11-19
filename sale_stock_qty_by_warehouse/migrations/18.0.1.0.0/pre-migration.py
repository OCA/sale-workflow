# Copyright 2026 Akretion (https://www.akretion.com).
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

OLD_STOCK_FIELD_KEY = "sale_order_line_stock_info.stock_field_on_sol"
NEW_STOCK_FIELD_KEY = "sale_stock_qty_by_warehouse.stock_field_on_sol"


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_config_parameter
        SET key = %s
        WHERE key = %s
            AND NOT EXISTS (SELECT 1 FROM ir_config_parameter WHERE key = %s)
        """,
        (NEW_STOCK_FIELD_KEY, OLD_STOCK_FIELD_KEY, NEW_STOCK_FIELD_KEY),
    )
