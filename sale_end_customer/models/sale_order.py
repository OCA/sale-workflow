# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_end_customer_id = fields.Many2one(
        "res.partner",
        string="End Customer",
        tracking=True,
        check_company=True,
    )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals["partner_end_customer_id"] = self.partner_end_customer_id.id
        return invoice_vals
