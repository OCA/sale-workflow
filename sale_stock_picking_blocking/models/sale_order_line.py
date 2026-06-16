# Copyright 2024 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _action_launch_stock_rule(self, **kwargs):
        allowed = self.filtered(lambda line: not line.order_id.delivery_block_id)
        return super(SaleOrderLine, allowed)._action_launch_stock_rule(**kwargs)
