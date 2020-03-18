# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    transmit_method_id = fields.Many2one(
        comodel_name="transmit.method",
        string="Transmission Method",
        track_visibility="onchange",
        ondelete="restrict",
    )

    @api.onchange("partner_id", "company_id")
    def onchange_partner_transmit_method(self):
        self.transmit_method_id = (
            self.partner_id.customer_invoice_transmit_method_id.id or False
        )

    @api.multi
    def _finalize_invoices(self, invoices, references):
        res = super()._finalize_invoices(invoices, references)
        for invoice in invoices.values():
            transmit_methods = invoice.invoice_line_ids.mapped(
                'sale_line_ids.order_id.transmit_method_id'
            )
            if len(transmit_methods) == 1:
                invoice.transmit_method_id = transmit_methods
        return res
