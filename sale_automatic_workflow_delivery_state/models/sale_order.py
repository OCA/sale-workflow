# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("delivery_state")
    def _compute_all_qty_delivered(self):
        for order in self:
            order.all_qty_delivered = order.delivery_state == "done"
