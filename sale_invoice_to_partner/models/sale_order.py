# Copyright 2026 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_id")
    def _compute_partner_invoice_id(self):
        """Use the customer's ``Invoice To`` partner as the invoice address.

        When the order's customer (or its commercial partner) defines an
        ``Invoice To`` partner, that partner is used as ``partner_invoice_id``
        so the invoices generated from the order are owed by it. Orders whose
        customer has no override keep the standard behaviour.
        """
        orders_with_invoice_to = self.browse()
        for order in self:
            invoice_to = (
                order.partner_id._get_invoice_to_partner()
                if order.partner_id
                else False
            )
            if invoice_to:
                order.partner_invoice_id = invoice_to
                orders_with_invoice_to |= order
        return super(
            SaleOrder, self - orders_with_invoice_to
        )._compute_partner_invoice_id()
