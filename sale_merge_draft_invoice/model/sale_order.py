# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_draft_invoices(self, invoices_vals):
        if self.env.context.get("merge_draft_invoice", False):
            invoices = super(SaleOrder, self)._get_draft_invoices(invoices_vals)
            invoices = self.env["account.move"].search(
                [
                    ("state", "=", "draft"),
                    ("partner_id", "=", invoices_vals["partner_id"]),
                    ("currency_id", "=", invoices_vals["currency_id"]),
                    ("invoice_user_id", "=", invoices_vals["invoice_user_id"]),
                    ("company_id", "=", invoices_vals["company_id"]),
                    ("move_type", "=", invoices_vals["move_type"]),
                ],
                limit=1,
            )
            return invoices
        else:
            return super(SaleOrder, self)._get_draft_invoices(invoices_vals)
