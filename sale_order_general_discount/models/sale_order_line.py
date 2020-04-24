# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(
        compute="_compute_general_discount",
        store=True,
        readonly=False,
        string="Discount (%)",
        digits="Discount",
        default=0.0,
    )

    @api.depends("order_id")
    def _compute_general_discount(self):
        for line in self:
            line.discount = line.order_id.general_discount
