# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    general_discount = fields.Float(
        string="Discount (%)",
        compute="_compute_general_discount",
        store=True,
        readonly=False,
        digits="Discount",
    )

    @api.depends("partner_id")
    def _compute_general_discount(self):
        for so in self:
            so.general_discount = so.partner_id.sale_discount
