# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_frequency_id = fields.Many2one(
        comodel_name="sale.invoice.frequency",
        string="Invoicing frequency",
        compute="_compute_invoice_frequency",
        store=True,
        readonly=False,
        help="Invoicing frequency for this order",
    )

    @api.depends("partner_id")
    def _compute_invoice_frequency(self):
        for record in self:
            record.invoice_frequency_id = record.partner_id.invoice_frequency_id
