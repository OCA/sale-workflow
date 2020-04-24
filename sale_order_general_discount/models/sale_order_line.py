# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(compute="_compute_discount", store=True, readonly=False,)

    @api.depends("order_id", "order_id.general_discount")
    def _compute_discount(self):
        if hasattr(super(), "_compute_discount"):
            super()._compute_discount()
        for line in self:
            line.discount = line.order_id.general_discount
