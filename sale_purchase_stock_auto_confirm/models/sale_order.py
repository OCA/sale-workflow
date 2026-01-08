# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        res = super()._action_confirm()
        for order in self:
            # Get the purchase orders using sudo,
            # as a sales user may not have access to the purchase order lines
            purchase_orders = order.sudo()._get_purchase_orders()
            for purchase in purchase_orders.filtered(
                lambda po: po.state == "draft"
                and po.company_id.purchase_auto_validation
            ):
                purchase.button_confirm()
        return res
