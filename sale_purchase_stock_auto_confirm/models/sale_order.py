# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        res = super()._action_confirm()

        purchase_orders = self.sudo()._get_purchase_orders()
        to_be_confirmed = purchase_orders.filtered(
            lambda po: po.state == "draft" and po.company_id.purchase_auto_validation
        )
        to_be_confirmed.button_confirm()

        return res
