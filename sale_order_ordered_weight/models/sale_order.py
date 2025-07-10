# Copyright 2021 Manuel Calero Solís (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_ordered_weight = fields.Float(
        compute="_compute_total_ordered_weight",
        string="Ordered Weight",
        store=True,
    )

    @api.depends("order_line.total_ordered_weight")
    def _compute_total_ordered_weight(self):
        for order in self:
            order.total_ordered_weight = sum(
                order.mapped("order_line.total_ordered_weight")
            )
