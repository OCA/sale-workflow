# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    transmit_method_id = fields.Many2one(
        comodel_name="transmit.method",
        string="Transmission Method",
        tracking=True,
        ondelete="restrict",
        compute="_compute_transmit_method_id",
        store=True,
        readonly=True,
    )

    @api.depends("partner_id", "company_id")
    def _compute_transmit_method_id(self):
        self.transmit_method_id = self.partner_id.customer_invoice_transmit_method_id

    def _prepare_invoice(self):
        values = super()._prepare_invoice()
        values["transmit_method_id"] = self.transmit_method_id.id
        return values
