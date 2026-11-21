# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tools.sql import column_exists


def migrate(cr, version):
    """Keep the routes set by the elaborations before 19.0.1.1.0.

    Up to that version the module stored them in its own sale order line
    ``route_id`` field, which nothing read in 19.0. The field is gone now, so
    copy its value to the core ``route_ids`` of the lines without routes.
    """
    if not column_exists(cr, "sale_order_line", "route_id"):
        return
    cr.execute(
        """
        INSERT INTO sale_order_line_stock_route_rel
            (sale_order_line_id, stock_route_id)
        SELECT sol.id, sol.route_id
        FROM sale_order_line sol
        WHERE sol.route_id IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM sale_order_line_stock_route_rel rel
                WHERE rel.sale_order_line_id = sol.id
            )
        """
    )
