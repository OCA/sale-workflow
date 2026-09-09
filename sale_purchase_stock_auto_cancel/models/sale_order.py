# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_cancel(self):
        res = super()._action_cancel()

        # Get the purchase orders using sudo,
        # as a sales user may not have access to the purchase order lines
        purchase_orders = self.sudo()._get_purchase_orders()
        purchase_orders.filtered(
            lambda po: po.company_id.purchase_auto_cancel
        ).button_cancel()

        return res
