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
    )

    @api.onchange("partner_id", "company_id")
    def onchange_partner_transmit_method(self):
        self.transmit_method_id = (
            self.partner_id.customer_invoice_transmit_method_id.id or False
        )

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super()._create_invoices(grouped, final, date)
        for move in moves:
            transmit_methods = move.invoice_line_ids.mapped(
                "sale_line_ids.order_id.transmit_method_id"
            )
            if len(transmit_methods) == 1:
                move.transmit_method_id = transmit_methods
        return moves
