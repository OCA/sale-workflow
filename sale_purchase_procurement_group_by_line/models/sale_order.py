# Copyright 2023 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Module ``sale_procurement_group_by_line`` moves the procurement group
    # from the sale order to the sale order lines; but ``sale_purchase_stock``
    # module only reads sale orders' procurement groups when retrieving
    # purchase orders linked to the sale orders.
    # We're overriding these 2 methods to add new dependencies to the computed
    # method, and update the way purchases are retrieved from sales.

    @api.depends(
        "order_line.procurement_group_id.stock_move_ids.created_purchase_line_id.order_id",  # noqa: B950
        "order_line.procurement_group_id.stock_move_ids.move_orig_ids.purchase_line_id.order_id",  # noqa: B950
    )
    def _compute_purchase_order_count(self):
        return super()._compute_purchase_order_count()

    def _get_purchase_orders(self):
        return (
            super()._get_purchase_orders()
            | self.order_line.procurement_group_id.stock_move_ids.created_purchase_line_id.order_id  # noqa: B950
            | self.order_line.procurement_group_id.stock_move_ids.move_orig_ids.purchase_line_id.order_id  # noqa: B950
        )
