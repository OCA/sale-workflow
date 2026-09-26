# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import AccessError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        companies = self.sale_order_ids.company_id
        if (
            not self.env.su
            and any(companies.mapped("restrict_so_invoicing"))
            and not self.env.user.has_group("sale_invoice_group.group_sale_invoice")
        ):
            raise AccessError(
                _("You are not allowed to create invoices from sales orders.")
            )
        return super().create_invoices()
