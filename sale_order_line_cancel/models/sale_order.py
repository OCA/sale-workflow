# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def action_draft(self):
        res = super().action_draft()
        orders = self.filtered(lambda s: s.state == "draft")
        orders.order_line.write({"product_qty_canceled": 0})
        return res

    def _action_cancel(self):
        res = super()._action_cancel()
        self.order_line._update_qty_canceled()
        return res
