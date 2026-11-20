# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    incoterm_address_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_incoterm_address_id",
        precompute=True,
        store=True,
        readonly=False,
    )

    @api.depends("partner_id")
    def _compute_incoterm_address_id(self):
        for order in self:
            order.incoterm_address_id = order.partner_id.sale_incoterm_address_id
