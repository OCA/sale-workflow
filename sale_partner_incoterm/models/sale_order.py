# Copyright 2015 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    incoterm = fields.Many2one(
        compute="_compute_incoterm",
        store=True,
        readonly=False,
        precompute=True,
        copy=True,
    )
    incoterm_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Incoterm Address",
        compute="_compute_incoterm",
        store=True,
        readonly=False,
        precompute=True,
        copy=True,
    )

    @api.depends("partner_id")
    def _compute_incoterm(self):
        for order in self:
            order.incoterm = order.partner_id.sale_incoterm_id
            order.incoterm_address_id = order.partner_id.sale_incoterm_address_id
