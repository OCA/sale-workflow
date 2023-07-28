# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        return super(
            SaleOrderLine,
            self.filtered(lambda line: not line.order_id.delivery_block_id),
        )._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
