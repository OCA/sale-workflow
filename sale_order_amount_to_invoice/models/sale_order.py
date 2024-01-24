# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    untaxed_amount_to_invoice = fields.Monetary(
        compute="_compute_untaxed_amount_to_invoice", store=True
    )

    @api.depends("order_line.untaxed_amount_to_invoice")
    def _compute_untaxed_amount_to_invoice(self):
        for rec in self:
            rec.untaxed_amount_to_invoice = sum(
                rec.order_line.mapped("untaxed_amount_to_invoice")
            )
