# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = ["sale.order", "sale.contact.mixin"]
    _name = "sale.order"

    def _prepare_invoice(self):
        """Propagate sale contact to invoice."""
        invoice_vals = super()._prepare_invoice()
        if self.sale_contact_partner_id:
            invoice_vals["sale_contact_partner_id"] = self.sale_contact_partner_id.id
        return invoice_vals
