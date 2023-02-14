# Copyright 2017-18 ForgeFlow S.L.(http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self):
        return super(
            SaleOrderLine,
            self.filtered(lambda line: not line.order_id.delivery_block_id),
        )._action_launch_stock_rule()
